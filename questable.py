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
