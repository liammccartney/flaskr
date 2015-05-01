from flask import Flask, url_for
import dotenv
import os
from flask_ldap3_login import LDAP3LoginManager
from flask_login import LoginManager, login_user, UserMixin, current_user, logout_user
from flask import render_template_string, redirect
from flask.ext.ldap3_login.forms import LDAPLoginForm
import pdb

dotenv.load_dotenv(".env")
app = Flask(__name__)
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
