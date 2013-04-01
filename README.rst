flask-mongo-sessions
====================

.. module:: flask-mongo-sessions

flask-mongo-sessions helps you to add server-side sessions to `Flask`_ with
`MongoDB`_ storage.

Requirements
------------

The extensions requires Flask>=0.8 and also `PyMongo`_ (`Flask-PyMongo`_)
or `MongoEngine`_ (`Flask-MongoEngine`_)

Tested with Python 2.5, 2.6 and 2.7.

Installation
------------

Installation of the extension is easy::

    $ pip flask-mongo-sessions

or::

    $ easy_install install flask-mongo-sessions

or::

    $ python setup.py install


Usage
-----

To work, the extension needs PyMongo's *Database* object and sessions
collection name. The object can be taken from PyMongo:

.. code-block:: python

    from flask import Flask
    from flask.ext.pymongo import PyMongo
    from flask.ext.mongo_sessions import MongoDBSessionInterface

    app = Flask(__name__)
    app.config['MONGO_DBNAME'] = 'database-name'
    mongo = PyMongo(app)
    with app.app_context():
        app.session_interface = MongoDBSessionInterface(app, mongo.db, 'sessions')

or from MongoEngine:

.. code-block:: python

    from flask import Flask
    from flask.ext.mongoengine import MongoEngine
    from flask.ext.mongo_sessions import MongoDBSessionInterface

    app = Flask(__name__)
    app.config['MONGODB_DB'] = 'database-name'
    db = mongo.connection[app.config['MONGODB_DB']]
    app.session_interface = MongoDBSessionInterface(app, db, 'sessions')

All connection parameters (address, port, etc.) must be set for the respective
extension.

Users sessions will be stored in the specified MongoDB database in
the collection with specified name.

Authors and contributors
------------------------
The project is started and maintained by Ivan Yurchenko
(ivan0yurchenko@gmail.com).


License
-------
MIT license (see *LICENSE* file)


Also
----

Please, send me a feedback about the app (bugs, examples of usage etc.)


.. _Flask: http://flask.pocoo.org/
.. _MongoDB: http://www.mongodb.org/
.. _PyMongo: https://github.com/mongodb/mongo-python-driver
.. _Flask-PyMongo: https://github.com/dcrosta/flask-pymongo/
.. _MongoEngine: http://mongoengine.org/
.. _Flask-MongoEngine: https://github.com/MongoEngine/flask-mongoengine
