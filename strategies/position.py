from modules.singleOrder import Order
from modules.templates import OrderSideValue, OrderSide, PositionStatusValue, PositionStatus
from modules.singleSymbol import Symbol
from typing import Type, Dict


class Position:
    symbol: Type[type(Symbol)] = None
    quantity: int = 0
    avgPrice: float = 0

    realized_pnl: float = 0
    position_status: Type[type(PositionStatusValue)] = PositionStatus.Open

    def _getUnrealizedPnL(self) -> float:
        return self.quantity * (self.symbol.ltp - self.avgPrice)

    def getPositionPnL(self):
        return self._getUnrealizedPnL() + self.realized_pnl

    def addFilledOrder(self, order: Type[Order]):
        newQuantity = self.quantity + (order.filledQuantity * order.side)

        if order.side * self.quantity > 0:  # increasing position side
            newPrice = ((self.quantity * self.avgPrice) + (order.filledQuantity * order.avgPrice)) / (
                    abs(self.quantity) + order.filledQuantity)
            # no change in realized pnl

        else:  # decreasing position side  or making it 0 (or even changing sides)
            if newQuantity * self.quantity > 0:  # reducing quantity but not changing sides
                newPrice = self.avgPrice
                unitsRealized = self.quantity - newQuantity
                self.realized_pnl += unitsRealized * (order.avgPrice - self.avgPrice)

            elif newQuantity * self.quantity == 0:  # either start with 0 or go to 0 self.quantity
                if self.position_status == PositionStatus.Closed:   # adding position to closed position
                    newQuantity = order.filledQuantity * order.side
                    newPrice = order.avgPrice
                    self.position_status = PositionStatus.Open
                else:                                               # closing a position
                    newPrice = 0
                    unitsRealized = self.quantity - newQuantity
                    self.realized_pnl += unitsRealized * (order.avgPrice - self.avgPrice)
                    self.position_status = PositionStatus.Closed

            else:  # side changes
                newPrice = order.avgPrice
                unitsRealized = self.quantity
                self.realized_pnl += unitsRealized * (order.avgPrice - self.avgPrice)

        self.quantity = newQuantity
        self.avgPrice = newPrice

    def getIntro(self):
        side = OrderSide.Buy if self.quantity >= 0 else OrderSide.Sell
        return f"{side.description} {self.quantity} {self.symbol.ticker} @ {self.avgPrice}, cmp = {self.symbol.ltp}, pnl = {self.getPositionPnL()}"

    def __init__(self, symbol: Type[type(Symbol)], qty, avgPrice, realizedPnL=0):
        self.symbol = symbol
        self.quantity = qty
        self.avgPrice = avgPrice
        self.realized_pnl = realizedPnL
