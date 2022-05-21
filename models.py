from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """ User model """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)


class Deck(db.Model):
    """ Deck model """

    __tablename__ = "decks"
    id = db.Column(db.Integer, primary_key=True)
    deck_name = db.Column(db.String(25), unique=True, nullable=False)
    user_id = db.Column(db.ForeignKey(User.id))
    user_decks = db.relationship(User, backref='decks')
    deck_notes = db.relationship("Note", cascade="all, delete-orphan", backref='notes')


class Note(db.Model):
    """ Note model """

    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    front = db.Column(db.String(200), nullable=False)
    back = db.Column(db.String(200), nullable=False)
    deck_id = db.Column(db.ForeignKey(Deck.id))
    type_note = db.Column(db.String(20), nullable=False)
    repeat_date = db.Column(db.DateTime(timezone=False), nullable=True)
