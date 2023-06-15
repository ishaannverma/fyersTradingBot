import threading
import time
from pprint import pprint
from typing import Type, Dict
from modules.templates import QueuesHandler, OrderStatusObject, OrderSide
from fyers_api.Websocket import ws
from modules.keys import app_credentials
from threading import Thread
from modules.singleOrder import Order


########################### ORDERS WEBSOCKET ###########################
def run_process_order_update(onMessage, access_token, log_path):
    data_type = "orderUpdate"
    fs = ws.FyersSocket(access_token=access_token, log_path=log_path)
    fs.websocket_data = onMessage
    fs.subscribe(data_type=data_type)
    fs.keep_running()


def startOrdersWebsocket(onMessage, log_path):
    thread = Thread(target=run_process_order_update,
                    args=(onMessage, app_credentials['WS_ACCESS_TOKEN'], log_path,))
    print(f'INFO: Starting orders websocket')
    thread.start()


class Orders:
    _queues: Dict[str, QueuesHandler] = {}  # strategy ID to handlers
    _fyers = None
    _orderIDToStrategyID = {
        # TODO make function to build this
    }

    ########################### ADDING AND REMOVING STRATEGIES ###########################
    def addStrategy(self, strategyID, ordersQueue, updatesQueue):
        queueHandler = QueuesHandler(ordersQueue, updatesQueue)
        self._queues[strategyID] = queueHandler

    ########################### WEBSOCKET ###########################
    def _onSocketMessage(self, msg):
        pprint(f"orders websocket: {msg}")
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

        self._queues[self._orderIDToStrategyID[fyersID]].updates.put(update)

        if orderStatus == OrderStatusObject.rejected.status or orderStatus == OrderStatusObject.filled.status or orderStatus == OrderStatusObject.cancelled.status:
            print(
                f"Removing order for {symbol} from strategy {self._orderIDToStrategyID[fyersID]} because order status is ({OrderStatusObject.getDescriptionForStatus(orderStatus)})")
            self._orderIDToStrategyID.pop(fyersID)

    ########################### ORDERING ###########################
    def sendOrder(self, order: Type[type(Order)]):
        # TODO cancel if another order of same symbol pending
        data = {
            "symbol": order.symbol,
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
        print(response)
        if response['s'] != "ok":
            order.status = OrderStatusObject.rejected
            return
        order.fyersID = response['id']
        order.status = OrderStatusObject.pending

    # listening to all the queues
    def orderQueueListener(self):
        while True:
            for stratID, queuesHandler in self._queues.items():
                ordersQueue = queuesHandler.orders
                while not ordersQueue.empty():
                    order = ordersQueue.get(block=False)
                    self.sendOrder(order)
                    if order.status != OrderStatusObject.rejected:
                        self._orderIDToStrategyID[order.fyersID] = stratID
            time.sleep(5)

    def startOrderingThread(self):
        threading.Thread(target=self.orderQueueListener).start()

    ########################### init ###########################
    def __init__(self, fyers, log_path):
        self._fyers = fyers
        startOrdersWebsocket(self._onSocketMessage, log_path)
        self.startOrderingThread()

    # {"s": "ok", "d": {"orderDateTime": 2002234599, "id": '
    #                                                      '"23061400128345", "exchOrdId": "23061400128345", "side": 1, "segment": "E", '
    #                                                      '"instrument": "", "productType": "INTRADAY", "status": 2, "qty": 1, '
    #                                                      '"remainingQuantity": 0, "filledQty": 1, "limitPrice": 77.05, "stopPrice": '
    #                                                      '0.0, "type": 2, "discloseQty": 0, "dqQtyRem": 0, "orderValidity": "DAY", '
    #                                                      '"slNo": 2, "offlineOrder": false, "message": "TRADE_CONFIRMED", '
    #                                                      '"orderNumStatus": "23061400128345:2", "tradedPrice": 77.05, "fyToken": '
    #                                                      '"10100000005097", "symbol": "NSE:ZOMATO-EQ"}, "ws_type": 1}
