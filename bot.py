#!/usr/bin/env python3

import logging
import telegram
import sqlite3
import questable
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
        RegexHandler
import signal
import sys
import re
import button_groups

try:
    import config
except ImportError:
    print("Missing Config. Exiting.")
    exit()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
                    %(message)s', level=logging.INFO)


def escape_html(message):
    return re.sub("<", "&lt;",
                  re.sub("&", "&amp;", message))


def start(bot, update):
    chat_id = update.message.chat_id
    if update.message.chat.type == "private":
        name = str(update.message.from_user.first_name)
        if update.message.from_user.last_name:
            name += " " + str(update.message.from_user.last_name)
    else:
        name = update.message.chat.title
    text = f"Hello {name}!\n" + \
        "Welcome to Questable. To get started, check /help."
    custom_keyboard = button_groups.main
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
    if update.message.chat.type == "private":
        reply_markup = telegram.ReplyKeyboardRemove()
    else:
        reply_markup = telegram.ForceReply()
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
    custom_keyboard = button_groups.difficulty
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


def add_diff(bot, update, player, type, qid):
    message = update.message.text.lower()
    chat_id = update.message.chat_id
    if message in ["low", "???? low", "l"]:
        diff = 1
    elif message in ["medium", "???? medium", "m"]:
        diff = 2
    elif message in ["high", "???? high", "h"]:
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
    custom_keyboard = button_groups.importance
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


def add_imp(bot, update, player, type, qid):
    message = update.message.text.lower()
    chat_id = update.message.chat_id
    if message in ["low", "???? low", "l"]:
        imp = 1
    elif message in ["medium", "???? medium", "m"]:
        imp = 2
    elif message in ["high", "???? high", "h"]:
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

    text = {"quest": "Quest", "side_quest": "Side Quest"}[type] + " Added!"
    bot.send_message(chat_id=chat_id, text=text)
    send_status(bot, update, player)


def send_status(bot, update, player, prefix=""):
    if update.message.chat.type == "private":
        name = str(update.message.from_user.first_name)
        if update.message.from_user.last_name:
            name += " " + str(update.message.from_user.last_name)
    else:
        name = update.message.chat.title
    name = escape_html(name)
    points = player.get_points()
    total_quests = len(player.get_quests(None))
    completed_quests = len(player.get_quests(1))
    total_side_quests = len(player.get_side_quests(None))
    completed_side_quests = len(player.get_side_quests(1))

    text = (prefix + f'<b>???? {name}</b>\n'
            f'<b>???? XP:</b> {points}\n'
            f'<b>?????? Quests:</b> {completed_quests}/{total_quests}\n'
            f'<b>???? Side Quests:</b> {completed_side_quests}/'
            f'{total_side_quests}\n')
    chat_id = update.message.chat_id
    custom_keyboard = button_groups.main
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
    if len(x) == 0:
        text = ("<b>You have completed every " +
                {"quest": "quest", "side_quest": "side quest"}[type] +
                " ever known to me.</b>")
    else:
        text = ("<b>" + {"quest": "????", "side_quest": "????"}[type] +
                " List of " + {"quest": "Quests", "side_quest":
                               "Side Quests"}[type] + "</b>")
    x.sort(key=lambda i: (i.imp, -i.QID), reverse=True)
    imp = 3
    for i in x:
        if i.imp <= imp:
            text += "\n\n<b>???? " + ["Low", "Medium", "High"][i.imp-1]
            text += "</b>"
            imp = i.imp - 1
        if type == "quest":
            text += f"\n/Q_{i.QID} {i.name}"
        else:
            text += f"\n/SQ_{i.QID} {i.name}"

    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML",
                     disable_web_page_preview=True)


