#!/usr/bin/env python3

import questable
import sqlite3
import errors
from flask import Flask, jsonify, request

app = Flask(__name__)
db = sqlite3.connect("questable.db", check_same_thread=False)


# Returns the player object if valid token
def get_player(db):
    try:
        token = request.args['token']
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
    return jsonify({
            "xp": player.get_points(),
            "quests_completed": len(player.get_quests()),
            "total_quests": len(player.get_quests(None)),
            "side_quests_completed": len(player.get_side_quests()),
            "total_side_quests": len(player.get_side_quests(None)),
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
        qid = request.args['qid']
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
        qid = request.args['id']
    except(KeyError):
        return jsonify(errors._400), 400

    side_quest = player.get_side_quest(qid)
    if side_quest is False:
        return jsonify(errors._404), 404
    return jsonify(dictify_quest(side_quest))


app.add_url_rule('/get_side_quest', '/get_side_quest',
                 lambda: get_side_quest(db), methods=['GET'])
