from strategies.strategyTemplate import Strategy
from typing import Type
from queue import Queue
from modules.orders import Orders


class StrategyHandler:
    _strategies_list = []
    _ordering_module = None
    _ordering_module_orders_queue = Queue() # from strategy to ordering module
    _logger = None
    _fyers = None

    def __init__(self, fyers, logger):
        self._fyers = fyers
        self._logger = logger
        self._ordering_module = Orders(self._fyers, self._logger.path)

    def addStrategy(self, strategy: Type[type(Strategy)]):
        updatesQueue = Queue()  # from ordering module to strategy
        commandsQueue = Queue()  # from strategyHandler to strategy
        # TODO add commands queue to handler too

        strategy.setQueues(self._ordering_module_orders_queue, updatesQueue, commandsQueue)

        strategyID = strategy.id
        strategy.startLogicOnThread()

        self._ordering_module.addStrategy(strategyID, self._ordering_module_orders_queue, updatesQueue)
        self._strategies_list.append(strategy)

        return strategyID

    def removeStrategy(self):
        pass