def quest(bot, update, player, qid, type):
    try:
        if type == "quest":
            x = questable.get_quest(player.DB, player.CHAT_ID, qid)
        elif type == "side_quest":
            x = questable.get_side_quest(player.DB, player.CHAT_ID, qid)
    except Exception:
        chat_id = update.message.chat_id
        text = ("<b>?????? Could not find " +
                {"quest": "Quest", "side_quest": "Side Quest"}[type] + "</b>")
        bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        return

    text = ("<b>???? " + {"quest": "Quest", "side_quest": "Side Quest"}[type]
            + f":</b> {x.name}"
            "\n<b>???? Priority:</b> " + ["Low", "Medium", "High"][x.imp-1]
            + "\n<b>" + ["????", "????", "????"][x.diff-1] + " Difficulty:</b> "
            + ["Low", "Medium", "High"][x.diff-1]
            + "\n<b>" + ["???", "???"][x.state] + " Status:</b> "
            + ["Incomplete", "Complete"][x.state])

    if x.state == 1:
        player.set_state('bo', 0)
        custom_keyboard = [["Back"]]
    elif x.state == 0:
        state = {"quest": "eq", "side_quest": "esq"}[type]
        player.set_state(state, qid)
        custom_keyboard = button_groups.quests(type)
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML",
                     reply_markup=reply_markup)


def quest_handling(bot, update, db):
    text = update.message.text.lower().split("@")[0].split("_")
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
    send_status(bot, update, player, f"<b>???? Earned {points} XP</b>\n\n")
    chat_id = update.message.chat_id
    custom_keyboard = button_groups.main
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
        text = "<b>?????? Updated Name</b>"
    elif target == "imp":
        message = message.lower()
        if message in ["low", "???? low", "l"]:
            x.imp = 1
        elif message in ["medium", "???? medium", "m"]:
            x.imp = 2
        elif message in ["high", "???? high", "h"]:
            x.imp = 3
        else:
            bot.send_message(chat_id=chat_id, text="Invalid Option")
            return
        text = "<b>?????? Updated Priority</b>"
    elif target == "diff":
        message = message.lower()
        if message in ["low", "???? low", "l"]:
            x.diff = 1
        elif message in ["medium", "???? medium", "m"]:
            x.diff = 2
        elif message in ["high", "???? high", "h"]:
            x.diff = 3
        else:
            bot.send_message(chat_id=chat_id, text="Invalid Option")
            return
        text = "<b>?????? Updated Difficulty</b>"

    x.update_db()
    if type == "quest":
        player.set_state('eq', qid)
    elif type == "side_quest":
        player.set_state('esq', qid)
    custom_keyboard = [
            ["??? Mark as done"],
            ["???? Edit Name", "?????? Change Priority"],
            ["???? Change Difficulty", "???? Delete " +
                {"quest": "Quest", "side_quest": "Side Quest"}[type]],
            ["?????? Back"]]
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
    else:
        player.set_state('none', 0)


def help_command(bot, update, db):
    player = questable.player(db, update.message.chat_id)
    drop_state(bot, update, player)
    chat_id = update.message.chat_id
    custom_keyboard = button_groups.main
    text = ("*Questable Bot*\n\nQuestable is an RPG-like bot for maintaining "
            "events in real life. _Main Tasks_ are _Quests_ while _other "
            "tasks_ are _Side Quests._ You can use the bot to maintain a "
            "list of things you need to do. For completing each Quest/Side "
            "Quests you get XP based on how difficult and important the "
            "Quest/Side Quest was. Quests/Side Quests can be added and "
            "modified later.\n\n To get more help check "
            "[Extended Help](https://questable.webionite.com/help/) or "
            "[this video](https://t.me/quadnite/25). In case, of "
            "bugs/feedback/more help, contact @ceda\\_ei or join the "
            "[group](https://t.me/questable).")
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown",
                     reply_markup=reply_markup)


def rate_command(bot, update, db):
    player = questable.player(db, update.message.chat_id)
    drop_state(bot, update, player)
    chat_id = update.message.chat_id
    custom_keyboard = button_groups.main
    text = ("[Vote for us on Telegram Directory!](https://t.me/tgdrbot?"
            "start=questable_bot)\n\n"
            "Telegram Directory is a website that helps you discover top "
            "telegram channels, bots and groups.")
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown",
                     reply_markup=reply_markup)


