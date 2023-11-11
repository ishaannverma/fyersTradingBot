import threading
import time
from random import randint
from typing import Type, Dict

from modules.login.login_route import fyers_model_class_obj as fyers
from modules.logging.logging import loggerObject as logger
from modules.logic.templates import OrderSide, LogType, OrderStatus, OrderStatusValue
from fyers_api.Websocket import ws  # TODO update to fyersv3
from modules.keys import app_credentials
from threading import Thread
from modules.logic.singleOrder import Order
from queue import Queue


########################### ORDERS WEBSOCKET ###########################
def run_process_order_update(onMessage):
    def websocketInstance():
        ws_access_token = fyers.get_WS_Access_token()
        if ws_access_token is None:
            raise Exception("WS Access Token evaluated as None")
        fs = ws.FyersSocket(access_token=ws_access_token, log_path=logger.logging_path)
        fs.websocket_data = onMessage
        fs.subscribe(data_type="orderUpdate")
        fs.keep_running()

    while True:
        try:
            websocketInstance()
        except Exception as e:
            logger.add_log(LogType.DEBUG, f"Failed to establish/maintain ORDERS websocket connection: {e}")
            time.sleep(5)

            # retry in 10 seconds
            # TODO this code might not run if hosted on a VM not in India
            # obj = time.localtime()
            # if obj.tm_wday > 4 :
            #     # if saturday or sunday, sleep for 6 hours
            #     time.sleep(6 * 60 * 60)
            # elif obj.tm_hour < 8 or obj.tm_hour > 16:
            #     time.sleep(60*60)
            # else:
            #     time.sleep(10)


def startOrdersWebsocket(onMessage):
    thread = Thread(target=run_process_order_update,
                    args=(onMessage,))
    logger.add_log(LogType.INFO, 'Starting orders websocket')
    thread.start()


class Orders:
    _updates_queues: Dict[str, type(Queue)] = {}  # strategy ID to updates queue
    _orders_queue: Type[type(Queue)] = None
    _ordersDict: Dict[str, type(Order)] = {}  # from fyersID to Order object

    ########################### ADDING AND REMOVING STRATEGIES ###########################
    def addStrategy(self, strategyID, updatesQueue):
        self._updates_queues[strategyID] = updatesQueue

    ########################### WEBSOCKET ###########################
    def _onSocketMessage(self, msg):
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
            dummyID = f"dummyID-{randint(0, 10000)}"
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

        status, response = fyers.place_order(data)

        if status is False:
            order.status = OrderStatus.rejected
            return
        order.fyersID = response['id']
        self._ordersDict[order.fyersID] = order
        order.status = OrderStatus.pending

    # listening to order queue
    def orderQueueListener(self):
        while True:
            order = self._orders_queue.get()
            logger.add_log(LogType.UPDATE,
                           f"Sending {'papertrade' if order.paperTrade else 'fyers trading'} order for {OrderSide.fromSideInteger(order.side).description} {order.orderedQuantity} {order.symbol.ticker} @ cmp = {order.symbol.ltp}")

            self.sendOrder(order)

    ########################### init ###########################
    def __init__(self, ordersQueue):
        self._orders_queue = ordersQueue

        startOrdersWebsocket(self._onSocketMessage)
        threading.Thread(target=self.orderQueueListener).start()
