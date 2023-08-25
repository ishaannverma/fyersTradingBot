import json
import os
import time

from modules.logic.templates import LogType
from modules.strategies.supported.monthStraddle import MonthStraddle
from modules.strategies.supported.strategyTemplate import Strategy
from typing import Type, Dict
from queue import Queue
from modules.logic.orders import Orders
from threading import Thread

from modules.login.login_route import fyers_model_class_obj as fyers
from modules.logging.logging import loggerObject as logger


class StrategyHandler:
    strategies_dict: Dict[str, type(Strategy)] = {}
    _commands_queues: Dict[str, type(Queue)] = {}
    _ordering_module = None
    _ordering_module_orders_queue = Queue()  # from strategy to ordering module
    _symbolsHandler = None

    def loadSavedStrategies(self):
        for fileName in os.listdir(logger.strat_bin_path):
            if not fileName.endswith(".json"):
                continue

            with open(os.path.join(logger.strat_bin_path, fileName), "rb") as file:
                dataDict = json.load(file)
                strategyName = dataDict['strategyName']
                # status = dataDict['status']
                killSwitch = dataDict['killSwitch']
                paperTrade = dataDict['paperTrade']

                if killSwitch:
                    continue

                logger.add_log(LogType.INFO, f"loading unclosed strategy {fileName.split('.')[0]}")

                if strategyName == "MonthStraddle":
                    strategyObject = MonthStraddle(None, None, self._symbolsHandler,
                                                   paperTrade).fill_from_json(dataDict)
                    self.addStrategy(strategyObject)

    def addStrategy(self, strategy: Type[type(Strategy)]):
        updatesQueue = Queue()  # from ordering module to strategy
        commandsQueue = Queue()  # from strategyHandler to strategy

        strategy.setQueues(orders=self._ordering_module_orders_queue, updates=updatesQueue, commands=commandsQueue)
        # same orders queue, different queues for updates and commands

        strategyID = strategy.id

        self._ordering_module.addStrategy(strategyID, updatesQueue)
        if strategyID in self.strategies_dict:
            logger.add_log(LogType.ERROR, f"Trying to add strategy with ID {strategyID} when one already exists")
            return strategyID
        self.strategies_dict[strategyID] = strategy
        self._commands_queues[strategyID] = commandsQueue

        print("starting")
        strategy.start()
        logger.add_log(LogType.UPDATE, f"Added {strategy.strategyName}: {strategyID}")
        return strategyID

    def removeStrategy(self, strategyID: str):
        commands_queue = self._commands_queues[strategyID]
        command = {
            'command': 'kill'
        }
        commands_queue.put(command)  # strategy will close itself and return only once all positions are closed

        self.strategies_dict.pop(strategyID)
        self._commands_queues.pop(strategyID)

    def getStrategy(self, strategyID: str):
        try:
            return self.strategies_dict[strategyID]
        except:
            return None

    def __init__(self, symbolsHandler):
        self._ordering_module = Orders(self._ordering_module_orders_queue)
        self._symbolsHandler = symbolsHandler

        def loaderTrigger():
            while not fyers.checkConnection():
                time.sleep(2)
            self.loadSavedStrategies()

        Thread(target=loaderTrigger).start()
