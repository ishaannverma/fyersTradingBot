import threading
import time
from typing import Type, Dict

from modules.logging import Logger
from modules.templates import QueuesHandler, OrderStatusObject, OrderSide, getDescriptionForOrderStatus, LogType
from fyers_api.Websocket import ws
from modules.keys import app_credentials
from threading import Thread
from modules.singleOrder import Order
from queue import Queue
from modules.Symbols import Symbols


########################### ORDERS WEBSOCKET ###########################
def run_process_order_update(onMessage, access_token, log_path):
    data_type = "orderUpdate"
    fs = ws.FyersSocket(access_token=access_token, log_path=log_path)
    fs.websocket_data = onMessage
    fs.subscribe(data_type=data_type)
    fs.keep_running()


def startOrdersWebsocket(onMessage, logger):
    thread = Thread(target=run_process_order_update,
                    args=(onMessage, app_credentials['WS_ACCESS_TOKEN'], logger.path,))
    logger.add_log(LogType.INFO, 'Starting orders websocket')
    thread.start()


class Orders:
    _updates_queues: Dict[str, type(Queue)] = {}  # strategy ID to updates queue
    _orders_queue: Type[type(Queue)] = None
    _fyers = None
    _orderIDToStrategyID = {
        # TODO make function to build this
    }
    _logger: Type[type(Logger)] = None

    ########################### ADDING AND REMOVING STRATEGIES ###########################
    def addStrategy(self, strategyID, updatesQueue):
        self._updates_queues[strategyID] = updatesQueue

    ########################### WEBSOCKET ###########################
    def _onSocketMessage(self, msg):
        self._logger.add_log(LogType.DEBUG, "orders websocket:\n" + str(msg))
        if msg['s'] != 'ok':
            return
        info = msg['d']

        symbol = info['symbol']
        fyersID = info['id']
        orderStatus = info['status']
        qty = info['filledQty']
        side = info['side']
        side = OrderSide.Buy if side == 1 else OrderSide.Sell
        price = info['tradedPrice']
        update = {
            'symbol': symbol,
            'orderID': fyersID,  # TODO is unnecessary?
            'orderStatus': orderStatus,  # TODO is unnecessary?
            'qty': qty,
            'avgPrice': price,
            'side': side
        }

        self._updates_queues[self._orderIDToStrategyID[fyersID]].put(update)

        if orderStatus == OrderStatusObject.rejected.status or orderStatus == OrderStatusObject.filled.status or orderStatus == OrderStatusObject.cancelled.status:
            self._logger.add_log(LogType.DEBUG,
                                 f"Removing order for {symbol} from strategy {self._orderIDToStrategyID[fyersID]} because order status is ({getDescriptionForOrderStatus(orderStatus)})")
            self._orderIDToStrategyID.pop(fyersID)

    def _sendDummyFilledUpdate(self, order: Type[type(Order)]):
        def sendUpdateAfterWait():
            time.sleep(3)
            order.status = OrderStatusObject.filled
            update = {
                'symbol': order.symbol,
                'orderID': "dummy",  # TODO is unnecessary?
                'orderStatus': OrderStatusObject.filled.status,  # TODO is unnecessary?
                'qty': order.quantity,
                'avgPrice': order.symbol.ltp,
                'side': order.side
            }
            self._updates_queues[order.strategyID].put(update)
        Thread(target=sendUpdateAfterWait).start()

    ########################### ORDERING ###########################
    def sendOrder(self, order: Type[type(Order)]):
        # TODO cancel if another order of same symbol pending
        data = {
            "symbol": order.symbol.ticker,
            "qty": order.quantity,
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
        self._logger.add_log(LogType.DEBUG, response)

        if response['s'] != "ok":
            order.status = OrderStatusObject.rejected
            return
        order.fyersID = response['id']
        order.status = OrderStatusObject.pending

    # listening to order queue
    def orderQueueListener(self):
        order = self._orders_queue.get()
        self._logger.add_log(LogType.UPDATE, f"Sending order for {order.symbol.ticker}, paper = {order.paperTrade}")
        if order.paperTrade:
            order.status = OrderStatusObject.pending
            self._sendDummyFilledUpdate(order)
            return
        self.sendOrder(order)
        if order.status != OrderStatusObject.rejected:
            self._orderIDToStrategyID[order.fyersID] = order.strategyID

    ########################### init ###########################
    def __init__(self, ordersQueue, fyers, logger):
        self._fyers = fyers
        self._orders_queue = ordersQueue
        self._logger = logger

        startOrdersWebsocket(self._onSocketMessage, self._logger)
        threading.Thread(target=self.orderQueueListener).start()

