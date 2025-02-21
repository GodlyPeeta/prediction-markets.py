from __future__ import annotations

import pytest
import os
import sys

here = os.path.dirname(__file__)

sys.path.append(os.path.join(here, '..'))

from prediction_markets import *

def main():
    kc = KalshiClient()

    d = kc.kalshi_get_markets(10)

    print(d)

main()