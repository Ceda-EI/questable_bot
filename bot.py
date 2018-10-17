#!/usr/bin/env python3

import logging
from telegram.ext import Updater, CommandHandler

try:
    import config
except ImportError:
    print("Missing Config. Exiting.")
    exit()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
                    %(message)s', level=logging.INFO)


def start(bot, update):
    chat_id = update.message.chat_id
    name = update.message.message
    text = f"Hello {name}!\n" + \
        "Welcome to Questable. To get started, check /help."
    bot.send_message(chat_id=chat_id, text=text)


updater = Updater(token=config.api_key)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()
