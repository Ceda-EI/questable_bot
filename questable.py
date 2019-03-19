import uuid


class base_quest():
    TABLE = None

    def __init__(self, db, chat_id, qid, name=None, imp=None, diff=None,
                 state=None):
        self.DB = db
        self.CHAT_ID = chat_id
        self.name = name
        self.QID = qid
        self.imp = imp
        self.diff = diff
        self.state = state

    def add_to_db(self):
        cursor = self.DB.cursor()
        query = (f'INSERT INTO {self.TABLE}(chat_id, qid, name, importance'
                 ', difficulty, state) values(?, ?, ?, ?, ?, ?)')
        cursor.execute(query, (self.CHAT_ID, self.QID, self.name, self.imp,
                               self.diff, self.state))
        self.DB.commit()

    def update_db(self):
        cursor = self.DB.cursor()
        query = (f'UPDATE {self.TABLE} SET name=?, importance=?, difficulty=?,'
                 ' state=? WHERE chat_id=? AND qid=?')
        cursor.execute(query, (self.name, self.imp, self.diff,
                               self.state, self.CHAT_ID, self.QID))
        self.DB.commit()

    def get_from_db(self):
        cursor = self.DB.cursor()
        query = (f'SELECT name, importance, difficulty, state FROM '
                 f'{self.TABLE} where chat_id=? AND qid=?')
        cursor.execute(query, (self.CHAT_ID, self.QID))
        output = cursor.fetchone()
        self.name, self.imp, self.diff, self.state = output

    def delete_from_db(self):
        cursor = self.DB.cursor()
        query = (f'DELETE FROM {self.TABLE} WHERE chat_id=? AND qid=?')
        cursor.execute(query, (self.CHAT_ID, self.QID))
        self.DB.commit()

    def __str__(self):
        return f"{self.QID}: {self.name}"


class quest(base_quest):
    TABLE = "quests"


class side_quest(base_quest):
    TABLE = "side_quests"


def get_quest(db, chat_id, qid):
    q = quest(db, chat_id, qid)
    q.get_from_db()
    return q


def add_quest(db, chat_id, qid, name=None, imp=None, diff=None,
              state=None):
    q = quest(db, chat_id, qid, name, imp, diff, state)
    q.add_to_db()
    return q


def get_side_quest(db, chat_id, qid):
    q = side_quest(db, chat_id, qid)
    q.get_from_db()
    return q


def add_side_quest(db, chat_id, qid, name=None, imp=None, diff=None,
                   state=None):
    q = side_quest(db, chat_id, qid, name, imp, diff, state)
    q.add_to_db()
    return q


class player():
    def __init__(self, db, chat_id):
        self.DB = db
        self.CHAT_ID = chat_id
        cursor = self.DB.cursor()
        cursor.execute('SELECT * FROM state WHERE chat_id = ?', (chat_id,))
        row = cursor.fetchone()
        if not row:
            cursor.execute('INSERT INTO state(chat_id, state, extra) '
                           'VALUES(?,?,?)', (chat_id, 'none', 0))
            db.commit()
        cursor.execute('SELECT * FROM points WHERE chat_id = ?', (chat_id,))
        row = cursor.fetchone()
        if not row:
            cursor.execute('INSERT INTO points(chat_id, points) VALUES(?,?)',
                           (chat_id, 0))
            db.commit()

    def get_state(self):
        cursor = self.DB.cursor()
        query = 'SELECT state, extra FROM state WHERE chat_id=?'
        cursor.execute(query, (self.CHAT_ID,))
        output = cursor.fetchone()
        return {"state": output[0], "extra": output[1]}

    def set_state(self, state, extra=0):
        cursor = self.DB.cursor()
        query = 'UPDATE state SET state=?, extra=? WHERE chat_id=?'
        cursor.execute(query, (state, extra, self.CHAT_ID))
        self.DB.commit()

    def get_points(self):
        cursor = self.DB.cursor()
        query = 'SELECT points FROM points WHERE chat_id=?'
        cursor.execute(query, (self.CHAT_ID,))
        output = cursor.fetchone()
        return int(output[0])

    def add_points(self, points):
        new_points = self.get_points() + points
        cursor = self.DB.cursor()
        query = 'UPDATE points SET points=? WHERE chat_id=?'
        cursor.execute(query, (new_points, self.CHAT_ID))
        self.DB.commit()

    def get_quests(self, state=0):
        cursor = self.DB.cursor()
        query = ('SELECT chat_id, qid, name, importance, difficulty, '
                 'state FROM quests WHERE chat_id = ?')
        if state is not None:
            query += ' AND state = ?'
            cursor.execute(query, (self.CHAT_ID, state))
        else:
            cursor.execute(query, (self.CHAT_ID,))
        quests = []
        for row in cursor:
            q = quest(self.DB, *row)
            quests.append(q)
        return quests

    def get_side_quests(self, state=0):
        cursor = self.DB.cursor()
        query = ('SELECT chat_id, qid, name, importance, difficulty, '
                 'state FROM side_quests WHERE chat_id = ?')
        if state is not None:
            query += ' AND state = ?'
            cursor.execute(query, (self.CHAT_ID, state))
        else:
            cursor.execute(query, (self.CHAT_ID,))
        quests = []
        for row in cursor:
            q = side_quest(self.DB, *row)
            quests.append(q)
        return quests

    def get_quest(self, qid):
        cursor = self.DB.cursor()
        query = ('SELECT chat_id, qid, name, importance, difficulty, '
                 'state FROM quests WHERE chat_id = ? AND qid = ?')
        cursor.execute(query, (self.CHAT_ID, qid))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return quest(self.DB, *row)

    def get_side_quest(self, qid):
        cursor = self.DB.cursor()
        query = ('SELECT chat_id, qid, name, importance, difficulty, '
                 'state FROM side_quests WHERE chat_id = ? AND qid = ?')
        cursor.execute(query, (self.CHAT_ID, qid))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return side_quest(self.DB, *row)

    def get_tokens(self):
        cursor = self.DB.cursor()
        query = ('SELECT token FROM tokens WHERE chat_id=?')
        cursor.execute(query, (self.CHAT_ID,))
        tokens = list(map(lambda x: x[0], cursor))
        return tokens

    def add_token(self):
        cursor = self.DB.cursor()
        token = str(uuid.uuid4())
        query = ('INSERT INTO tokens(chat_id, token) values(?, ?)')
        cursor.execute(query, (self.CHAT_ID, token))
        self.DB.commit()
        return token

    def delete_token(self, token):
        cursor = self.DB.cursor()
        query = ('DELETE FROM tokens WHERE chat_id = ? AND token = ?')
        cursor.execute(query, (self.CHAT_ID, token))
        self.DB.commit()


def get_player_from_token(db, token):
    cursor = db.cursor()
    query = "SELECT chat_id FROM tokens WHERE token=?"
    cursor.execute(query, (token,))
    chat_id = cursor.fetchone()
    if chat_id is None:
        return False
    else:
        return player(db, chat_id[0])
