# FYERS API PROJECT TO TRADE USING ALGORITM
from modules.login import login, checkConnection
from modules.logging import logger

logger = logger()

fyers = login(logger, autoLogin=True)
checkConnection(fyers)
