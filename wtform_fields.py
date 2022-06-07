from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError

from passlib.hash import pbkdf2_sha256
from models import User, Deck


def invalid_credentials(form, field):
    """ Username and password checker """

    password = field.data
    username = form.username.data

    # Check username is invalid
    user_data = User.query.filter_by(username=username).first()
    if user_data is None:
        raise ValidationError("Username or password is incorrect")
    # Check password in invalid
    elif not pbkdf2_sha256.verify(password, user_data.password):
        raise ValidationError("Username or password is incorrect")


class RegistrationForm(FlaskForm):
    """ Registration form"""

    username = StringField('username', validators=[InputRequired(message="Username required"),
                                           Length(min=4, max=25, message="Username must be between 4 and 25 characters")])
    password = PasswordField('password', validators=[InputRequired(message="Password required"),
                                         Length(min=4, max=25, message="Password must be between 4 and 25 characters")])
    confirm_pswd = PasswordField('confirm_pswd', validators=[InputRequired(message="Password required"),
                                         EqualTo('password', message="Passwords must match")])

    def validate_username(self, username):
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists. Select a different username.")


class LoginForm(FlaskForm):
    """ Login form """

    username = StringField('username', validators=[InputRequired(message="Username required")])
    password = PasswordField('password', validators=[InputRequired(message="Password required"), invalid_credentials])


class DeckForm(FlaskForm):
    """ Form for create deck """

    deck_name = StringField('deck_name', validators=[InputRequired(message="Deck name required"), Length(min=1, max=25, message="Deck name must be between 1 and 25 characters")])
    def validate_deck_name(self, deck_name):
        user_object = Deck.query.filter_by(deck_name=deck_name.data).first()
        if user_object:
            raise ValidationError("Deck name already exists. Select a different deck name.")


class NoteForm(FlaskForm):
    """ Form for create note """

    # type = StringField('type', validators=[InputRequired(message="Type name required"), Length(min=1, max=20, message="Type must be between 1 and 20 characters")])
    # deck_name = StringField('deck_name', validators=[InputRequired(message="Deck name required"), Length(min=1, max=25, message="Deck name must be between 1 and 25 characters")])
    front = StringField('front', validators=[InputRequired(message="Front required"), Length(min=1, max=200, message="Front must be between 1 and 200 characters")])
    back = StringField('back', validators=[InputRequired(message="Back required"), Length(min=1, max=200, message="Back must be between 1 and 200 characters")])
