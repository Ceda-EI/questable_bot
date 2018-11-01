#!/usr/bin/env python3

import logging
import telegram
import sqlite3
import questable
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

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
            ['Add Quest', 'Add Side Quest'],
            ['List Quests', 'List Side Quests']
            ]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


def add_quest(bot, update, player, type="quest"):
    # Get largest id and set qid to 1 more than that
    if type == "quest":
        x = player.get_quests(None)
    elif type == "side_quest":
        x = player.get_side_quests(None)
    else:
        raise ValueError('Not quest or side_quest')
    if len(x) == 0:
        qid = 1
    else:
        x.sort(key=lambda i: i.QID, reverse=True)
        qid = x[0].QID + 1

    # Add quest / side_quest
    if type == 'quest':
        questable.add_quest(player.DB, player.CHAT_ID, qid, state=0)
        player.set_state('aq', qid)
    if type == 'side_quest':
        questable.add_side_quest(player.DB, player.CHAT_ID, qid, state=0)
        player.set_state('asq', qid)

    # Send message
    chat_id = update.message.chat_id
    text = ("What shall the name of " +
            {"quest": "Quest", "side_quest": "Side Quest"}[type] + " be?")
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


def add_name(bot, update, player, type, qid):
    if type == "quest":
        x = questable.get_quest(player.DB, player.CHAT_ID, qid)
        player.set_state('qd', qid)
    elif type == "side_quest":
        x = questable.get_side_quest(player.DB, player.CHAT_ID, qid)
        player.set_state('sqd', qid)
    else:
        raise ValueError('Not quest or side_quest')

    x.name = update.message.text
    x.update_db()

    chat_id = update.message.chat_id
    text = "How difficult is it?"
    custom_keyboard = [["Low", "Medium", "High"]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


def add_diff(bot, update, player, type, qid):
    message = update.message.text
    chat_id = update.message.chat_id
    if message == "Low":
        diff = 1
    elif message == "Medium":
        diff = 2
    elif message == "High":
        diff = 3
    else:
        bot.send_message(chat_id=chat_id, text="Invalid Option")
        return False

    if type == "quest":
        x = questable.get_quest(player.DB, player.CHAT_ID, qid)
        player.set_state('qi', qid)
    elif type == "side_quest":
        x = questable.get_side_quest(player.DB, player.CHAT_ID, qid)
        player.set_state('sqi', qid)
    else:
        raise ValueError('Not quest or side_quest')

    x.diff = diff
    x.update_db()

    text = "How important is it?"
    custom_keyboard = [["Low", "Medium", "High"]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


def add_imp(bot, update, player, type, qid):
    message = update.message.text
    chat_id = update.message.chat_id
    if message == "Low":
        imp = 1
    elif message == "Medium":
        imp = 2
    elif message == "High":
        imp = 3
    else:
        bot.send_message(chat_id=chat_id, text="Invalid Option")
        return False

    if type == "quest":
        x = questable.get_quest(player.DB, player.CHAT_ID, qid)
        player.set_state('none', 0)
    elif type == "side_quest":
        x = questable.get_side_quest(player.DB, player.CHAT_ID, qid)
        player.set_state('none', 0)
    else:
        raise ValueError('Not quest or side_quest')

    x.imp = imp
    x.update_db()

    text = "Quest Added!"
    bot.send_message(chat_id=chat_id, text=text)
    send_status(bot, update, player)


def send_status(bot, update, player):
    name = str(update.message.from_user.first_name)
    if update.message.from_user.last_name:
        name += " " + str(update.message.from_user.last_name)
    points = player.get_points()
    total_quests = len(player.get_quests(None))
    completed_quests = len(player.get_quests(1))
    total_side_quests = len(player.get_side_quests(None))
    completed_side_quests = len(player.get_side_quests(1))

    text = (f'<b>{name}</b>\n\n'
            f'🔥XP: {points}\n'
            f'⭐️Quests: {completed_quests}/{total_quests}\n'
            f'💠Side Quests: {completed_side_quests}/{total_side_quests}\n')
    chat_id = update.message.chat_id
    custom_keyboard = [
            ['Add Quest', 'Add Side Quest'],
            ['List Quests', 'List Side Quests']
            ]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup,
                     parse_mode="HTML")


def me_handler(bot, update, db):
    chat_id = update.message.chat_id
    player = questable.player(db, chat_id)
    send_status(bot, update, player)


def message_handling(bot, update, db):
    text = update.message.text
    player = questable.player(db, update.message.chat_id)
    state = player.get_state()

    # states
    # none: in the middle of nothing
    # aq / asq: Added Quest: User has pressed add Quest/Side Quest
    # qd / sqd: (Side) Quest difficulty: User has entered title, difficulty
    # requested
    # qi / sqi: (Side) Quest importance: User has entered difficulty,
    # importance requested

    if state["state"] == "none":
        if text == "Add Quest":
            add_quest(bot, update, player)
        elif text == "Add Side Quest":
            add_quest(bot, update, player, "side_quest")
    elif state["state"] == "aq":
        add_name(bot, update, player, "quest", state["extra"])
    elif state["state"] == "asq":
        add_name(bot, update, player, "side_quest", state["extra"])
    elif state["state"] == "qd":
        add_diff(bot, update, player, "quest", state["extra"])
    elif state["state"] == "sqd":
        add_diff(bot, update, player, "side_quest", state["extra"])
    elif state["state"] == "qi":
        add_imp(bot, update, player, "quest", state["extra"])
    elif state["state"] == "sqi":
        add_imp(bot, update, player, "side_quest", state["extra"])


db = sqlite3.connect("questable.db", check_same_thread=False)
cursor = db.cursor()
# Set up tables
queries = [
       ("CREATE TABLE IF NOT EXISTS quests(chat_id int NOT NULL, qid int NOT"
           " NULL, name varchar(255), difficulty int, importance int, "
           "state int DEFAULT 0, UNIQUE(chat_id, qid));"),

       ("CREATE TABLE IF NOT EXISTS side_quests(chat_id int NOT NULL, qid int "
           "NOT NULL, name varchar(255), difficulty int, importance int, "
           "state int DEFAULT 0, UNIQUE(chat_id, qid));"),

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

start_handler = CommandHandler('me', lambda x, y: me_handler(x, y, db))
dispatcher.add_handler(start_handler)

handler = MessageHandler(Filters.text, lambda x, y: message_handling(x, y, db))
dispatcher.add_handler(handler)

updater.start_polling()
