from __future__ import annotations

from hypothesis import given, settings
from hypothesis.strategies import integers 

from prediction_markets import *

@given(integers(min_value=1, max_value=50))
@settings(deadline=1000, max_examples=10)
def test_client_market_read_and_load(num_markets):
    kc = KalshiClient()
    
    markets = kc.get_markets(limit=num_markets)[0]
    assert len(markets) == num_markets

    KalshiMarket.refresh_markets(markets)

    for m in markets:
        assert m.last_refreshed_data is not None