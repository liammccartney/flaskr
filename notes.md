# What does hello.py do?
- imports Flask class
    - and instance of this class will be our Web Server Gateway Interface (WSGI)
- creats an instance of class Flask called app
    - first argument is the name of the application's module or package. 
    - if you're using a single module (like here) use __name__ because if it is started as an application or an important module the name will be different (__main__ v the actual import name)
- route() decorator tells Flask what url should trigger our function
- the funciton is given a name, which is also used to generate URLs for the particular function and returns the message we want to display the user's browswer.
- finally: we use the run() function to run the local serve with our application
    - `if __name__ == '__main__':` makes sure the server only runs if the script is executed directly from the Python interpreter and not used as an imported module'

## Debug Mode
allows for the server to reload on code changes
provides debugger
````python
app.debug = True
app.run()
#OR
app.run(debug=True)
```
**this should never be used on production machines**

## Routing
use the route decorator to bind a function to a URL
### Variable Rules
to add variable parts ot a URL use angle brackets
`/user/<username>`
```python
@app.route('/user/<username>')
def show_user_profile(username):
    #show the user profile for that user
    return 'User %s' % username
```
this allows you to pass parameters from the URL to the method attached at that URL
You can convert these values using syntax:
`/post/<int:post_id>`
Converters:
    - int
    - float
    - path
### Unique URLs / Redirection Behavior
Flask URL rules based on Werkzeugs routing module
Trailing slashes matter
`/about != /about/`
### URL Building
Flask can generate URLs
use `url_for()` to build a URL for a specific function
syntax:
```
@app.route('/user/<username>')
def profile(username): pass
# then
url_for('profile', username='Liam') #=> /user/Liam

### HTTP Methods
a route only knows how to respond to a GET by default
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'Post':
        do_the_login()
    else:
        show_the_login_form()
```
allows you to conditionally handle kinds of requests of the same url

## Static Files
ideally your web server is configured to serve static files for you, but during development Flask can do this
create a folder called static in the package, or next to the module, and it will be available at /static ont he application
`url_for('static', filename='style.css')`

## Rendering Templates
Jinja2 template enginer
use `render_template()` method
    provide templat name and locals you need inside
example template:
```html
<!doctype html>
<title>Hello from Flask</title>
{% if name %}
    <h1>Hello {{name}}!</h1>
{% else %}
    <h1>Hello World!</h1>
{% endif %}
```
inside a template you have acess to `request`, `session`, and `g` objects as well as `get_flashed_messages()` function
Templaes are useful if inheritance is used
    possible to keep certain elements on each page
Automatic escaping is enabled
    if a variable evaluated containes HTML, it will be escaped properly

## Accessing Request Data
data sent to the server is provided by the global `request` object
### Context Locals
    certain objects in Flask are global
        actually proxies to objects that are local to a specific context
    in testing you have to bind a request object yourself
        `test_request_context()` allows you to do so
        ```python
        from flask import request
        with app.test_request_context('/hello', method='POST'):
            #now you can do something with the request until the
            #end of the with block, suck as basic assertions
            assert request.path == '/hello'
            assert request.method == 'POST'
        ```
    you can also pass the whole WSGI envrionemtn to `request_context()` method
        ```python
        from flask import request
        with app.requst_context(environ):
            assert request.method == 'POST'
        ```
## The Request Object
`from flask import request`
the current request method is available by using the **method** attribute
to access form data (from POST or PUT) use the **form** attribute
```python
@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method was GET or credentials invalid
    return render_template('login.html', error=error)
```
If an attribute does not exist on `request` then a special `KeyError` is raised, if you do not catch it HTTP 400 Bad Request error page is shown instead
#### Query Parameters
use the `args` attribute on `request`
`searchword = request.args.get('key', '')`

### Cookies
use the `cookies` attribute
use  `set_cookie` method of response objects
the `cookies` attribute is a dictionary wth all the cookies the client transmits
if you want to use sessions, do not use the cookies directly, instead use the Sessions in Flask that add security on top of cookies

## Redirects and Errors
use `redirect()` method
user `abort()` to abour a request early with an error code
```python
from flask import abor, redirect, url_for
@app.route('/')
def index():
    return redirect(url_for('login'))
@app.route('/login')
def login('/login')
def login():
    abort(401)
    this_is_never_executed()
```
=> this is example how how redirect works, even if it is basically meaningless

you can use `errorhandler()` decorator to customize your error pages
```python
from flask import render_template

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
```

## About Responses
the return value from a view function is automatically converted into a response object
ie: if the return value is a string it is converted into a response object with the string as the response body, a 200 OK error code, and a text/html mimetype
    1. if a resposne object of the correct type is returned, it is directly return from the view
    2. if it is a string, a response object is created with that data and the default params
    3. if a tuple is returned the items in thet ype can provide extra info
        - format: `(response, status, headers)`
        - _status_ value will override the status code
        - _headers_ can be a list or dictionary of additional header values
    4. if none of that works, Flask will assume the return value is a valid WSGI app and convert it to a response object

if you want a view's response object use `make_response()`'

## Sessions
`session` object exists in addition to the `request` object
allows you to store information specific to a user from one request to the next
implemented on top of cookies, cryptographically
requires a secret key
```python
from flask import Flask, session, redirect, url_for, escape, request

app = Flask(__name_)

@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST']
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
        '''

@app.route('/logout')
def logout():
    #remove the username from the session if it is there
    session.pop('username', None)
    return redirect(url_for('index'))

app.secret_key = 'ABCDEFGHI123'
```

### How to generate good secret keys:
your operating system has wasy to generate pretty random stuff
```python
import os
os.urandom(24)
```

Flask takes values you put into the session object and serialize them into a cookie
If you find things not persisting, ensure the cookie size is supported by the browser

## Message Flashing
the flashing system basically makes it possible to record a message at the end of a request and access it on the next (and only the next) request
Usually combined with a layout template to expose the message
use `flash()` to get a hold of messages you can use `get_flashed_messages()`
both available in the templates


