from flask import Flask
from flask import request
from flask import session

from flask.ext.pymongo import PyMongo

from flask_mongo_sessions import MongoDBSessionInterface


app = Flask('testapp')
app.config['SERVER_NAME'] = 'localhost:5000'
app.config['MONGO_DBNAME'] = '__test-db__'
mongo = PyMongo(app)
app.session_interface = MongoDBSessionInterface(mongo, 'sessions')

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


if __name__ == "__main__":
    app.run(debug=True)
