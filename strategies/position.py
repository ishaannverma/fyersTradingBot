from modules.templates import OrderSideValue, OrderSide
from typing import Type


class Position:
    ticker: str = ""
    quantity: int = 0
    side: Type[type(OrderSideValue)] = OrderSide.PlaceHolder
    avgPrice: float = 0

    def getIntro(self):
        return f"{self.side.description} {self.quantity} {self.ticker} @ {self.avgPrice} "

    def __init__(self, ticker, qty, side: Type[type(OrderSideValue)], avgPrice):
        self.ticker = ticker
        self.quantity = qty
        self.side = side
        self.avgPrice = avgPrice
