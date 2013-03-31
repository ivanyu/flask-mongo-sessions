from flask import Flask
from flask import request
from flask import session

from flask.ext.pymongo import PyMongo
from flask.ext.mongoengine import MongoEngine

from flask_mongo_sessions import MongoDBSessionInterface

def create_app(db_interface):
    app = Flask('testapp')
    app.config['SERVER_NAME'] = 'localhost:5000'

    if db_interface == 'pymongo':
        app.config['MONGO_DBNAME'] = '__test-db__'
        mongo = PyMongo(app)
        with app.app_context():
            app.session_interface = MongoDBSessionInterface(
                app, mongo.db, 'sessions')
    elif db_interface == 'mongoengine':
        return None
        app.config['MONGODB_DB'] = '__test-db__'

    @app.route("/set")
    def set_session():
        session['data'] = request.args['d']
        return 'data'

    @app.route("/setpermanent")
    def set_permanent_session():
        session.permanent = True
        session['data'] = request.args['d']
        return 'data'

    @app.route("/get")
    def get_session():
        return session.get('data', '')

    return app

if __name__ == "__main__":
    app = create_app('pymongo')
    app.run(debug=True)
