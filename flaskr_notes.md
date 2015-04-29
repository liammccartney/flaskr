# User Stories
1. Let the user sign in adn out w/ credentials specified in config
    - only one user supported
2. When logged in user can add new entries on the page
3. page shows all entries so far in reverse order

will be using SQLite3 directly
larger applications require SQLAlchemy to handl db connections more intelligently

## Step 0: Creating folders
```
/flaskr
    /static
    /templates
```
_flaskr_ folder is **not** a python package
will drop db schema and main module into folder directly
files inside of _static_ are availabel to users of app via HTTP
    a place for CSS and JS files
_template_ where Flask will look for Jinja2 templates

## Step 1: Db Schema
using a single table - _entries_

## Step 2: Application Setup Code
w/ schema in place, time for app module: _flaskr.py_
`from_object()` will look at the given object (if string, imports) and then look for all uppercase variables defined there
    in our case the config we wrote a few liens of code above
        this could have been a separate file

usually it is a good idea to load a config from a configurable file
`from_envar()` is for this
```python
app.config.from_envvar('FLASKR_SETTINGS', silent=True`
```
this lets us set an environment variable called **`FLASKR_SETTINGS`** to specify a config file to be loaded
the silent switch tells Flask to not complain if no environment key is set
the *secret_key* is needed to keep client-side sessions secure
NEVER LEAVE DEBUG MODE ACTIVATED IN A PRODUCTION SYSTEM

we add a method `connect_db()` to easily connect to the config's specific db

## Step 3: Creating the Database
Flaskr is a db powered app - powered by a relational db system
need to pipe schema.sql into sqlite3
good idea to add a function to do this for you
requires `contextlib.closing()`
'closing()' helper function allows ut to keep a conenct open for the duration of the *with* block
`open_resource()` method supports that function aout of the box, so it can be used in the *with* block directly
    this function opens a file from the resouece location and allows you to read from it
    we are using it to execute a script on the db connection

when we connect we get an object (we're calling it db) th can give us a cursor
    on that cursor is a method to execute a complete script
    then we have to commit changes (SQLite3 does not commit implictly)
now it is possible to create a db by starting up a Python shell and importing an calling that function
```python
from flaskr import init_db
init_db()
```
## Step 4: Request Db Connections
we will need the db connectionin al our functions so it makes sense to init them befor each request
Flask provies `before_request()`, `after_request()`, `teardown_request()` decorators
```python
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
```
Functions marked with `before_request()` are called before a req and passed no arguments
Functions marked `after_request()` called after a req and passed the response that will be sent to the client
    they have to return that response object or a differentone
    they are not guaranteed to executed if an exception is raised
`teardown_request()` - get called after ther esponse has been constructed
    they are not allowed to modify the request and their return values are ignored
    if an exception occurred while the request was being processed, it is passed ot each function
        otherwise *None* is passed in.
