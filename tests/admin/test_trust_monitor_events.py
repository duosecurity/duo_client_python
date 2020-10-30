from .. import util
import duo_client.admin
from .base import TestAdmin


MINTIME = 1603399970000
MAXTIME = 1603399973797
LIMIT = 10
NEXT_OFFSET = "99999"
EVENT_TYPE = "auth"


class TestTrustMonitorEvents(TestAdmin):

    def test_get_trust_monitor_events_iterator(self):
        """
        Test to ensure that the correct parameters are supplied when calling
        next on the generator.
        """

        generator = self.client_dtm.get_trust_monitor_events_iterator(
            MINTIME,
            MAXTIME,
            event_type=EVENT_TYPE,
        )
        events = [e for e in generator]
        self.assertEqual(events, [{"foo": "bar"},{"bar": "foo"}])

    def test_get_trust_monitor_events_by_offset(self):
        """
        Test to ensure that the correct parameters are supplied.
        """

        res = self.client_list.get_trust_monitor_events_by_offset(
            MINTIME,
            MAXTIME,
            limit=LIMIT,
            offset=NEXT_OFFSET,
            event_type=EVENT_TYPE,
        )[0]
        uri, qry_str = res["uri"].split("?")
        args = util.params_to_dict(qry_str)

        self.assertEqual(res["method"], "GET")
        self.assertEqual(uri, "/admin/v1/trust_monitor/events")
        self.assertEqual(args["mintime"], ["1603399970000"])
        self.assertEqual(args["maxtime"], ["1603399973797"])
        self.assertEqual(args["offset"], ["99999"])
        self.assertEqual(args["limit"], ["10"])
        self.assertEqual(args["type"], ["auth"])
