flask-mongo-sessions
====================

Server-side sessions for Flask with MongoDB.

Installation
------------

The extension can be installed with *setup.py*:

    python setup.py install

Or with *pip*:

    pip install flask-mongo-sessions

Usage
-----

The usage is pretty simple:

    from flask import Flask
    from flask.ext.pymongo import PyMongo
    from flask.ext.mongo_sessions import MongoDBSessionInterface

    app = Flask(__name__)
    mongo = PyMongo(app)
    session_collection = 'session'
    app.session_interface = MongoDBSessionInterface(mongo, session_collection)

Other
-----

### License

**MIT License**  
See *LICENSE* file.

### Contributors

Project initially started by Ivan Yurchenko (ivan 0 yurchenko [at] gmail [dot]
com)

### Also

Please, send me a feedback about the app (bugs, examples of usage etc.)
