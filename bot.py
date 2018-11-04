#!/usr/bin/env python3

import logging
import telegram
import sqlite3
import questable
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
        RegexHandler

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
    message = update.message.text.lower()
    chat_id = update.message.chat_id
    if message == "low":
        diff = 1
    elif message == "medium":
        diff = 2
    elif message == "high":
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
    message = update.message.text.lower()
    chat_id = update.message.chat_id
    if message == "low":
        imp = 1
    elif message == "medium":
        imp = 2
    elif message == "high":
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


def send_status(bot, update, player, prefix=""):
    name = str(update.message.from_user.first_name)
    if update.message.from_user.last_name:
        name += " " + str(update.message.from_user.last_name)
    points = player.get_points()
    total_quests = len(player.get_quests(None))
    completed_quests = len(player.get_quests(1))
    total_side_quests = len(player.get_side_quests(None))
    completed_side_quests = len(player.get_side_quests(1))

    text = (f'<b>{name}</b>\n\n' + prefix +
            f'<b>🔥 XP:</b> {points}\n'
            f'<b>⭐️ Quests:</b> {completed_quests}/{total_quests}\n'
            f'<b>💠 Side Quests:</b> {completed_side_quests}/'
            f'{total_side_quests}\n')
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
    drop_state(bot, update, player)
    send_status(bot, update, player)


def list_quests(bot, update, player, type):
    if type == "quest":
        x = player.get_quests(0)
    elif type == "side_quest":
        x = player.get_side_quests(0)
    else:
        raise ValueError('Not quest or side_quest')
    text = "<b>List of " + {"quest": "Quests", "side_quest":
                            "Side Quests"}[type] + "</b>\n"
    x.sort(key=lambda i: (i.imp, -i.QID), reverse=True)
    if type == "quest":
        for i in x:
            text += f"\n/Q_{i.QID} {i.name}"
    else:
        for i in x:
            text += f"\n/SQ_{i.QID} {i.name}"

    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")


def quest(bot, update, player, qid, type):
    try:
        if type == "quest":
            x = questable.get_quest(player.DB, player.CHAT_ID, qid)
        elif type == "side_quest":
            x = questable.get_side_quest(player.DB, player.CHAT_ID, qid)
    except Exception:
        chat_id = update.message.chat_id
        text = ("<b>❗️ Could not find " +
                {"quest": "Quest", "side_quest": "Side Quest"}[type] + "</b>")
        bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        return

    text = ("<b>🗺 " + {"quest": "Quest", "side_quest": "Side Quest"}[type]
            + f":</b> {x.name}"
            "\n<b>📌 Priority:</b> " + ["Low", "Medium", "High"][x.imp-1]
            + "\n<b>📘 Difficulty:</b> " + ["Low", "Medium", "High"][x.diff-1]
            + "\n<b>" + ["❎", "✅"][x.state] + " Status:</b> "
            + ["Incomplete", "Complete"][x.state])

    if x.state == 1:
        player.set_state('bo', 0)
        custom_keyboard = [["Back"]]
    elif x.state == 0:
        state = {"quest": "eq", "side_quest": "esq"}[type]
        player.set_state(state, qid)
        custom_keyboard = [
                ["Mark as done"],
                ["Edit Name", "Change Priority", "Change Difficulty"],
                ["Back"]]

    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML",
                     reply_markup=reply_markup)


def quest_handling(bot, update, db):
    text = update.message.text.lower().split("_")
    chat_id = update.message.chat_id
    player = questable.player(db, chat_id)
    drop_state(bot, update, player)
    if text[0] == "/q":
        quest(bot, update, player, text[1], "quest")
    elif text[0] == "/sq":
        quest(bot, update, player, text[1], "side_quest")


def mark_as_done(bot, update, player, qid, type):
    if type == "quest":
        x = questable.get_quest(player.DB, player.CHAT_ID, qid)
    elif type == "side_quest":
        x = questable.get_side_quest(player.DB, player.CHAT_ID, qid)
    else:
        raise ValueError('Not quest or side_quest')

    if x.state == 1:
        return
    x.state = 1
    x.update_db()
    points = (55 if type == "quest" else 0) + 10*x.imp + 15*x.diff
    player.add_points(points)
    player.set_state('none', 0)
    send_status(bot, update, player, f"<b>🌟 Earned {points} XP</b>\n\n")
    chat_id = update.message.chat_id
    custom_keyboard = [
            ['Add Quest', 'Add Side Quest'],
            ['List Quests', 'List Side Quests']
            ]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_animation(chat_id=chat_id, animation=random.choice(config.gifs),
                       reply_markup=reply_markup)


def edit_quest(bot, update, player, qid, target, type):
    if type == "quest":
        x = questable.get_quest(player.DB, player.CHAT_ID, qid)
    elif type == "side_quest":
        x = questable.get_side_quest(player.DB, player.CHAT_ID, qid)
    else:
        raise ValueError('Not quest or side_quest')

    message = update.message.text
    chat_id = update.message.chat_id

    if target == "name":
        x.name = message
        text = "<b>Updated Name</b>"
    elif target == "imp" or target == "diff":
        message = message.lower()
        if message != "low" and message != "medium" and message != "high":
            bot.send_message(chat_id=chat_id, text="Invalid Option")
            return
        else:
            num = {"low": 1, "medium": 2, "high": 3}[message]
            if target == "imp":
                x.imp = num
                text = "<b>Updated Priority</b>"
            elif target == "diff":
                x.diff = num
                text = "<b>Updated Difficulty</b>"

    x.update_db()
    if type == "quest":
        player.set_state('eq', qid)
    elif type == "side_quest":
        player.set_state('esq', qid)
    custom_keyboard = [
            ["Mark as done"],
            ["Edit Name", "Change Priority", "Change Difficulty"],
            ["Back"]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup,
                     parse_mode="HTML")


