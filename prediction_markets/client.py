from __future__ import annotations
from datetime import datetime
from .market import *
from .enums import *

class Client:
    """ A single user client on a platform. Contains all the info required to place trades
    
    Abstract class.
    """

    def __init__(self):
        raise NotImplementedError

    def place_order(self, market: Market, price: float, quantity: float, side: Side) -> Order: 
        """ Creates and places a limit order at some price and quantity. 

        Returns a Order object if it goes through. 
        Raises an error otherwise.
        """
        raise NotImplementedError
    
class Order:
    """ A single limited order placed on a platform by a client.
    
    Abstract class.
    """
    client: Client
    market: Market
    placed_price: float # price per share when the order was placed
    quantity: float
    side: Side

    def __init__(self, client: Client, market: Market, placed_price: float, quantity: float, side: Side):
        self.client = client
        self.market = market
        self.placed_price = placed_price
        self.quantity = quantity
        self.side = side