def tokens(bot, update):
    custom_keyboard = button_groups.tokens
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    reply_text = ("Tokens are used to authenticate external "
                  "applications. This only provides access to "
                  "Questable data.\n"
                  "\nOfficial clients are:\n"
                  "[Questable CLI](https://gitlab.com/questable/questable-cli)"
                  )
    bot.send_message(chat_id=update.message.chat_id, text=reply_text,
                     reply_markup=reply_markup, parse_mode="markdown",
                     disable_web_page_preview=True)


def add_token(bot, update, player):
    custom_keyboard = button_groups.main
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    if len(player.get_tokens()) < 3:
        reply_text = player.add_token()
    else:
        reply_text = "Maximum number of tokens reached."
    bot.send_message(chat_id=player.CHAT_ID, text=reply_text,
                     reply_markup=reply_markup)


def delete_token(bot, update, player):
    tokens = player.get_tokens()
    custom_keyboard = list(map(lambda x: [x], tokens))
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    reply_text = "Choose token to remove."
    player.set_state("rt")
    bot.send_message(chat_id=update.message.chat_id, text=reply_text,
                     reply_markup=reply_markup)


def delete_token_rt(bot, update, player):
    player.delete_token(update.message.text.lower())
    custom_keyboard = button_groups.main
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    reply_text = "Token has been removed."
    player.set_state("none")
    bot.send_message(chat_id=player.CHAT_ID, text=reply_text,
                     reply_markup=reply_markup)


def list_tokens(bot, update, player):
    custom_keyboard = button_groups.main
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    reply_text = "???? List of tokens\n\n"
    reply_text += "\n".join(player.get_tokens())
    bot.send_message(chat_id=update.message.chat_id, text=reply_text,
                     reply_markup=reply_markup)


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
    # rt: Remove token

    if state["state"] == "none":
        if text in ["add quest", "?????? add quest", "aq"]:
            add_quest(bot, update, player)
        elif text in ["add side quest", "???? add side quest", "asq"]:
            add_quest(bot, update, player, "side_quest")
        elif text in ["list quests", "???? list quests", "lq"]:
            list_quests(bot, update, player, "quest")
        elif text in ["list side quests", "???? list side quests", "lsq"]:
            list_quests(bot, update, player, "side_quest")
        elif text in ["tokens", "???? tokens", "t"]:
            tokens(bot, update)
        elif text in ["list tokens", "???? list tokens", "lt"]:
            list_tokens(bot, update, player)
        elif text in ["generate token", "???? generate token", "gt"]:
            add_token(bot, update, player)
        elif text in ["delete token", "???? delete token", "dt"]:
            delete_token(bot, update, player)
        elif text == "ls":
            list_quests(bot, update, player, "side_quest")
            list_quests(bot, update, player, "quest")

        else:
            if update.message.chat.type == "private":
                send_status(bot, update, player)

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
        if text in ["back", "?????? back", "b"]:
            player.set_state('none', 0)
            send_status(bot, update, player)
        elif text in ["mark as done", "??? mark as done", "mad"]:
            mark_as_done(bot, update, player, state["extra"], "quest")
        elif text in ["edit name", "???? edit name", "en"]:
            player.set_state('eqn', state["extra"])
            text = "What shall the new name of the Quest be?"
            reply_markup = telegram.ReplyKeyboardRemove()
            bot.send_message(chat_id=player.CHAT_ID, text=text,
                             reply_markup=reply_markup)
        elif text in ["change priority", "?????? change priority", "cp"]:
            player.set_state('eqi', state["extra"])
            text = "How important is it?"
            custom_keyboard = button_groups.importance
            reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            bot.send_message(chat_id=player.CHAT_ID, text=text,
                             reply_markup=reply_markup)
        elif text in ["change difficulty", "???? change difficulty", "cd"]:
            player.set_state('eqd', state["extra"])
            text = "How difficult is it?"
            custom_keyboard = button_groups.difficulty
            reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            bot.send_message(chat_id=player.CHAT_ID, text=text,
                             reply_markup=reply_markup)
        elif text in ["delete quest", "???? delete quest", "dq"]:
            quest = questable.get_quest(db, player.CHAT_ID, state["extra"])
            quest.delete_from_db()
            drop_state(bot, update, player)
            prefix = f"<b>Quest {quest.name} has been deleted</b>\n\n"
            send_status(bot, update, player, prefix=prefix)
        else:
            if update.message.chat.type == "private":
                drop_state(bot, update, player)
                send_status(bot, update, player)

    elif state["state"] == "esq":
        if text in ["back", "?????? back", "b"]:
            player.set_state('none', 0)
            send_status(bot, update, player)
        elif text in ["mark as done", "??? mark as done", "mad"]:
            mark_as_done(bot, update, player, state["extra"], "side_quest")
        elif text in ["edit name", "???? edit name", "en"]:
            player.set_state('esqn', state["extra"])
            text = "What shall the new name of the Side Quest be?"
            reply_markup = telegram.ReplyKeyboardRemove()
            bot.send_message(chat_id=player.CHAT_ID, text=text,
                             reply_markup=reply_markup)
        elif text in ["change priority", "?????? change priority", "cp"]:
            player.set_state('esqi', state["extra"])
            text = "How important is it?"
            custom_keyboard = button_groups.importance
            reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            bot.send_message(chat_id=player.CHAT_ID, text=text,
                             reply_markup=reply_markup)
        elif text in ["change difficulty", "???? change difficulty", "cd"]:
            player.set_state('esqd', state["extra"])
            text = "How difficult is it?"
            custom_keyboard = button_groups.difficulty
            reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            bot.send_message(chat_id=player.CHAT_ID, text=text,
                             reply_markup=reply_markup)
        elif text in ["delete side quest", "???? delete side quest", "dsq"]:
            sq = questable.get_side_quest(db, player.CHAT_ID, state["extra"])
            sq.delete_from_db()
            drop_state(bot, update, player)
            prefix = f"<b>Side Quest {sq.name} has been deleted</b>\n\n"
            send_status(bot, update, player, prefix=prefix)
        else:
            if update.message.chat.type == "private":
                drop_state(bot, update, player)
                send_status(bot, update, player)

    elif state["state"] == "bo":
        if text == "back" or update.message.chat.type == "private":
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

    elif state["state"] == "rt":
        delete_token_rt(bot, update, player)
    else:
        if update.message.chat.type == "private":
            drop_state(bot, update, player)
            send_status(bot, update, player)


