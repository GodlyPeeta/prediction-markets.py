from .market import *
import requests
from datetime import datetime
from exceptions import *
import json

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

    def refresh_data(self):
        pass

def _check_api_response(response: requests.Response) -> None:
    if response.status_code == 200:
        return
    
    try:
        js = response.json()
        error_msg = f'{json.dumps(js["error"])}'
    except:
        error_msg = f"Unkown error"
    
    raise APIRequestError(f"Recieved status code {response.status_code}: {error_msg}")