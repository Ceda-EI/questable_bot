#!/usr/bin/env python3

import questable
import sqlite3
import errors
from flask import Flask, jsonify, request, redirect

app = Flask(__name__)
db = sqlite3.connect("questable.db", check_same_thread=False)


# Returns the player object if valid token
def get_player(db):
    try:
        token = request.values['token']
    except (AttributeError):
        return False
    except (KeyError):
        return False
    return questable.get_player_from_token(db, token)


# /auth.
def auth(db):
    if get_player(db) is False:
        return jsonify({"success": False})
    else:
        return jsonify({"success": True})


app.add_url_rule('/auth', '/auth', lambda: auth(db), methods=['GET'])


# /player
def player(db):
    player = get_player(db)
    if player is False:
        return jsonify(errors._401), 401
    noq = len(player.get_quests(None))
    nosq = len(player.get_side_quests(None))
    return jsonify({
            "xp": player.get_points(),
            "quests_completed": noq - len(player.get_quests()),
            "total_quests": noq,
            "side_quests_completed": nosq - len(player.get_side_quests()),
            "total_side_quests": nosq,
            })


app.add_url_rule('/player', '/player', lambda: player(db), methods=['GET'])


def dictify_quest(quest):
    return {
            "id": quest.QID,
            "name": quest.name,
            "difficulty": quest.diff,
            "priority": quest.imp,
            "state": [False, True][quest.state]
            }


# /get_quests
def get_quests(db):
    player = get_player(db)
    if player is False:
        return jsonify(errors._401), 401
    quests = list(map(dictify_quest, player.get_quests()))
    return jsonify(quests)


app.add_url_rule('/get_quests', '/get_quests', lambda: get_quests(db),
                 methods=['GET'])


# /get_side_quests
def get_side_quests(db):
    player = get_player(db)
    if player is False:
        return jsonify(errors._401), 401
    side_quests = list(map(dictify_quest, player.get_side_quests()))
    return jsonify(side_quests)


app.add_url_rule('/get_side_quests', '/get_side_quests',
                 lambda: get_side_quests(db), methods=['GET'])


# /get_quest
def get_quest(db):
    player = get_player(db)
    if player is False:
        return jsonify(errors._401), 401
    try:
        qid = request.values['id']
    except(KeyError):
        return jsonify(errors._400), 400

    quest = player.get_quest(qid)
    if quest is False:
        return jsonify(errors._404), 404

    return jsonify(dictify_quest(quest))


app.add_url_rule('/get_quest', '/get_quest', lambda: get_quest(db),
                 methods=['GET'])


# /get_side_quest
def get_side_quest(db):
    player = get_player(db)
    if player is False:
        return jsonify(errors._401), 401
    try:
        qid = request.values['id']
    except(KeyError):
        return jsonify(errors._400), 400

    side_quest = player.get_side_quest(qid)

    if side_quest is False:
        return jsonify(errors._404), 404

    return jsonify(dictify_quest(side_quest))


app.add_url_rule('/get_side_quest', '/get_side_quest',
                 lambda: get_side_quest(db), methods=['GET'])


# /add_quest
def add_quest(db):
    player = get_player(db)
    if player is False:
        return jsonify(errors._401), 401

    x = player.get_quests(None)
    if len(x) == 0:
        qid = 1
    else:
        x.sort(key=lambda i: i.QID, reverse=True)
        qid = x[0].QID + 1

    try:
        name = request.values['name']
        imp = int(request.values['priority'])
        diff = int(request.values['difficulty'])
    except (KeyError):
        return jsonify(errors._400), 400
    except (ValueError):
        return jsonify(errors._400_bv), 400

    if imp not in [1, 2, 3] or diff not in [1, 2, 3]:
        return jsonify(errors._400_bv), 400

    quest = questable.add_quest(db, player.CHAT_ID, qid, name, imp, diff, 0)
    return jsonify(dictify_quest(quest))


app.add_url_rule('/add_quest', '/add_quest', lambda: add_quest(db),
                 methods=['POST'])


# /add_side_quest
def add_side_quest(db):
    player = get_player(db)
    if player is False:
        return jsonify(errors._401), 401

    x = player.get_side_quests(None)
    if len(x) == 0:
        qid = 1
    else:
        x.sort(key=lambda i: i.QID, reverse=True)
        qid = x[0].QID + 1

    try:
        name = request.values['name']
        imp = int(request.values['priority'])
        diff = int(request.values['difficulty'])
    except (KeyError):
        return jsonify(errors._400), 400
    except (ValueError):
        return jsonify(errors._400_bv), 400

    if imp not in [1, 2, 3] or diff not in [1, 2, 3]:
        return jsonify(errors._400_bv), 400

    quest = questable.add_side_quest(db, player.CHAT_ID, qid, name, imp,
                                     diff, 0)
    return jsonify(dictify_quest(quest))


