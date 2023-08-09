# FYERS API PROJECT TO TRADE USING ALGORITHM

from modules.login.login import login, checkConnection
from modules.logging import Logger
from modules.Symbols import Symbols
from strategies.strategiesHandler import StrategyHandler
from modules.templates import LogLevel
from flask import Flask

def sendTelegram(message):
    pass

app = Flask(__name__)

logger = Logger(LogLevel.DEBUG, sendTelegram)

fyers = login(logger, autoLogin=True)
checkConnection(fyers, logger)

symbolsHandler = Symbols(fyers, logger)
nifty50 = symbolsHandler.get('nifty50')
indiavix = symbolsHandler.get('indiavix')

strategiesHandler = StrategyHandler(fyers, symbolsHandler, logger)
