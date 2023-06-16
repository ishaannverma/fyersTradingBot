from typing import Type
from queue import Queue


########################### CONTRACT MONTHS ###########################

class ContractMonth:
    MMM = ""
    M = ""

    def __init__(self, mmm: str, m: str):
        self.MMM = mmm.upper()
        self.M = m.upper()


class ContractMonths:
    months_list = [
        ContractMonth('JAN', "1"),
        ContractMonth('FEB', "2"),
        ContractMonth('MAR', "3"),
        ContractMonth('APR', "4"),
        ContractMonth('MAY', "5"),
        ContractMonth('JUN', "6"),
        ContractMonth('JUL', "7"),
        ContractMonth('AUG', "8"),
        ContractMonth('SEP', "9"),
        ContractMonth('OCT', "O"),
        ContractMonth('NOV', "N"),
        ContractMonth('DEC', "D")
    ]
    january = months_list[0]
    february = months_list[1]
    march = months_list[2]
    april = months_list[3]
    may = months_list[4]
    june = months_list[5]
    july = months_list[6]
    august = months_list[7]
    september = months_list[8]
    october = months_list[9]
    november = months_list[10]
    december = months_list[11]


########################### STRATEGY STATUS ###########################

class StrategyStatusValue:
    code: int = 0
    description: str = "untraded"

    def __init__(self, code, desc):
        self.code = code
        self.description = desc


class StrategyStatusObject:
    untraded = StrategyStatusValue(0, "untraded")
    trading = StrategyStatusValue(1, "trading")
    closed = StrategyStatusValue(-1, "closed")


StrategyStatus = StrategyStatusObject()


########################### ORDER STATUS ###########################

class OrderStatusValue:
    status: int = 0
    description: str = "placeholder"

    def __init__(self, stat, desc):
        self.status = stat
        self.description = desc


class OrderStatusObject:
    unsent = OrderStatusValue(0, "Unsent")
    cancelled = OrderStatusValue(1, "Cancelled")
    filled = OrderStatusValue(2, "Filled")
    forFutureUse = OrderStatusValue(3, "For Future Use")
    transit = OrderStatusValue(4, "Transit")
    rejected = OrderStatusValue(5, "Rejected")
    pending = OrderStatusValue(6, "Pending")

    def fromStatusInt(self, num: int):
        if num == 1:
            return self.cancelled
        elif num == 2:
            return self.filled
        if num == 3:
            return self.forFutureUse
        elif num == 4:
            return self.transit
        if num == 5:
            return self.rejected
        elif num == 6:
            return self.pending


OrderStatus = OrderStatusObject()


########################### ORDER SIDE ###########################

class OrderSideValue:
    symbolNum: int = 0
    description: str = "placeholder"

    def __init__(self, symbolNum, description):
        self.symbolNum = symbolNum
        self.description = description


class OrderSideObject:
    Buy = OrderSideValue(1, "BUY")
    Sell = OrderSideValue(-1, "SELL")
    PlaceHolder = OrderSideValue(0, "Placeholder")

    def fromSideInteger(self, num: int):
        if num == 1:
            return self.Buy
        if num == -1:
            return self.Sell
        if num == 0:
            return self.PlaceHolder


OrderSide = OrderSideObject()


########################### POSITION STATUS ###########################

class PositionStatusValue:
    status: int = 1
    description: str = "Open"

    def __init__(self, stat, desc):
        self.status = stat
        self.description = desc


class PositionStatusObject:
    Closed = OrderStatusValue(0, "Closed")
    Open = OrderStatusValue(1, "Open")

    def fromStatusInt(self, num: int):
        if num == 0:
            return self.Closed
        elif num == 1:
            return self.Open


PositionStatus = PositionStatusObject()


########################### LOG TYPE ###########################

class LogTypeValue:
    num: int = 6
    description: str = "print"

    def __init__(self, num, desc):
        self.num = num
        self.description = desc


class LogTypeObject:
    FATAL = LogTypeValue(1, "FATAL")
    ERROR = LogTypeValue(2, "ERROR")
    WARNING = LogTypeValue(3, "WARNING")
    INFO = LogTypeValue(4, "INFO")
    UPDATE = LogTypeValue(4, "UPDATE")
    DEBUG = LogTypeValue(5, "DEBUG")
    # PRINT = LogTypeValue(6, "PRINT")


LogType = LogTypeObject()


########################### LOG LEVEL ###########################

class LogLevelValue:
    num: int = 6

    def __init__(self, num):
        self.num = num


class LogLevelObject:
    OFF = 0
    FATAL = 1
    ERROR = 2
    WARNING = 3
    INFO = 4
    DEBUG = 5
    ALL = 6


LogLevel = LogLevelObject()
