from modules.templates import OrderStatusValue, OrderStatus, OrderSideValue, OrderSide
from typing import Type
from modules.singleSymbol import Symbol


class Order:
    # filled before ordering
    strategyID: str = ""
    symbol: str = ""
    quantity: int = 0
    side: int = 0

    # filled after ordering and getting response
    status: Type[type(OrderStatusValue)] = OrderStatus.unsent
    fyersID: str = ""

    # filled by websocket
    avgPrice: float = 0

    def __init__(self, symbolObject: Type[type(Symbol)], quantity: int, side: Type[type(OrderSideValue)]):
        self.symbol = symbolObject.ticker
        self.quantity = quantity
        self.side = side.symbolNum
