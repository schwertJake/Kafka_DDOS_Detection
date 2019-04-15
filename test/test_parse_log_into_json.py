import unittest
import parse_log_into_json.app as app


class TestApacheLogIngest(unittest.TestCase):

    def test_normal_parse(self):
        test_line = "200.4.91.190 - - [25/May/2015:23:11:15 +0000] \"GET / HTTP/1.0\" 200 3557 \"-\" \"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)\""
        parsed = app.parse_apache_log_line(test_line)
        self.assertEqual(parsed,
                         {
                             "IP": "200.4.91.190",
                             "Time": 1432595475,
                             "Request_Method": 'GET',
                             "Request_Resource": '/',
                             "Request_Protocol": 'HTTP/1.0',
                             "Status_Code": 200,
                             "Payload_Size": 3557,
                             "Referer": '-',
                             "User_Agent": 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'
                         })

    def test_imporper_string(self):
        test_line = "200.4.91.190 [25/May/2015:23:11:15 +0000] \"GET / HTTP/1.0\" 200 3557 \"-\""
        self.assertEqual({},
                          app.parse_apache_log_line(test_line))

    def test_non_string(self):
        test_line = 12345
        self.assertEqual({},
                         app.parse_apache_log_line(test_line))

    def test_epoch_converter(self):
        test_ts = "25/May/2015:23:11:15"
        test_tz = '+0000'
        self.assertEqual(app.get_time_epoch(test_ts, test_tz),
                         1432595475)

    def test_epoch_converter_incorrect_format(self):
        test_ts = "May/25/2015:23:11:15"
        test_tz = '+0000'
        self.assertRaises(TypeError,
                          app.get_time_epoch(test_ts, test_tz))