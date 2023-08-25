from modules.logic.templates import OrderStatusValue, OrderStatus, OrderSideValue
from typing import Type
from modules.strategies.singleSymbol import Symbol


class Order:
    # filled before ordering
    strategyID: str = ""
    symbol: Type[type(Symbol)] = None
    orderedQuantity: int = 0
    side: int = 0
    paperTrade: bool = True

    # filled after ordering and getting response
    status: Type[type(OrderStatusValue)] = OrderStatus.unsent
    fyersID: str = ""

    # filled by websocket
    filledQuantity: int = 0
    avgPrice: float = 0

    def updateOrder(self, filledQty: int, status: Type[type(OrderStatusValue)], price: float):
        self.filledQuantity = filledQty
        self.status = status
        self.avgPrice = price

    def __init__(self, symbolObject: Type[type(Symbol)], quantity: int, side: Type[type(OrderSideValue)],
                 paperTrade=True):
        self.symbol = symbolObject
        self.orderedQuantity = quantity
        self.side = side.symbolNum
        self.paperTrade = paperTrade
