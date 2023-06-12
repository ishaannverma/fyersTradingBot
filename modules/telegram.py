import telebot
from modules.keys import telegram_credentials

telegram_bot = telebot.TeleBot(telegram_credentials['API_KEY'])

telegram_commands = {
    'help': 'Get all commands available with this bot',
    'ping': 'Replies if running'

}


def sendTelegram(message):
    telegram_bot.send_message(1704843212, message)


sendTelegram("Telegram Bot Running")


@telegram_bot.message_handler(commands=['help'])
def help(message):
    text = ""
    for i, (k, v) in enumerate(telegram_commands.items()):
        text += f"{i + 1}. /{k} : {v}\n"
    telegram_bot.reply_to(message, text)


@telegram_bot.message_handler(commands=['ping'])
def ping(message):
    telegram_bot.reply_to(message, "ping")


# EASTER EGGS
@telegram_bot.message_handler(commands=['sucha', 'swaru'])
def test_telegram(message):
    telegram_bot.reply_to(message, "HEYYYY <3 <3")
