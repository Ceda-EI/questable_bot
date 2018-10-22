#!/usr/bin/env python3

import logging
import telegram
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
    name = str(update.message.from_user.first_name)
    if update.message.from_user.last_name:
        name += " " + str(update.message.from_user.last_name)
    text = f"Hello {name}!\n" + \
        "Welcome to Questable. To get started, check /help."
    custom_keyboard = [
            ['Add Quest', 'Add Side-quests'],
            ['List Quests', 'List Side-quests']
            ]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


updater = Updater(token=config.api_key)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()
