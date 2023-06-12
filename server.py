# FYERS API PROJECT TO TRADE USING ALGORITM
from modules.login import login, checkConnection
from modules.logging import logger
from modules.telegram import telegram_bot, sendTelegram

logger = logger()

fyers = login(logger, autoLogin=True)
checkConnection(fyers)

telegram_bot.infinity_polling()
