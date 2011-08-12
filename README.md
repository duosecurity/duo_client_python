# Overview

**duo_verify** - Demonstration client to call Duo Verify API methods
with Python.

# Install

To set up, edit duo.conf to include your integration key, secret key,
and API hostname. To use the demo, you can also define an IP address
to look up, and your phone number to receive a PIN over voice or SMS.

# Usage

Run one of the executable Python scripts and observe the output:

* `call.py`: Send a PIN with a voice call
* `sms.py`: Send a PIN with an SMS message
* `lookup.py`: Look up a phone number and an IP address

# For more information

See the Duo Verify API guide:

<http://www.duosecurity.com/docs/duoverify>
