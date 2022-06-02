from flask import Flask, redirect, url_for, request, render_template, session, flash, json
from flask_login import LoginManager, login_user, current_user, logout_user


from wtform_fields import *
from models import *

app = Flask(__name__)
app.secret_key = 'replace later'

# Configure database
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://lxwvizyttgkgqf:8bb45888158e3468b011f6742ea3a84c91494679be1155bc5ff58e0aa72f5bf2@ec2-54-228-125-183.eu-west-1.compute.amazonaws.com:5432/d7eb449u08v2c7'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize login manager
login = LoginManager(app)
login.init_app(app)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/", methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('decks'))

    reg_form = RegistrationForm()

    # Update database if validation success
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data
        # Hash password
        hashed_pswd = pbkdf2_sha256.hash(password)

        # add user with hashed password to db
        user_object = User(username=username, password=hashed_pswd)
        db.session.add(user_object)
        db.session.commit()

        flash('Registered successfully. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template("index.html", form=reg_form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('decks'))


    login_form = LoginForm()

    # Allow login if validation success
    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username=login_form.username.data).first()
        login_user(user_object)
        return redirect(url_for('decks'))

    return render_template("login.html", form=login_form)


@app.route("/decks", methods=['GET', 'POST'])
def decks():
    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for('login'))

    deck_form = DeckForm()
    user_id = int(current_user.get_id())

    if (request.method == "POST") and deck_form.validate_on_submit():
        deck_name = deck_form.deck_name.data

        # add deck_name with user_id to db
        deck_object = Deck(deck_name=deck_name, user_id=user_id)
        db.session.add(deck_object)
        db.session.commit()
        flash(f'Deck with name {deck_name} created.', 'success')
        # return render_template("decks.html", form=deck_form)

    user_decks = [deck.deck_name for deck in User.query.get(user_id).decks]

    # Способ отобразить колоды
    # print(User.query.get(3).decks[0].deck_name)
    return render_template("decks.html", form=deck_form, user_decks=user_decks)

@app.route("/delete", methods=['POST'])
def delete():
    # Delete deck
    if request.form.get('delete'):
        deck_name = request.form.get('delete')
        deck_object = Deck.query.filter_by(deck_name=deck_name).first()
        # print()

        u = db.session.get(Deck, deck_object.id)
        db.session.delete(u)
        db.session.commit()
        # return "test"
        return redirect(url_for('decks'))

@app.route("/add", methods=['GET', 'POST'])
def add():
    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for('login'))

    note_form = NoteForm()
    user_id = int(current_user.get_id())

    if (request.method == "POST") and note_form.validate_on_submit():
        # get data from request and fill the field
        front = note_form.front.data
        back = note_form.back.data
        deck_name = request.form.get('deck_name')
        deck_id = Deck.query.filter_by(deck_name=deck_name).first().id
        type_note = request.form.get('type_note')
        date = None
        # print(f"front={front}, back={back}, deck_id={deck_id}, type_note={type_note}, date={date}")

        # add note to db
        note_object = Note(front=front, back=back, deck_id=deck_id, type_note=type_note, repeat_date=date)
        db.session.add(note_object)
        db.session.commit()
        flash(f'Note for {deck_name} created.', 'success')
        # return render_template("add.html", form=note_form)

    print(User.query.get(user_id).decks)
    user_decks = [deck.deck_name for deck in User.query.get(user_id).decks]

    # Способ отобразить колоды
    # print(User.query.get(3).decks[0].deck_name)
    # return render_template("decks.html", form=deck_form, user_decks=user_decks)

    return render_template("add.html", form=note_form, user_decks=user_decks)

@app.route("/user/<string:name_deck>", methods=['GET', 'POST'])
def uniq_deck(name_deck):
    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for('login'))

    deck_id = Deck.query.filter_by(deck_name=name_deck).first().id
    notes = Note.query.filter_by(deck_id=deck_id).all()
    notes_front = [note.front for note in notes]

    return render_template("uniq_deck.html", notes_front=notes_front, Deck_name=name_deck)

@app.route("/learn", methods=['GET', 'POST'])
def learn():
    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for('login'))

    if request.method == "POST":
        name_deck = request.form.get('deck_name')
        deck_id = Deck.query.filter_by(deck_name=name_deck).first().id
        notes = Note.query.filter_by(deck_id=deck_id).all()
        notes_front = [note.front for note in notes]
        notes_back = [note.back for note in notes]

        return render_template("learn_deck.html", notes_front=notes_front, notes_back=notes_back, Deck_name=name_deck)

    user_id = int(current_user.get_id())
    user_decks = [deck.deck_name for deck in User.query.get(user_id).decks]

    return render_template("learn.html", user_decks=user_decks)

@app.route("/logout", methods=['GET'])
def logout():
    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for('login'))

    # Logout user
    logout_user()
    flash('You have logged out successfully', 'success')
    return redirect(url_for('login'))

def get_notes_value(name_deck):
    deck_id = Deck.query.filter_by(deck_name=name_deck).first().id
    notes = Note.query.filter_by(deck_id=deck_id).all()
    notes_front = [note.front for note in notes]
    notes_back = [note.back for note in notes]
    return (notes_front, notes_back)

@app.route('/get_note_start', methods=['GET', 'POST'])
def get_note_start():
    print(request.form)

    name_deck = request.form.get('deck_name')
    notes_front, notes_back = get_notes_value(name_deck)

    return json.dumps({'notes_front': notes_front[0],
                       'notes_back': notes_back[0],
                       'notes_len': len(notes_front)})

@app.route('/get_note_next', methods=['GET', 'POST'])
def get_note_next():
    name_deck = request.form.get('deck_name')
    note_number_next = int(request.form.get('note_number')) + 1
    notes_front, notes_back = get_notes_value(name_deck)

    if note_number_next >= len(notes_front):
        note_number_next = len(notes_front) - 1

    return json.dumps({'notes_front': notes_front[note_number_next],
                      'notes_back': notes_back[note_number_next],
                       'notes_number': note_number_next})


@app.route('/get_note_prev', methods=['GET', 'POST'])
def get_note_prev():
    name_deck = request.form.get('deck_name')
    note_number_prev = int(request.form.get('note_number')) - 1
    if note_number_prev < 0:
        note_number_prev = 0
    notes_front, notes_back = get_notes_value(name_deck)

    return json.dumps({'notes_front': notes_front[note_number_prev],
                      'notes_back': notes_back[note_number_prev],
                       'notes_number': note_number_prev})



if __name__ == '__main__':
    app.run(debug=True)

