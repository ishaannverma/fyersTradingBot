# FYERS API PROJECT TO TRADE USING ALGORITHM

from modules.login import login, checkConnection
from modules.logging import Logger
from modules.telegram import telegram_bot, sendTelegram
from modules.Symbols import Symbols
from modules.orders import Orders
from strategies.strategiesHandler import StrategyHandler
from strategies.monthStraddle import MonthStraddle
from modules.templates import LogLevel

logger = Logger(LogLevel.DEBUG)

fyers = login(logger, autoLogin=True)
checkConnection(fyers, logger)

symbolsHandler = Symbols(fyers, logger)
nifty50 = symbolsHandler.get('nifty50')
indiavix = symbolsHandler.get('indiavix')

strategiesHandler = StrategyHandler(fyers, symbolsHandler, logger)

# strategiesHandler.addStrategy(MonthStraddle(symbol=nifty50, vix=indiavix, fyers=fyers, symbolsHandler=symbolsHandler, logger=logger, paperTrade=True))

# last and blocking line of the app
telegram_bot.infinity_polling()
