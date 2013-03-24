import pickle
import uuid
from datetime import datetime

from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionMixin
from flask.sessions import SessionInterface


class MongoDBSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, new=True):
        def on_update(this):
            this.modified = True
        if initial:
            initial = pickle.loads(initial)
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False

    def pickle(self):
        return pickle.dumps(dict(self))


class MongoDBSessionInterface(SessionInterface):
    session_class = MongoDBSession

    def __init__(self, mongo, collection_name):
        self._mongo = mongo
        self._collection_name = collection_name

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.__generate_sid()
            return self.session_class(sid=sid)

        doc = self.__get_collection().find_one({'_id': sid})
        if doc:
            session = self.session_class(initial=doc['d'], sid=sid)
        else:
            session = self.session_class(sid=sid)
        return session

    def save_session(self, app, session, response):
        cookie_domain = self.get_cookie_domain(app)
        cookie_path = self.get_cookie_path(app)
        cookie_exp = self.get_expiration_time(app, session)

        if not session:
            self.__get_collection().remove({'_id': session.sid})
            if session.modified:
                response.delete_cookie(key=app.session_cookie_name,
                                       path=cookie_path,
                                       domain=cookie_domain)
            return

        self.__get_collection().update(
            {'_id': session.sid},
            {'$set': {
                'd': session.pickle(),
                'cr': datetime.utcnow(),
            }},
            upsert=True)

        response.set_cookie(key=app.session_cookie_name,
                            value=session.sid,
                            expires=cookie_exp,
                            #path=cookie_path,
                            #domain=cookie_domain,
                            secure=self.get_cookie_secure(app),
                            httponly=self.get_cookie_httponly(app))

    def __get_collection(self):
        return self._mongo.db[self._collection_name]

    def __generate_sid(self):
        return uuid.uuid4().hex
