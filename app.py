from flask import Flask, url_for
import dotenv
import os
from flask.ext.sqlalchemy import SQLAlchemy
from flask_ldap3_login import LDAP3LoginManager
from flask_login import LoginManager, login_user, UserMixin, current_user, logout_user
from flask import render_template_string, redirect
from flask.ext.ldap3_login.forms import LDAPLoginForm
import pdb

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

@app.route('/')
def home():
    # Redirect users who are not logged in.
    if not current_user or current_user.is_anonymous():
        return redirect(url_for('login'))

    # User is logged in, so show them a page with their cn and dn.
    template = """
    <h1>Welcome: {{ current_user.data.cn }}</h1>
    <h2>{{ current_user.dn }}</h2>
    """

    return render_template_string(template)


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
