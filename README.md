flask-mongo-sessions
====================

Server-side sessions for Flask with MongoDB.

Works with Python 2.5, 2.6 and 2.7

Installation
------------

The extension can be installed with *setup.py*:

    python setup.py install

Or with *pip*:

    pip install flask-mongo-sessions

Usage
-----

The usage is pretty simple. The extension class is init by PyMongo Database
object and the sessions collection name.
Database object can be taken from *PyMongo*:

    from flask import Flask
    from flask.ext.pymongo import PyMongo
    from flask.ext.mongo_sessions import MongoDBSessionInterface

    app = Flask(__name__)
    app.config['MONGO_DBNAME'] = 'database-name'
    mongo = PyMongo(app)
    with app.app_context():
        app.session_interface = MongoDBSessionInterface(app, mongo.db, 'sessions')

or from *MongoEngine*:

    from flask import Flask
    from flask.ext.mongoengine import MongoEngine
    from flask.ext.mongo_sessions import MongoDBSessionInterface

    app = Flask(__name__)
    app.config['MONGODB_DB'] = 'database-name'
    db = mongo.connection[app.config['MONGODB_DB']]
    app.session_interface = MongoDBSessionInterface(app, db, 'sessions')

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
