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

class StrategyStatus:
    _code: int = 0
    _description: str = "Untraded"

    def setTrading(self):
        self._code = 1
        self._description = "Trading (active positions)"

    def setClosed(self):
        self._code = 2
        self._description = "Positions closed"


########################### ORDER STATUS ###########################

class OrderStatusValue:
    status: int = 0
    description: str = "placeholder"

    def __init__(self, stat, desc):
        self.status = stat
        self.description = desc


def getDescriptionForOrderStatus(status):
    if status < 0 or status > 6:
        return "Invalid Status"
    if status == 0:
        return "Unsent"
    if status == 1:
        return "Cancelled"

    if status == 2:
        return "Filled"

    if status == 3:
        return "For Future Use"

    if status == 4:
        return "Transit"

    if status == 5:
        return "Rejected"

    if status == 6:
        return "Pending"


class OrderStatusObject:
    unsent = OrderStatusValue(0, "Unsent")
    cancelled = OrderStatusValue(1, "Cancelled")
    filled = OrderStatusValue(2, "Filled")
    forFutureUse = OrderStatusValue(3, "For Future Use")
    transit = OrderStatusValue(4, "Transit")
    rejected = OrderStatusValue(5, "Rejected")
    pending = OrderStatusValue(6, "Pending")


OrderStatus = OrderStatusObject()


########################### ORDER SIDE ###########################

class OrderSideValue:
    symbolNum: int = 0
    description: str = "placeholder"

    def __init__(self, symbolNum, description):
        self.symbolNum = symbolNum
        self.description = description


class OrderSideObject:
    Buy = OrderSideValue(1, "Buy")
    Sell = OrderSideValue(-1, "Sell")
    PlaceHolder = OrderSideValue(0, "Placeholder")


OrderSide = OrderSideObject()


########################### LOG TYPE ###########################

class LogTypeValue:
    num: int = 6
    description: str = "print"

    def __init__(self, num, desc):
        self.num = num
        self.description = desc


class LogTypeObject:
    FATAL = LogTypeValue(0, "FATAL")
    ERROR = LogTypeValue(1, "ERROR")
    WARNING = LogTypeValue(2, "WARNING")
    INFO = LogTypeValue(3, "INFO")
    UPDATE = LogTypeValue(4, "UPDATE")
    DEBUG = LogTypeValue(5, "DEBUG")
    PRINT = LogTypeValue(6, "PRINT")


LogType = LogTypeObject()
