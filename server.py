# FYERS API PROJECT TO TRADE USING ALGORITHM
from pprint import pprint

from modules.login import login, checkConnection
from modules.logging import logger
from modules.telegram import telegram_bot, sendTelegram
from modules.Symbols import Symbols
from modules.orders import Orders
from strategies.strategiesHandler import StrategyHandler
from strategies.monthStraddle import MonthStraddle
logger = logger()

fyers = login(logger, autoLogin=True)
checkConnection(fyers)

symbolsHandler = Symbols(fyers, logger)
nifty50 = symbolsHandler.get('nifty50')
indiavix = symbolsHandler.get('indiavix')

strategiesHandler = StrategyHandler(fyers, logger)

monthStraddle = MonthStraddle(nifty50, indiavix, fyers, symbolsHandler, logger, True)
strategiesHandler.addStrategy(monthStraddle)

# last and blocking line of the app
telegram_bot.infinity_polling()