def drop_state(bot, update, player):
    state = player.get_state()
    if state["state"] in ["eqn", "esqn", "eqi", "esqi", "eqd", "esqd", "bo",
                          "eq", "esq"]:
        player.set_state('none', 0)
    elif state["state"] in ["aq", "qd", "qi"]:
        x = questable.get_quest(player.DB, player.CHAT_ID, state["extra"])
        x.delete_from_db()
        player.set_state('none', 0)
    elif state["state"] in ["asq", "sqd", "sqi"]:
        x = questable.get_side_quest(player.DB, player.CHAT_ID, state["extra"])
        x.delete_from_db()
        player.set_state('none', 0)


def message_handling(bot, update, db):
    text = update.message.text.lower()
    player = questable.player(db, update.message.chat_id)
    state = player.get_state()

    # states
    # none: in the middle of nothing
    # aq / asq: Added Quest: User has pressed add Quest/Side Quest
    # qd / sqd: (Side) Quest difficulty: User has entered title, difficulty
    # requested
    # qi / sqi: (Side) Quest importance: User has entered difficulty,
    # importance requested
    # eq / esq: Edit Quest / Side Quest. the user press /Q_\d+ or /SQ_\d+
    # bo: Back Only
    # eqn / esqn: Edit Quest / Side Quest Name
    # eqi / esqi: Edit Quest / Side Quest Importance
    # eqd / esqd: Edit Quest / Side Quest Difficulty

    if state["state"] == "none":
        if text == "add quest":
            add_quest(bot, update, player)
        elif text == "add side quest":
            add_quest(bot, update, player, "side_quest")
        elif text == "list quests":
            list_quests(bot, update, player, "quest")
        elif text == "list side quests":
            list_quests(bot, update, player, "side_quest")

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

    elif state["state"] == "eq":
        if text == "back":
            player.set_state('none', 0)
            send_status(bot, update, player)
        elif text == "mark as done":
            mark_as_done(bot, update, player, state["extra"], "quest")
        elif text == "edit name":
            player.set_state('eqn', state["extra"])
            text = "What shall the new name of the Quest be?"
            reply_markup = telegram.ReplyKeyboardRemove()
            bot.send_message(chat_id=player.CHAT_ID, text=text,
                             reply_markup=reply_markup)
        elif text == "change priority":
            player.set_state('eqi', state["extra"])
            text = "How important is it?"
            custom_keyboard = [["Low", "Medium", "High"]]
            reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            bot.send_message(chat_id=player.CHAT_ID, text=text,
                             reply_markup=reply_markup)
        elif text == "change difficulty":
            player.set_state('eqd', state["extra"])
            text = "How difficult is it?"
            custom_keyboard = [["Low", "Medium", "High"]]
            reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            bot.send_message(chat_id=player.CHAT_ID, text=text,
                             reply_markup=reply_markup)

    elif state["state"] == "esq":
        if text == "back":
            player.set_state('none', 0)
            send_status(bot, update, player)
        elif text == "mark as done":
            mark_as_done(bot, update, player, state["extra"], "side_quest")
        elif text == "edit name":
            player.set_state('esqn', state["extra"])
            text = "What shall the new name of the Side Quest be?"
            reply_markup = telegram.ReplyKeyboardRemove()
            bot.send_message(chat_id=player.CHAT_ID, text=text,
                             reply_markup=reply_markup)
        elif text == "change priority":
            player.set_state('esqi', state["extra"])
            text = "How important is it?"
            custom_keyboard = [["Low", "Medium", "High"]]
            reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            bot.send_message(chat_id=player.CHAT_ID, text=text,
                             reply_markup=reply_markup)
        elif text == "change difficulty":
            player.set_state('esqd', state["extra"])
            text = "How difficult is it?"
            custom_keyboard = [["Low", "Medium", "High"]]
            reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            bot.send_message(chat_id=player.CHAT_ID, text=text,
                             reply_markup=reply_markup)

    elif state["state"] == "bo":
        player.set_state('none', 0)
        send_status(bot, update, player)

    elif state["state"] == "eqn":
        edit_quest(bot, update, player, state["extra"], "name", "quest")

    elif state["state"] == "esqn":
        edit_quest(bot, update, player, state["extra"], "name", "side_quest")

    elif state["state"] == "eqi":
        edit_quest(bot, update, player, state["extra"], "imp", "quest")

    elif state["state"] == "esqi":
        edit_quest(bot, update, player, state["extra"], "imp", "side_quest")

    elif state["state"] == "eqd":
        edit_quest(bot, update, player, state["extra"], "diff", "quest")

    elif state["state"] == "esqd":
        edit_quest(bot, update, player, state["extra"], "diff", "side_quest")


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

me = CommandHandler('me', lambda x, y: me_handler(x, y, db))
dispatcher.add_handler(me)

cancel = CommandHandler('cancel', lambda x, y: me_handler(x, y, db))
dispatcher.add_handler(cancel)

handler = MessageHandler(Filters.text, lambda x, y: message_handling(x, y, db))
dispatcher.add_handler(handler)

unknown = CommandHandler(Filters.command, lambda x, y: message_handling(x, y,
                                                                        db))
dispatcher.add_handler(unknown)

quest_handler = RegexHandler(r"/[Ss]?[Qq]_\d+", lambda x, y:
                             quest_handling(x, y, db))
dispatcher.add_handler(quest_handler)

updater.start_polling()
