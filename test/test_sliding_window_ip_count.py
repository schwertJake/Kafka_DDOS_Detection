import unittest
import time
import sliding_window_ip_count.app as app

class TestSlidingWindow(unittest.TestCase):

    def test_put_sliding_window_initial(self):
        sample_ip_ts = {
            "IP": '127.0.0.1',
            "TS": int(time.time())
        }
        app.put_sliding_window(sample_ip_ts)
        self.assertEqual(app.sliding_window,
                         {
                             '127.0.0.1': {
                                 "ts": [sample_ip_ts["TS"]],
                                 "count": 1
                             }
                         })

    def test_put_sliding_window_multiple(self):
        app.THROTTLE_LIMIT = 5
        app.WINDOW_SIZE = 1
        sample_ip_ts = {
            "IP": '127.0.0.1',
            "TS": 1555343427
        }
        sample_ip_ts_2 = {
            "IP": '127.0.0.1',
            "TS": 1555343428
        }
        app.put_sliding_window(sample_ip_ts)
        app.put_sliding_window(sample_ip_ts_2)
        self.assertEqual(app.sliding_window,
                         {
                             '127.0.0.1': {
                                 "ts": [1555343427, 1555343428],
                                 "count": 2
                             }
                         })