app.add_url_rule('/add_side_quest', '/add_side_quest',
                 lambda: add_side_quest(db), methods=['POST'])


# /update_quest
def update_quest(db):
    player = get_player(db)
    if player is False:
        return jsonify(errors._401), 401
    try:
        qid = request.values['id']
    except(KeyError):
        return jsonify(errors._400), 400

    available_keys = [i for i in ['name', 'difficulty', 'priority', 'state']
                      if i in request.values.keys()]
    if len(available_keys) == 0:
        return jsonify(errors._400), 400
    quest = questable.get_quest(db, player.CHAT_ID, qid)

    if quest is False:
        return jsonify(errors._404), 404

    if quest.state == 1:
        return jsonify(dictify_quest(quest))

    for i in available_keys:
        try:
            if i == "name":
                quest.name = request.values["name"]
            elif i == "difficulty":
                diff = int(request.values["difficulty"])
                if diff in [1, 2, 3]:
                    quest.diff = diff
                else:
                    return jsonify(errors._400_bv), 400
            elif i == "priority":
                imp = int(request.values["priority"])
                if imp in [1, 2, 3]:
                    quest.imp = imp
                else:
                    return jsonify(errors._400_bv), 400
            elif i == "state":
                state = bool(request.values["state"])
                if state is True:
                    quest.state = 1
                    points = 55 + 10*quest.imp + 15*quest.diff
                    player.add_points(points)
                else:
                    return jsonify(errors._400_bv), 400
        except (ValueError):
            return jsonify(errors._400_bv), 400

    quest.update_db()
    return jsonify(dictify_quest(quest))


app.add_url_rule('/update_quest', '/update_quest', lambda: update_quest(db),
                 methods=['POST'])


# /update_side_quest
def update_side_quest(db):
    player = get_player(db)
    if player is False:
        return jsonify(errors._401), 401
    try:
        qid = request.values['id']
    except(KeyError):
        return jsonify(errors._400), 400

    available_keys = [i for i in ['name', 'difficulty', 'priority', 'state']
                      if i in request.values.keys()]
    if len(available_keys) == 0:
        return jsonify(errors._400), 400
    quest = questable.get_side_quest(db, player.CHAT_ID, qid)

    if quest is False:
        return jsonify(errors._404), 404

    if quest.state == 1:
        return jsonify(dictify_quest(quest))

    for i in available_keys:
        try:
            if i == "name":
                quest.name = request.values["name"]
            elif i == "difficulty":
                diff = int(request.values["difficulty"])
                if diff in [1, 2, 3]:
                    quest.diff = diff
                else:
                    return jsonify(errors._400_bv), 400
            elif i == "priority":
                imp = int(request.values["priority"])
                if imp in [1, 2, 3]:
                    quest.imp = imp
                else:
                    return jsonify(errors._400_bv), 400
            elif i == "state":
                state = bool(request.values["state"])
                if state is True:
                    quest.state = 1
                    points = 10*quest.imp + 15*quest.diff
                    player.add_points(points)
                else:
                    return jsonify(errors._400_bv), 400
        except (ValueError):
            return jsonify(errors._400_bv), 400

    quest.update_db()
    return jsonify(dictify_quest(quest))


app.add_url_rule('/update_side_quest', '/update_side_quest',
                 lambda: update_side_quest(db), methods=['POST'])


# /delete_quest
def delete_quest(db):
    player = get_player(db)
    if player is False:
        return jsonify(errors._401), 401
    try:
        qid = request.values['id']
    except(KeyError):
        return jsonify(errors._400), 400

    try:
        quest = questable.get_quest(db, player.CHAT_ID, qid)
    except Exception:
        return jsonify(errors._404), 404

    if quest.state == 1:
        return jsonify({"success": False})

    quest.delete_from_db()
    return jsonify({"success": True})


app.add_url_rule('/delete_quest', '/delete_quest',
                 lambda: delete_quest(db), methods=['DELETE'])


# /delete_side_quest
def delete_side_quest(db):
    player = get_player(db)
    if player is False:
        return jsonify(errors._401), 401
    try:
        qid = request.values['id']
    except(KeyError):
        return jsonify(errors._400), 400

    try:
        side_quest = questable.get_side_quest(db, player.CHAT_ID, qid)
    except Exception:
        return jsonify(errors._404), 404

    if side_quest.state == 1:
        return jsonify({"success": False})

    side_quest.delete_from_db()
    return jsonify({"success": True})


app.add_url_rule('/delete_side_quest', '/delete_side_quest',
                 lambda: delete_side_quest(db), methods=['DELETE'])


@app.route('/')
def redirect_to_docs():
    return redirect("https://questable.webionite.com/api", code=301)
