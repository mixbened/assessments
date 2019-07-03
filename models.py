import os
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite"))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, unique=True)
    session_token = db.Column(db.String)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    test_id = db.Column(db.String, db.ForeignKey('tests.id'))
    questions_total = db.Column(db.Integer)
    questions_correct = db.Column(db.Integer)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)
    a1 = db.Column(db.String)
    a2 = db.Column(db.String)
    a3 = db.Column(db.String)
    correct = db.Column(db.String)
    test_id = db.Column(db.String, db.ForeignKey('tests.id'))
    def asdict(self):
        return {
            "id": self.id,
            "title": self.title,
            "a1": self.a1,
            "a2": self.a2,
            "a3": self.a3,
            "correct": self.correct,
            "test_id": self.test_id
        }

