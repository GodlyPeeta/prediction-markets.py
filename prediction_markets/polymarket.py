from .market import *
import requests
from datetime import datetime

root="https://clob.polymarket.com"

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
    question_id: str # not super sure what this is used for but store anyway
    token_ids: dict[str, str] # the token strings to "yes" and "no" respectively

    def __init__(self, condition_id):
        super().__init__()
        self.condition_id = condition_id