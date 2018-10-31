#!/usr/bin/env python3

import logging
import telegram
import sqlite3
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
            ['Add Quest', 'Add Side-quest'],
            ['List Quests', 'List Side-quests']
            ]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


db = sqlite3.connect("questable.db")
cursor = db.cursor()
# Set up tables
queries = [
       ("CREATE TABLE IF NOT EXISTS quests(chat_id int NOT NULL, qid int NOT"
           " NULL, name varchar(255) NOT NULL, difficulty int NOT NULL, "
           "importance int NOT NULL, date int NOT NULL, state int NOT NULL "
           "DEFAULT 0, UNIQUE(chat_id, qid));"),

       ("CREATE TABLE IF NOT EXISTS side_quests(chat_id int NOT NULL, qid int"
           " NOT NULL, name varchar(255) NOT NULL, difficulty int NOT NULL, "
           "importance int NOT NULL, date int NOT NULL, state int NOT NULL "
           "DEFAULT 0, UNIQUE(chat_id, qid));"),

       ("CREATE TABLE IF NOT EXISTS points(chat_id int PRIMARY KEY, points "
           "int);"),

       ("CREATE TABLE IF NOT EXISTS state(chat_id int PRIMARY KEY, state "
           "varchar(10), extra varchar(10));"),
        ]
for query in queries:
    cursor.execute(query)
db.commit()

updater = Updater(token=config.api_key)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()
