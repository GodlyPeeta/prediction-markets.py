from __future__ import annotations

from .market import *
from .client import *
import requests
from datetime import datetime
from enum import Enum
import json
from .enums import *
from typing import List
from .exceptions import *
from dateutil.parser import isoparse

# The CLOB is for api requests related to order books and anything writable, the gamma is read only. 
# However, they still have overlap in coverage and program should switch between them depending on what is more appropriate for the task
clobRoot="https://clob.polymarket.com"
gammaRoot="https://gamma-api.polymarket.com"

class PMMarket(Market):
    """ A market on Polymarket
    """
    title: str # The listed title of the market
    rules: str # The listed rules to the market. Used to identify differences between seemingly similar markets
    open: bool # Whether this market is open to orders
    open_time: datetime # the time this market opened
    close_time: datetime #the time this market closes, used to calculate returns
    book: OrderBook # The orderbook of this market. Not automatically refreshed

    last_refreshed_data: datetime # the last time the data has been refreshed
    last_refreshed_book: datetime

    condition_id: str # used to search via endpoints
    token_ids: dict[str, str] # the token strings to "yes" and "no" respectively

    def __init__(self, condition_id):
        super().__init__()
        self.condition_id = condition_id

        def _load_data(self, dataJSON: dict) -> None:
            """ Interprets data given from the PM API and refreshes this object.

            Note that this DOES update last_refreshed_data. 
            """
            self.title = dataJSON["question"]
            self.rules = dataJSON["description"]
            self.open = dataJSON["active"]

            self.open_time = isoparse(dataJSON["createdAt"])
            self.close_time = isoparse(dataJSON['endDate'])

            self.last_refreshed_data = datetime.now()

            self.condition_id = dataJSON["conditionId"]

    def refresh_data(self):
        PMMarket.refresh_markets(self)

    # this function exists to save latency on updating a lot of markets at once
    def refresh_markets(markets: List[PMMarket]) -> None:
        """ Refreshes all the markets in <markets> at once with minimal API calls.
        """
        params = {"condition_ids": []}
        for m in markets:
            params["condition_ids"].append(m.condition_id)
        
        # check for URL too long 414/413 error
        length = len(requests.Request('GET', f"{gammaRoot}/markets", params=params).prepare().url)
        if length > 8192:
            raise URLParamError("URL too long, try splitting this call into smaller calls")

        data = requests.get(f"{gammaRoot}/markets", params=params)

        _check_api_response(data)

        markets_d = {}
        for m in markets:
            markets_d[m.condition_id] = m

        data = data.json()

        gotKeyError = False
        erroneousTickers = []
        for m in data:
            try:
                markets_d[m['conditionId']]._load_data(m)
            except KeyError:
                gotKeyError = True
                erroneousTickers.append(m['conditionId'])
        
        if gotKeyError:
            raise KeyError(erroneousTickers)


def _check_api_response(response: requests.Response) -> None:
    if response.status_code == 200:
        return
    
    try:
        js = response.json()
        error_msg = f'{json.dumps(js["error"])}'
    except:
        error_msg = f"Unkown error"
    
    raise APIRequestError(f"Recieved status code {response.status_code}: {error_msg}")