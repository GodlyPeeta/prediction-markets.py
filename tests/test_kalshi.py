from __future__ import annotations

import unittest
from hypothesis import given, settings
from hypothesis.strategies import integers 

from prediction_markets import *

class TestKalshi(unittest.TestCase):

    # @given(integers(min_value=1, max_value=1000))
    # @settings(deadline=1000, max_examples=1)
    def test_client_market_read_and_load(self):
        num_markets = 20
        kc = KalshiClient()
        
        markets = kc.get_markets(limit=num_markets)[0]
        self.assertEqual(len(markets), num_markets)

        KalshiMarket.refresh_markets(markets)

        for m in markets:
            self.assertIsNotNone(m.last_refreshed_data)