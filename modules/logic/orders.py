import threading
import time
from random import randint
from typing import Type, Dict

from modules.logging.logging import Logger
from modules.logic.templates import OrderSide, LogType, OrderStatus, OrderStatusValue
from fyers_api.Websocket import ws
from modules.keys import app_credentials
from threading import Thread
from modules.logic.singleOrder import Order
from queue import Queue


########################### ORDERS WEBSOCKET ###########################
def run_process_order_update(onMessage, access_token, log_path):
    data_type = "orderUpdate"
    fs = ws.FyersSocket(access_token=access_token, log_path=log_path)
    fs.websocket_data = onMessage
    fs.subscribe(data_type=data_type)
    fs.keep_running()


def startOrdersWebsocket(onMessage, logger):
    thread = Thread(target=run_process_order_update,
                    args=(onMessage, app_credentials['WS_ACCESS_TOKEN'], logger.logging_path,))
    logger.add_log(LogType.INFO, 'Starting orders websocket')
    thread.start()


class Orders:
    _updates_queues: Dict[str, type(Queue)] = {}  # strategy ID to updates queue
    _orders_queue: Type[type(Queue)] = None
    _fyers = None
    _ordersDict: Dict[str, type(Order)] = {}  # from fyersID to Order object
    _logger: Type[type(Logger)] = None

    ########################### ADDING AND REMOVING STRATEGIES ###########################
    def addStrategy(self, strategyID, updatesQueue):
        self._updates_queues[strategyID] = updatesQueue

    ########################### WEBSOCKET ###########################
    def _onSocketMessage(self, msg):
        # self._logger.add_log(LogType.DEBUG, "orders websocket:\n" + str(msg))
        time.sleep(1)
        if msg['s'] != 'ok':
            return
        info = msg['d']

        # symbol = info['symbol']
        fyersID = info['id']
        orderStatus: Type[type(OrderStatusValue)] = OrderStatus.fromStatusInt(info['status'])
        qty = info['filledQty']
        price = info['tradedPrice']

        self._ordersDict[fyersID].updateOrder(qty, orderStatus, price)  # update order object
        self._updates_queues[self._ordersDict[fyersID].strategyID].put(
            self._ordersDict[fyersID])  # send order object to Strategy

        if orderStatus == OrderStatus.rejected or orderStatus == OrderStatus.filled or orderStatus == OrderStatus.cancelled:
            self._ordersDict.pop(fyersID)

    def _sendDummyFilledUpdate(self, order: Type[type(Order)], dummyID: str):
        def sendUpdateAfterWait():
            time.sleep(3)
            msg = {
                's': 'ok',
                'd': {
                    'id': dummyID,
                    'symbol': order.symbol.ticker,
                    'status': OrderStatus.filled.status,
                    'filledQty': order.orderedQuantity,
                    'tradedPrice': order.symbol.ltp,
                    'side': order.side
                }
            }
            self._onSocketMessage(msg)

        Thread(target=sendUpdateAfterWait).start()

    ########################### ORDERING ###########################
    def sendOrder(self, order: Type[type(Order)]):
        if order.paperTrade:
            dummyID = f"dummyID-{randint(0,10000)}"
            order.fyersID = dummyID
            order.status = OrderStatus.pending
            self._ordersDict[order.fyersID] = order
            self._sendDummyFilledUpdate(order, dummyID)
            return

        data = {
            "symbol": order.symbol.ticker,
            "qty": order.orderedQuantity,
            "type": 2,  # market order
            "limitPrice": 0,
            "stopPrice": 0,
            "disclosedQty": 0,
            "side": order.side,
            "productType": "MARGIN",
            "offlineOrder": "False",
            "validity": "IOC"
        }

        response = self._fyers.place_order(data)
        # self._logger.add_log(LogType.DEBUG, response)

        if response['s'] != "ok":
            order.status = OrderStatus.rejected
            return
        order.fyersID = response['id']
        self._ordersDict[order.fyersID] = order
        order.status = OrderStatus.pending

    # listening to order queue
    def orderQueueListener(self):
        while True:
            order = self._orders_queue.get()
            self._logger.add_log(LogType.UPDATE, f"Sending {'papertrade' if order.paperTrade else 'fyers trading'} order for {OrderSide.fromSideInteger(order.side).description} {order.orderedQuantity} {order.symbol.ticker} @ cmp = {order.symbol.ltp}")

            self.sendOrder(order)

    ########################### init ###########################
    def __init__(self, ordersQueue, fyers, logger):
        self._fyers = fyers
        self._orders_queue = ordersQueue
        self._logger = logger

        startOrdersWebsocket(self._onSocketMessage, self._logger)
        threading.Thread(target=self.orderQueueListener).start()
