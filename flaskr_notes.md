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
