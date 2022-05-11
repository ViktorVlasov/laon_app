from flask import Flask, redirect, url_for, request, render_template, session
from wtform_fields import *
from models import *

app = Flask(__name__)
app.secret_key = 'replace later'

# Configure database
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://cbbydgxbphirfb:8561383db67f859da3fa51809c2d6a3f27970a8e6e46ccffe5a2a713ddf54b06@ec2-63-32-248-14.eu-west-1.compute.amazonaws.com:5432/dd6qsh2q8nbr1e'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route("/", methods=['GET', 'POST'])
def index():

    reg_form = RegistrationForm()

    # Update database if validation success
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data
        # Hash password
        hashed_pswd = pbkdf2_sha256.hash(password)

        # add user with hashed password to db
        user = User(username=username, password=hashed_pswd)
        db.session.add(user)
        db.session.commit()

        # flash('Registered successfully. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template("index.html", form=reg_form)

@app.route("/login", methods=['GET', 'POST'])
def login():

    login_form = LoginForm()

    # Allow login if validation success
    if login_form.validate_on_submit():
        # user_object = User.query.filter_by(username=login_form.username.data).first()
        # login_user(user_object)
        return "Success logged!"
        # return redirect(url_for('chat'))

    return render_template("login.html", form=login_form)

if __name__ == '__main__':
    app.run(debug=True)

