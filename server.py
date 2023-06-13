# FYERS API PROJECT TO TRADE USING ALGORITM
from modules.login import login, checkConnection
from modules.logging import logger
from modules.telegram import telegram_bot, sendTelegram
from modules.Symbols import Symbols
from modules.dateParsing import customDate
logger = logger()

fyers = login(logger, autoLogin=True)
checkConnection(fyers)

symbolsHandler = Symbols(fyers)
nifty50 = symbolsHandler.get('nifty50')


# NSE:NIFTY23OCT17500CE
# random = symbolsHandler.get('NSE:NIFTY2361517000CE')
print(nifty50.getWeeklyExpiryAfterNDays(38, 18500, "CE"))
# last and blocking line of the app
telegram_bot.infinity_polling()
