from __future__ import annotations

from .market import *
from .client import *
import requests
from datetime import datetime
from enum import Enum
import json
from .enums import *
from typing import List

root="https://api.elections.kalshi.com/trade-api/v2"
demoRoot="https://demo-api.kalshi.co/trade-api/v2"

class Environment(Enum):
    DEMO = "demo",
    PROD = "prod"

def get_api_root(env: Environment) -> str:
    """ Gets the API root
    """
    if env == Environment.DEMO:
        return demoRoot
    else:
        return root

class KalshiMarket(Market):
    """ A market on Kalshi
    """
    title: str # The listed title of the market
    rules: str # The listed rules to the market. Used to identify differences between seemingly similar markets
    open: bool # Whether this market is open to orders
    open_time: datetime # the time this market opened
    close_time: datetime #the time this market closes, used to calculate returns
    book: OrderBook # The orderbook of this market. Not automatically refreshed

    last_refreshed_data: datetime # the last time the data has been refreshed
    last_refreshed_book: datetime

    ticker: str # the ticker used as id on kalshi
    environment: Environment # demo or prod

    # this function exists to save latency on updating a lot of markets at once
    def refresh_markets(markets: List[KalshiMarket]) -> None:
        """ Refreshes all the markets in <markets> at once with minimal API calls.
        """
        
        marketIdsProd = {}
        marketIdsDemo = {}

        for m in markets:
            if m.environment == Environment.PROD:
                marketIdsProd[m.ticker] = m
            else:
                marketIdsDemo[m.ticker] = m

        for marketIds in [marketIdsDemo, marketIdsProd]:
            if len(marketIds) == 0:
                continue

            s = ",".join(marketIds)
            env = Environment.DEMO if marketIds is marketIdsDemo else Environment.PROD
            params = {"tickers": s}

            # check for URL too long 414 error
            if len(s) > 2000 - len(get_api_root(env)) - 9:
                raise KalshiURLTooLong("URL too long, try splitting this call into smaller calls")
            
            data = requests.get(f"{get_api_root(env)}/markets", params=params)

            _check_api_response(data)
            
            responseMarkets = data.json()['markets']

            # check if any instances of keyerror were logged, but still process the rest of them
            gotKeyError = False
            erroneousTickers = []

            for m in responseMarkets:
                ticker = m['ticker']

                try:
                    marketIds[ticker]._load_data(m)
                except KeyError:
                    gotKeyError = True
                    erroneousTickers.append(ticker)

            if gotKeyError:
                raise KeyError(erroneousTickers)

    def __init__(self, ticker, demo=Environment.PROD):
        super().__init__()
        self.ticker = ticker
        self.environment = demo

    def _get_api_root(self) -> str:
        """ Gets the api root URL for endpoints
        """
        return get_api_root(self.environment)
    
    def _load_data(self, dataJSON: dict) -> None:
        """ Interprets data given from the Kalshi API and refreshes this object.

        Note that this DOES update last_refreshed_data. 
        """
        self.title = dataJSON['title']
        self.rules = dataJSON['rules_primary']
        self.open = True if dataJSON['status']=="active" else False
        self.open_time = datetime.fromisoformat(dataJSON['open_time'][0:-1])
        self.close_time = datetime.fromisoformat(dataJSON['close_time'][0:-1])

        self.last_refreshed_data = datetime.now()

    def refresh_data(self) -> None:
        apiRoot = self._get_api_root()
        data = requests.get(f"{apiRoot}/markets/{self.ticker}")

        _check_api_response(data)
        
        dataJSON = data.json()['market']
        self._load_data(dataJSON)

    def refresh_book(self) -> None:
        apiRoot = self._get_api_root()
        data = requests.get(f"{apiRoot}/markets/{self.ticker}/orderbook")

        _check_api_response(data)
        
        dataJSON = data.json()['orderbook']
        self.book.update_book(dataJSON['yes'], dataJSON['no'])


# TODO: test
# example code from kalshi demo: https://github.com/Kalshi/kalshi-starter-code-python/blob/main/clients.py
#                                https://github.com/Kalshi/kalshi-starter-code-python/blob/main/main.py
#                                https://trading-api.readme.io/reference/api-keys
class KalshiClient(Client):
    """ A single client on Kalshi. Uses HTTP connections
    """
    key_id: str
    private_key: str
    logged_in: bool

    environment: Environment
    
    def __init__(self, key_id: str=None, private_key: str=None, environment: Environment=Environment.PROD):
        self.key_id = key_id if key_id is not None else None
        self.private_key = private_key if private_key is not None else None
        self.environment = environment

        if key_id is None or private_key is None:
            self.logged_in = False
        else:
            self.logged_in = True

    def get_markets(self, limit: int=None, cursor:str=None, status:str=None) -> list[list[KalshiMarket], str]:
        """ Gets <limit> markets from the <cursor> that have the given <status>. 
        Returns a list that contains a list of markets and the next cursor, respectively.
        
        Note that the cursor is a page identifier. 

        Note that the markets are instantiated but does NOT call update data. 
        """
        apiRoot = get_api_root(self.environment)

        if limit is None:
            limit = ""

        if cursor is None:
            cursor = ""

        if status is None:
            status = ""

        params = {"limit": limit, "cursor": cursor, "status": status}
        d = requests.get(f"{apiRoot}/markets", params=params)

        _check_api_response(d)

        markets = d.json()["markets"]
        ret = [[]]
    
        for m in markets:
            market = KalshiMarket(m['ticker'], self.environment)
            market._load_data(m) # load in the data the same way that refresh_data would

            ret[0].append(market)

        ret.append(d.json()['cursor'])

        return ret


class KalshiOrder(Order):
    """ An order on Kalshi
    """
    client: Client
    market: Market
    placed_price: float # price per share when the order was placed
    quantity: float
    side: Side
    
    def __init__(self, client, market, placed_price, quantity, side):
        super().__init__(client, market, placed_price, quantity, side)


def _check_api_response(response: requests.Response) -> None:
    if response.status_code == 200:
        return
    
    try:
        js = response.json()
        error_msg = f'{json.dumps(js["error"])}'
    except:
        error_msg = f"Unkown error"
    
    raise KalshiRequestError(f"Recieved status code {response.status_code}: {error_msg}")

class KalshiURLTooLong(Exception):
    pass

class KalshiRequestError(Exception):
    pass