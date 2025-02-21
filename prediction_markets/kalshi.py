from .market import *
from .client import *
import requests
from datetime import datetime
from enum import Enum
import json
from .enums import *

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

        if data.status_code != 200:
            raise KalshiRequestError(f"Recieved status code {data.status_code} instead of 200. Ticker: {self.ticker}")
        
        dataJSON = data.json()['market']
        self._load_data(dataJSON)

    def refresh_book(self) -> None:
        apiRoot = self._get_api_root()
        data = requests.get(f"{apiRoot}/markets/{self.ticker}/orderbook")

        if data.status_code != 200:
            raise KalshiRequestError(f"Recieved status code {data.status_code} instead of 200. Ticker: {self.ticker}")
        
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

    def kalshi_get_markets(self, limit: int=None, cursor:str=None, status:str=None) -> list[list[KalshiMarket], str]:
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

        if d.status_code != 200:
            # TODO: TEST THIS
            err = ""
            if "error" in d.json():
                err = f'\nError: \n{json.dumps(d.json()["error"])}'
            raise KalshiRequestError(f"Recieved status code {d.status_code} instead of 200. {err}")
        print(d.json())
        markets = d.json()["markets"]
        ret = [[]]
    
        for m in markets:
            market = KalshiMarket(m['ticker'])
            market._load_data(m) # load in the data the same way that refresh_data would

            ret[0].append(market, self.environment)

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

class KalshiRequestError(Exception):
    pass