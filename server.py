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

# strategiesHandler.addStrategy(MonthStraddle(symbol=nifty50, vix=indiavix, fyers=fyers, symbolsHandler=symbolsHandler, logger=logger, paperTrade=True))


########################### TELEGRAM ###########################

telegram_commands = {
    'help': 'Get all commands available with this bot',
    'getStrategies': 'All strategies running on the app',
    'strat <stratID> positions': 'Get positions in given strategy',
    # 'strat <stratID> pnl': 'Get PnL of given strategy'
}


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

    telegram_bot.reply_to(message, reply)


@telegram_bot.message_handler(commands=['strat', 's'])
def strategyFunc(message):
    sendTelegram(message.text)
    commands = message.text.split()
    if len(commands) != 3:
        telegram_bot.reply_to(message, f"invalid param length")
        return

    stratID = commands[1]
    query = commands[2]

    if query == 'positions':
        strategy = [(key, value) for key, value in strategiesHandler.strategies_dict.items() if key.startswith(stratID)]
        if len(strategy) < 1:
            telegram_bot.reply_to(message, f"no strat found with this stratID")
            return
        if len(strategy) > 1:
            telegram_bot.reply_to(message, f"be more specific with the stratID")
            return

        stratObject: Type[Strategy] = strategy[0][1]
        reply = ""
        for i, position in enumerate(stratObject.positions):
            if len(reply) != 0:
                reply += "\n"
            reply += f"{i + 1}. {position.getIntro()}"

        telegram_bot.reply_to(message, reply)
        return


# EASTER EGGS
@telegram_bot.message_handler(commands=['sucha', 'swaru'])
def test_telegram(message):
    telegram_bot.reply_to(message, "HEYYYY <3 <3")


# last and blocking line of the app
telegram_bot.infinity_polling()
