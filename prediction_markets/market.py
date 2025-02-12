from __future__ import annotations
from datetime import datetime
from enums import *

class Market:
    """ Represents a single market. 
    Note the difference between a market and an event. An event holds multiple markets. 

    Has ONLY yes/no order options. 

    Abstract class.
    """
    title: str # The listed title of the market
    rules: str # The listed rules to the market. Used to identify differences between seemingly similar markets
    open: bool # Whether this market is open to orders
    open_time: datetime # the time this market opened
    close_time: datetime #the time this market closes, used to calculate returns
    book: OrderBook # The orderbook of this market. Not automatically refreshed

    last_refreshed_data: datetime # the last time the data has been refreshed
    last_refreshed_book: datetime
    
    def __init__(self):
        """ Does not initialize the attributes. Must call refresh to initialize attributes 
        """
        self.last_refreshed_data = None
        self.last_refreshed_book = None

        self.book = OrderBook()

    def refresh_data(self) -> None:
        """ Refreshes all basic data. Does NOT refresh order book
        """
        raise NotImplementedError

    def refresh_book(self) -> None:
        """ Refreshes the order book 
        """
        raise NotImplementedError
    
    

class OrderBook:
    """ An orderbook for a market
    """
    yes: list[list[int]] # each inner list contains two ints. The first int is the price, the second is the number of orders at that price. 
    no: list[list[int]]

    def __init__(self):
        pass

    def update_book(self, yes: list[list[int]]=None, no: list[list[int]]=None) -> None:
        """ Updates the books. Provide with None for no change
        """
        self.yes = yes if yes is not None else self.yes
        self.no = no if no is not None else self.no

    def get_best_orders(side: Side) -> int:
        """ Gets the best price and quantity for yes/no
        """
        pass

    def __str__(self):
        """ str rep
        """
        return f"yes: {self.yes}\nno: {self.no}"