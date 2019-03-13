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
