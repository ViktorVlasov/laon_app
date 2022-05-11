from flask import Flask, redirect, url_for, request, render_template, session
from wtform_fields import *
from models import *

app = Flask(__name__)
app.secret_key = 'replace later'

# Configure database
app.config['SQLALCHEMY_DATABASE_URI']=''
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route("/", methods=['GET', 'POST'])
def index():

    reg_form = RegistrationForm()

    # Update database if validation success
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data

        user_object = User.query.filter_by(username=username).first()
        if user_object:
            return "Someone else has taken this username"

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return "INSERT INTO DB"
        # Hash password
        # hashed_pswd = pbkdf2_sha256.hash(password)

        # Add username & hashed password to DB
        # user = User(username=username, hashed_pswd=hashed_pswd)
        # db.session.add(user)
        # db.session.commit()

        # flash('Registered successfully. Please login.', 'success')
        # return redirect(url_for('login'))

    return render_template("index.html", form=reg_form)

if __name__ == '__main__':
    app.run(debug=True)

