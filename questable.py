from datetime import datetime


class base_quest():
    TABLE = None

    def __init__(self, db, chat_id, qid, name=None, imp=None, diff=None,
                 state=None, date=None):
        self.DB = db
        self.CHAT_ID = chat_id
        self.name = name
        self.QID = qid
        self.imp = imp
        self.diff = diff
        self.state = state
        if date:
            if isinstance(date, datetime):
                self.date = date
            else:
                self.date = datetime.fromtimestamp(date)
        else:
            date = None

    def add_to_db(self):
        cursor = self.DB.cursor()
        query = (f'INSERT INTO {self.TABLE}(chat_id, qid, name, importance'
                 ', difficulty, date, state) values(?, ?, ?, ?, ?, ?, ?)')
        cursor.execute(query, (self.CHAT_ID, self.QID, self.name, self.imp,
                               self.diff, self.date, self.state))
        self.DB.commit()

    def update_db(self):
        cursor = self.DB.cursor()
        query = (f'UPDATE {self.TABLE} SET name=?, importance=?, difficulty=?,'
                 ' date=?, state=? WHERE chat_id=? AND qid=?')
        cursor.execute(query, (self.name, self.imp, self.diff, self.date,
                               self.state, self.CHAT_ID, self.QID))
        self.DB.commit()

    def get_from_db(self):
        cursor = self.DB.cursor()
        query = (f'SELECT name, importance, difficulty, date, state FROM '
                 '{self.TABLE} where chat_id=? AND qid=?')
        cursor.execute(query, self.CHAT_ID, self.QID)
        output = cursor.fetchone()
        self.name, self.imp, self.diff, self.date, self.state = output


class quest(base_quest):
    TABLE = "quests"


class side_quest(base_quest):
    TABLE = "side_quests"


def get_quest(db, chat_id, qid):
    q = quest(db, chat_id, qid)
    q.get_from_db()
    return q


def add_quest(self, db, chat_id, qid, name=None, imp=None, diff=None,
              state=None, date=None):
    q = quest(self, db, chat_id, qid, name, imp, diff, state, date)
    q.add_to_db()
    return q


def get_side_quest(db, chat_id, qid):
    q = side_quest(db, chat_id, qid)
    q.get_from_db()
    return q


def add_side_quest(self, db, chat_id, qid, name=None, imp=None, diff=None,
                   state=None, date=None):
    q = side_quest(self, db, chat_id, qid, name, imp, diff, state, date)
    q.add_to_db()
    return q
