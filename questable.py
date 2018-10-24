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


class quest(base_quest):
    TABLE = "quests"


class side_quest(base_quest):
    TABLE = "side_quests"
