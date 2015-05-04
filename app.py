from flask import Flask, request, render_template_string, redirect, render_template
import requests
import dotenv
import os
from flask.ext.sqlalchemy import SQLAlchemy
from flask_ldap3_login import LDAP3LoginManager
from flask_login import LoginManager, login_user, UserMixin, current_user, logout_user
from flask.ext.ldap3_login.forms import LDAPLoginForm

from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup

import operator
import re
import nltk

dotenv.load_dotenv(".env")

app = Flask(__name__)
db = SQLAlchemy(app)

from models import Result

app.config['APP_SETTINGS'] = os.environ.get('APP_SETTINGS')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['DEBUG'] = os.environ.get('DEBUG')

app.config['LDAP_HOST'] = os.environ.get('LDAP_HOST')
app.config['LDAP_BASE_DN'] = os.environ.get('LDAP_BASE_DN')

app.config['LDAP_USER_RDN_ATTR'] = os.environ.get('LDAP_USER_RDN_ATTR')
app.config['LDAP_USER_LOGIN_ATTR'] = os.environ.get('LDAP_USER_LOGIN_ATTR')
app.config['LDAP_BIND_USER_DN'] = os.environ.get('LDAP_BIND_USER_DN')
app.config['LDAP_BIND_USER_PASSWORD'] = os.environ.get('LDAP_BIND_USER_PASSWORD')
app.config['LDAP_USER_SEARCH_SCOPE'] = os.environ.get('LDAP_USER_SEARCH_SCOPE')
login_manager = LoginManager(app)
ldap_manager = LDAP3LoginManager(app)
users = {}

# Declare an Object Model for the user, and make it comply with the
# flask-login UserMixin mixin.
class User(UserMixin):
    def __init__(self, dn, username, data):
        self.dn = dn
        self.username = username
        self.data = data

    def __repr__(self):
        return self.dn

    def get_id(self):
        return self.dn

    def is_anonymous(self):
        return False


# Declare a User Loader for Flask-Login.
# Simply returns the User if it exists in our 'database', otherwise
# returns None.
@login_manager.user_loader
def load_user(id):
    if id in users:
        return users[id]
    return None


# Declare The User Saver for Flask-Ldap3-Login
# This method is called whenever a LDAPLoginForm() successfully validates.
# Here you have to save the user, and return it so it can be used in the
# login controller.
@ldap_manager.save_user
def save_user(dn, username, data, memberships):
    user = User(dn, username, data)
    users[dn] = user
    return user

@app.route('/', methods=['GET', 'POST'])
def home():
    # Redirect users who are not logged in.
    # if not current_user or current_user.is_anonymous():
        # return redirect(url_for('login'))

    # User is logged in, so show them a page with their cn and dn.
    errors = []
    results = {}
    if request.method == "POST":
        # get url that the person has entered
        try:
            url = request.form['url']
            r = requests.get(url)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
            return render_template('index.html', errors=errors)
        if r:

            # text processing
            raw = BeautifulSoup(r.text).get_text()
            nltk.data.path.append('./nltk_data/')  # set the path
            tokens = nltk.word_tokenize(raw)
            text = nltk.Text(tokens)

            # remove punctuation, count raw words
            nonPunct = re.compile('.*[A-Za-z].*')
            raw_words = [w for w in text if nonPunct.match(w)]
            raw_word_count = Counter(raw_words)

            # stop words
            no_stop_words = [w for w in raw_words if w.lower() not in stops]
            no_stop_words_count = Counter(no_stop_words)

            # save the results
            results = sorted(
                no_stop_words_count.items(),
                key=operator.itemgetter(1),
                reverse=True
            )[:10]
            try:
                result = Result(
                    url=url,
                    result_all=raw_word_count,
                    result_no_stop_words=no_stop_words_count
                )
                db.session.add(result)
                db.session.commit()
            except:
                errors.append("Unable to add item to database.")
    return render_template('index.html', errors=errors, results=results)

@app.route('/login', methods=['GET', 'POST'])
def login():
    template = """
    {{ get_flashed_messages() }}
    {{ form.errors }}
    <form method="POST">
        <label>Username{{ form.username() }}</label>
        <label>Password{{ form.password() }}</label>
        {{ form.submit() }}
        {{ form.hidden_tag() }}
    </form>
    """

    # Instantiate a LDAPLoginForm which has a validator to check if the user
    # exists in LDAP.
    form = LDAPLoginForm()

    if form.validate_on_submit():
        # Successfully logged in, We can now access the saved user object
        # via form.user.
        login_user(form.user) # Tell flask-login to log them in.
        return redirect('/')  # Send them home

    return render_template_string(template, form=form)
@app.route('/logout')
def logout():
    logout_user()

    return redirect('/')

if __name__ == '__main__':
    app.run()
