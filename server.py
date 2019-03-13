#!/usr/bin/env python3

import questable
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
db = sqlite3.connect("questable.db", check_same_thread=False)


# /auth.
def auth(db):
    success = jsonify({"success": True})
    failure = jsonify({"success": False})
    try:
        token = request.args['token']
    except (AttributeError):
        return failure
    except (KeyError):
        return failure
    if questable.get_player_from_token(db, token) is False:
        return failure
    else:
        return success


app.add_url_rule('/auth', '/auth', lambda: auth(db), methods=['GET'])
