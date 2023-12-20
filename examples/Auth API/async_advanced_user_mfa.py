"""
Example of Duo Auth API with asynchronous user authentication action

This example uses the threading and queue libraries to illustrate how multiple users could potentially have
authentication requests in flight at the same time while the application polls for responses on each authentication
event without blocking main program execution.
"""
import getpass
import logging
import queue
import signal
import os
import sys
import time
import threading
from pathlib import Path
import traceback
from logging.handlers import RotatingFileHandler
from datetime import datetime

from duo_client import Auth

FIVE_MINUTES = 5 * 60
WORKER_THREADS = 3
SHUTDOWN_TIMEOUT = 10
WORKER_SLEEP_INTERVAL = 0.5


def _write_auth_entry(auth_entry: dict) -> None:
    """Write authentication result entry to separate log file"""
    filename = Path(__file__).with_name("user_authentication_result.log")
    human_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, 'a', encoding='utf-8') as auth_fn:
        auth_fn.write(f"{human_time} - {auth_entry}\n")


class DuoAuthAPI:
    """
    Class to hold global variables and methods used by the Duo Auth
    """

    def __init__(self):
        """Setup Duo Auth API object"""
        self.RUNNING = True
        self.DEBUG = True
        self.lock = threading.Lock()
        signal.signal(signal.SIGINT, self.close)
        self.logger = self._init_logger()
        self.logger.info(f"========== Starting {Path(__file__).name} ==========")
        self.stderr_tmp = sys.stderr
        sys.stderr = open(os.devnull, 'w')

        credentials = self.prompt_for_credentials()

        self._auth_client = Auth(
                ikey=credentials['IKEY'],
                skey=credentials['SKEY'],
                host=credentials['APIHOST']
        )
        if not self.ping_duo():
            self.exit_with_error("Duo Ping failed.")
        if not self.verify_duo():
            self.exit_with_error("Unable to verify Duo Auth API credentials.")

        self.authentications = {}
        """
        self.authentications[txid] = {
                  "timestamp": int,
                  "username": str,
                  "success": bool,
                  "status": str,
                  "message": str
        """

        self.user_queue = queue.Queue()
        self.auth_queue = queue.Queue()
        self.result_queue = queue.Queue()

        self.initialize_threads()

    @staticmethod
    def _init_logger():
        logger = logging.getLogger(__name__)
        f = Path(__file__)
        log_handler = RotatingFileHandler(
                filename=f.with_name(f.stem + ".log"),
                maxBytes=25000000,
                backupCount=5
        )
        LOGGING_FORMAT = "{asctime} [{levelname}]\t{module} : {funcName}({lineno}) - {message}"
        log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT, style='{'))
        logger.addHandler(log_handler)
        logger.setLevel(logging.DEBUG)
        logger.info(f"Logger created with file {f.with_name(f.stem + '.log')} at log level " +
                    f"{logging.getLevelName(logger.getEffectiveLevel())}")
        return logger

    @staticmethod
    def _get_user_input(prompt, secure=False):
        """Read information from STDIN, using getpass when sensitive information should not be echoed to tty"""
        if secure is True:
            return getpass.getpass(prompt)
        else:
            return input(prompt)

    def close(self, signal_number, frame):
        """
        Handle CRTL-C interrupt signal and exit program
        """
        if self.DEBUG is True:
            self.logger.debug(f"Signal number {signal_number} received.")
            self.logger.debug(f"Frame traceback: {traceback.print_stack(frame)}")
        self.logger.info(f"SIGINIT received. Waiting for threads to complete...")
        print(f"\n\nSIGINIT received. Waiting for threads to complete...\n")
        self.logger.info("Setting instance RUNNING property to False...")
        self.RUNNING = False
        for thread in threading.enumerate():
            if thread != threading.main_thread():
                self.logger.info(f"Waiting for {thread.name} thread to complete...")
                print(f"{thread.name} shutting down...")
                thread.join(timeout=SHUTDOWN_TIMEOUT)
                if thread.is_alive() is True:
                    self.logger.info(f"{thread.name} did not shut down gracefully.")
                    print(f"    {thread.name} did not shut down gracefully.")
        self.logger.info(f"All threads complete. Shutting down.")
        sys.stderr = self.stderr_tmp
        print(f"All threads complete. Shutting down.")
        sys.exit()

    def exit_with_error(self, reason: str) -> None:
        """Log error message and exit program"""
        self.logger.error(f"Exiting with error: {reason}")
        sys.exit()

    def ping_duo(self) -> bool:
        """Verify that the Duo service is available"""
        duo_ping = self._auth_client.ping()
        if 'time' in duo_ping:
            self.logger.info("Duo service check completed successfully.")
            return True
        else:
            self.logger.error(f"Error: {duo_ping}")
            return False

    def verify_duo(self) -> bool:
        """Verify that IKEY and SKEY information provided are valid"""
        duo_check = self._auth_client.check()
        if 'time' in duo_check:
            self.logger.info("IKEY and SKEY provided have been verified.")
            return True
        else:
            self.logger.error(f"Error: {duo_check}")
            return False

    def _cleanup_authentications_dictionary(self):
        """Background task to remove old data from authentications dictionary"""
        t_name = threading.current_thread().name
        self.logger.info(f"#### Starting thread {t_name} ####")
        while self.RUNNING is True:
            threshold_time = int(time.time()) - FIVE_MINUTES
            self.logger.info(f"[{t_name}] Scanning for authentication data for older than {threshold_time}")
            self.lock.acquire(blocking=True)
            try:
                for txid in list(self.authentications.keys()):
                    if self.authentications[txid]['timestamp'] < threshold_time:
                        self.logger.warning(f"[{t_name}] *** Removing {txid} from authentications dictionary ***")
                        del self.authentications[txid]
            finally:
                self.lock.release()
            time.sleep(30)
        self.logger.info(f"[{t_name}] RUNNING property set to False. Cleaning up...")

    def prompt_for_credentials(self) -> dict:
        """Collect required API credentials from command line prompts and return them in a dictionary format"""
        ikey = self._get_user_input('Duo Auth API integration key ("DI..."): ')
        skey = self._get_user_input('Duo Auth API integration secret key: ', secure=True)
        host = self._get_user_input('Duo Auth API hostname ("api-....duosecurity.com"): ')
        return {"IKEY": ikey, "SKEY": skey, "APIHOST": host}

    def prompt_for_username(self) -> None:
        """Collect username from TTY and place on preauth_queue."""
        self.logger.debug(f"Prompting for username...") if self.DEBUG is True else ...
        username = self._get_user_input("Duo username to authenticate: ")
        self.logger.debug(f"    Username: {username} received") if self.DEBUG is True else ...
        self.user_queue.put_nowait(username)
        self.logger.info(f"    {username} placed in user_queue.")

    def preauth_user_from_queue(self) -> None:
        """Preauth user from pre-auth queue"""
        t_name = threading.current_thread().name
        self.logger.info(f"#### Starting thread {t_name} ####")
        duo_user = None
        got_item = False
        while self.RUNNING is True and got_item is False:
            try:
                duo_user = self.user_queue.get(block=False)
                got_item = True
            except queue.Empty:
                time.sleep(WORKER_SLEEP_INTERVAL)
            if got_item is False:
                continue
            self.logger.info(f"[{t_name}] Executing pre-authentication for {duo_user}...")
            pre_auth = self._auth_client.preauth(duo_user)
            self.logger.info(f"[{t_name}] Pre-authentication result for {duo_user} is {pre_auth}")
            if pre_auth['result'] == 'auth':
                self.auth_queue.put_nowait((duo_user, pre_auth))
                self.user_queue.task_done()
            else:
                self.logger.error(f"[{t_name}] Pre-auth for {duo_user} failed. Reason: {pre_auth}")
        self.logger.info(f"[{t_name}] RUNNING property set to False. Cleaning up...")

    def auth_user_from_queue(self) -> None:
        """Authenticate user from pre-auth queue"""
        t_name = threading.current_thread().name
        self.logger.info(f"#### Starting thread {t_name} ####")
        duo_user = None
        got_item = False
        while self.RUNNING is True and got_item is False:
            try:
                (duo_user, pre_auth_result) = self.auth_queue.get(block=False)
                got_item = True
            except queue.Empty:
                time.sleep(WORKER_SLEEP_INTERVAL)
            if got_item is False:
                continue
            try:
                self.logger.info(f"[{t_name}] Executing asynchronous authentication action for {duo_user}...")
                auth = self._auth_client.auth(factor="push", username=duo_user, device="auto", async_txn=True)
                if 'txid' in auth:
                    self.logger.info(f"[{t_name}] Placing {auth['txid']} in result_queue for user {duo_user}")
                    self.result_queue.put_nowait((duo_user, auth['txid']))
                    self.auth_queue.task_done()
            except Exception as e_str:
                self.logger.exception(f"[{t_name}] Exception caught: {e_str}")
        self.logger.info(f"[{t_name}] RUNNING property set to False. Cleaning up...")

    def get_user_auth_result(self) -> None:
        """Gets user authentication result from result_queue"""
        t_name = threading.current_thread().name
        self.logger.info(f"#### Starting thread {t_name} ####")
        duo_user = None
        txid = None
        got_item = False
        while self.RUNNING is True and got_item is False:
            try:
                (duo_user, txid) = self.result_queue.get(block=False)
                got_item = True
            except queue.Empty:
                time.sleep(WORKER_SLEEP_INTERVAL)
            if got_item is False:
                continue
            self.logger.info(f"[{t_name}] Getting authentication result for TXID {txid}, username {duo_user}...")
            waiting = True
            while waiting is True:
                self.logger.info(f"[{t_name}] Waiting for {duo_user} to respond [{txid}]...")
                auth_status = self._auth_client.auth_status(txid)
                if auth_status['waiting'] is not True:
                    waiting = False
                    self.logger.info(f"[{t_name}] Authentication result for {duo_user} [{txid}] is {auth_status}")
                    # Record authentication result for potential use elsewhere in the program
                    self.lock.acquire()
                    try:
                        self.authentications[txid] = {
                                "timestamp": int(time.time()),
                                "message":   auth_status['status_msg'],
                                "status":    auth_status['status'],
                                "success":   auth_status['success'],
                                "username":  duo_user
                        }
                    finally:
                        self.lock.release()
                    _write_auth_entry(self.authentications[txid])
                else:
                    self.logger.info(f"[{t_name}] Still waiting for {duo_user} to respond [{auth_status}]")
            self.result_queue.task_done()
        self.logger.info(f"[{t_name}] RUNNING property set to False. Cleaning up...")

    def initialize_threads(self):
        """Start background worker threads to monitor queues and process items"""
        threading.Thread(target=self._cleanup_authentications_dictionary,
                         name="Auth-dict-cleanup",
                         daemon=True).start()
        for i in range(WORKER_THREADS):
            threading.Thread(target=self.preauth_user_from_queue,
                             name=f"Pre-auth-worker-{i}",
                             daemon=True).start()
            threading.Thread(target=self.auth_user_from_queue,
                             name=f"Auth-worker-{i}",
                             daemon=True).start()
            threading.Thread(target=self.get_user_auth_result,
                             name=f"Result-worker-{i}",
                             daemon=True).start()

    def run(self):
        """Run the program setup and loop"""
        while self.RUNNING is True:
            self.prompt_for_username()
            time.sleep(1)
        self.logger.info(f"[run()] RUNNING property set to False. Cleaning up...")
        sys.stderr = self.stderr_tmp


if __name__ == '__main__':
    duo_auth_api = DuoAuthAPI()
    duo_auth_api.run()

