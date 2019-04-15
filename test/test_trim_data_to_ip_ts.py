import unittest
import trim_data_to_ip_ts.app as app

class TestTrimData(unittest.TestCase):

    def test_trim_to_ip_ts_normal(self):
        test_dict = {
            "IP": "200.4.91.190",
            "Time": 1432595475,
            "Request_Method": 'GET',
            "Request_Resource": '/',
            "Request_Protocol": 'HTTP/1.0',
            "Status_Code": 200,
            "Payload_Size": 3557,
            "Referer": '-',
            "User_Agent": 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'
        }
        exp_result = {
            "IP": "200.4.91.190",
            "TS": 1432595475
        }
        self.assertEqual(app.trim_to_ip_ts(test_dict), exp_result)

    def test_trim_to_ip_ts_keys_dont_exist(self):
        test_dict = {
            "Request_Method": 'GET',
            "Request_Resource": '/',
            "Request_Protocol": 'HTTP/1.0',
            "Status_Code": 200,
            "Payload_Size": 3557,
            "Referer": '-',
            "User_Agent": 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'
        }
        self.assertEqual({}, app.trim_to_ip_ts(test_dict))
