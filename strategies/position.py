from modules.templates import OrderSideValue, OrderSide
from modules.singleSymbol import Symbol
from typing import Type


class Position:
    symbol: Type[type(Symbol)] = None
    quantity: int = 0
    side: Type[type(OrderSideValue)] = OrderSide.PlaceHolder
    avgPrice: float = 0

    def getPnL(self):
        return round(self.side.symbolNum * self.quantity * (self.symbol.ltp - self.avgPrice), 2)

    def getIntro(self):
        return f"{self.side.description} {self.quantity} {self.symbol.ticker} @ {self.avgPrice}, cmp = {self.symbol.ltp}, pnl = {self.getPnL()}"

    def __init__(self, symbol: Type[type(Symbol)], qty, side: Type[type(OrderSideValue)], avgPrice):
        self.symbol = symbol
        self.quantity = qty
        self.side = side
        self.avgPrice = avgPrice
