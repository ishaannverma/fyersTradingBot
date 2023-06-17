# FYERS API PROJECT TO TRADE USING ALGORITHM
from typing import Type

from modules.login import login, checkConnection
from modules.logging import Logger
from modules.Symbols import Symbols
from modules.orders import Orders
from strategies.strategiesHandler import StrategyHandler
from strategies.monthStraddle import MonthStraddle
from modules.templates import LogLevel
import telebot
from modules.keys import telegram_credentials
from strategies.strategyTemplate import Strategy

telegram_bot = telebot.TeleBot(telegram_credentials['API_KEY'])


def sendTelegram(message):
    telegram_bot.send_message(1704843212, message)


logger = Logger(LogLevel.DEBUG, sendTelegram)

fyers = login(logger, autoLogin=True)
checkConnection(fyers, logger)

symbolsHandler = Symbols(fyers, logger)
nifty50 = symbolsHandler.get('nifty50')
indiavix = symbolsHandler.get('indiavix')

strategiesHandler = StrategyHandler(fyers, symbolsHandler, logger)


########################### TELEGRAM ###########################

telegram_commands = {
    'help': 'Get all commands available with this bot',
    'getStrategies': 'All strategies running on the app',
    'addStrategy <stratName or "help"> <comma separated args in parenthesis>': 'Add a strategy (send with keyword "help" for more info)',
    'strat <stratID> kill': 'Get PnL of given strategy',
    'strat <stratID> positions': 'Get positions in given strategy',
    'strat <stratID> pnl': 'Get PnL of given strategy',
}

addStratHelp = {
    'MonthStraddle': "Monthly short straddle with expiry more than 7 days away. Args string = 'underlying=<nifty50>,paperTrade=<true>'"
}


# TODO add changes to positions and all to savefile too

@telegram_bot.message_handler(commands=['help'])
def telegramHelp(message):
    text = ""
    for i, (k, v) in enumerate(telegram_commands.items()):
        text += f"{i + 1}. /{k} : {v}\n"
    telegram_bot.reply_to(message, text)


@telegram_bot.message_handler(commands=['getStrategies'])
def getStrategies(message):
    reply = ""

    for i, (stratID, strategy) in enumerate(strategiesHandler.strategies_dict.items()):
        if len(reply) != 0:
            reply += "\n"
        reply += f"{i + 1}. {strategy.getIntro()}"

    if len(reply) == 0:
        reply = "no strategies to show"

    telegram_bot.reply_to(message, reply)


@telegram_bot.message_handler(commands=['addStrategy', 'add'])
def addStrategy(message):
    try:
        keyword = message.text.split()[1]
    except:
        keyword = "help"

    try:
        argsString = message.text.split("(")[1][:-1]  # now both ( and ) are removed
        signSeparated = argsString.split(",")
        argsDict = {}
        for pair in signSeparated:
            k = pair.split("=")[0].strip()
            v = pair.split("=")[1].strip()
            argsDict[k.lower()] = v.lower()
    except:
        argsDict = {}

    if keyword == "help":
        reply = ""

        for i, (stratName, stratInfo) in enumerate(addStratHelp.items()):
            if len(reply) != 0:
                reply += "\n"
            reply += f"{i + 1}. {stratName} : {stratInfo}\n"

        telegram_bot.reply_to(message, reply)
        return

    if keyword.lower() == "MonthStraddle".lower():
        try:
            underlying = symbolsHandler.get(argsDict['underlying'].lower())
            paperTrade = True if argsDict['papertrade'] == 'true' else False
        except:
            telegram_bot.reply_to(message, f"ill formed args string")
            return

        stratID = strategiesHandler.addStrategy(
            MonthStraddle(symbol=underlying, vix=indiavix, fyers=fyers, symbolsHandler=symbolsHandler, logger=logger,
                          paperTrade=paperTrade))

        telegram_bot.reply_to(message, stratID)
        return


@telegram_bot.message_handler(commands=['strat', 's'])
def strategyFunc(message):
    commands = message.text.split()
    if len(commands) != 3:
        telegram_bot.reply_to(message, f"invalid param length")
        return

    stratID = commands[1]
    query = commands[2]

    strategy = [(key, value) for key, value in strategiesHandler.strategies_dict.items() if key.startswith(stratID)]
    if len(strategy) < 1:
        telegram_bot.reply_to(message, f"no strat found with this stratID")
        return
    if len(strategy) > 1:
        telegram_bot.reply_to(message, f"be more specific with the stratID")
        return

    stratObject: Type[type(Strategy)] = strategy[0][1]

    if query == 'kill':
        strategiesHandler.removeStrategy(stratObject.id)

    if query == 'positions':
        reply = ""
        for i, (ticker, position) in enumerate(stratObject.positions.items()):
            if len(reply) != 0:
                reply += "\n"
            reply += f"{i + 1}. {position.getIntro()}"

        if len(reply) == 0:
            reply = "no positions to show"
        telegram_bot.reply_to(message, reply)
        return

    if query == 'pnl':
        reply = str(stratObject.getPnL())
        telegram_bot.reply_to(message, reply)
        return


# EASTER EGGS
@telegram_bot.message_handler(commands=['sucha', 'swaru'])
def test_telegram(message):
    telegram_bot.reply_to(message, "HEYYYY <3 <3")


# last and blocking line of the app
telegram_bot.infinity_polling()