def sigterm_handler(signal, frame, db):
    db.close()
    sys.exit(0)


signal.signal(signal.SIGTERM, lambda x, y: sigterm_handler(x, y, db))

# Set up database and tables
db = sqlite3.connect("questable.db", check_same_thread=False)
cursor = db.cursor()
with open('schema.sql') as f:
    cursor.executescript(f.read())
db.commit()

updater = Updater(token=config.api_key, use_context=False)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('me', lambda x, y: me_handler(x, y, db)))
dispatcher.add_handler(CommandHandler('rate', lambda x, y:
                                      rate_command(x, y, db)))
dispatcher.add_handler(CommandHandler('cancel', lambda x, y: me_handler(x, y,
                                                                        db)))
dispatcher.add_handler(CommandHandler('help', lambda x, y: help_command(x, y,
                                                                        db)))
dispatcher.add_handler(RegexHandler(r"/[Ss]?[Qq]_\d+", lambda x, y:
                                    quest_handling(x, y, db)))
dispatcher.add_handler(MessageHandler(Filters.command, lambda x, y:
                                      message_handling(x, y, db)))
dispatcher.add_handler(MessageHandler(Filters.text, lambda x, y:
                                      message_handling(x, y, db)))

if config.update_method == "polling":
    updater.start_polling()
elif config.update_method == "webhook":
    updater.start_webhook(listen=config.webhook["listen"],
                          url_path=config.webhook["url_path"],
                          port=config.webhook["port"])
    updater.bot.set_webhook(url=config.webhook["url"])
