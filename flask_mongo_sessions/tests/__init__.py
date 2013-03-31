from __future__ import with_statement

import itertools
import unittest
import uuid
import re
import time
from datetime import timedelta

import test_apps


class ZeroConfCase(unittest.TestCase):
    def __init__(self, db_interface, *args, **kwargs):
        super(ZeroConfCase, self).__init__(*args, **kwargs)
        self._db_interface = db_interface

    def setUp(self):
        self.app = test_apps.create_app(self._db_interface)   
        self.client = self.app.test_client()

    def tearDown(self):
        # with self.app.app_context():
        #     self.app.mongo.db.command('dropDatabase')
        pass

    def _test_with_sid(self, sid):
        test_data = "This_is_a_test_data."
        self.client.set_cookie(self.app.config['SERVER_NAME'],
                               key='session',
                               value=sid)
        r = self.client.get('/set?d='+test_data)
        cookies = [h[1] for h in r.headers 
                   if h[0]=='Set-Cookie' and h[1].startswith('session=')]
        session = next(iter(cookies), None)
        self.assertTrue(session)
        m = re.search('session=(\w{32})', session)
        self.assertTrue(m)
        returned_sid = m.group(1)

        self.client.set_cookie(self.app.config['SERVER_NAME'],
                               key='session',
                               value=returned_sid)
        r = self.client.get('/get')
        self.assertEquals(r.data, test_data)

    def test_new_session(self):
        self._test_with_sid(None)

    def test_empty_sid(self):
        self._test_with_sid('')

    def test_invalid_sid(self):
        self._test_with_sid('invalid')
        
    def test_valid_nonexistent_sid(self):
        self._test_with_sid(uuid.uuid4().hex)

    # def runTest(self):
    #     for m in self.__dict__:
    #         if m.startswith('test_'):
    #             self.__dict__[m]()


class ExpirationCase(unittest.TestCase):
    def __init__(self, db_interface, *args, **kwargs):
        super(ExpirationCase, self).__init__(*args, **kwargs)
        self._db_interface = db_interface

    def setUp(self):
        self.app = test_apps.create_app(self._db_interface)   
        self.client = self.app.test_client()
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=5)

#     def tearDown(self):
#         # with self.app.app_context():
#         #     self.app.mongo.db.command('dropDatabase')
#         pass

    def _test_with_sleep(self, data_in, data_out, sleep_period):
        r = self.client.get('/setpermanent?d='+data_in)
        cookies = [h[1] for h in r.headers 
                   if h[0]=='Set-Cookie' and h[1].startswith('session=')]
        session = next(iter(cookies), None)
        self.assertTrue(session)
        m = re.search('session=(\w{32})', session)
        self.assertTrue(m)
        returned_sid = m.group(1)

        time.sleep(sleep_period)

        self.client.set_cookie(self.app.config['SERVER_NAME'],
                               key='session',
                               value=returned_sid)
        r = self.client.get('/get')
        self.assertEquals(r.data, data_out)

    def test_expiring(self):
        self._test_with_sleep(data_in="This_is_a_test_data.",
                              data_out="",
                              sleep_period=5)

    def test_not_expiring(self):
        data = "This_is_a_test_data."
        self._test_with_sleep(data_in=data,
                              data_out=data,
                              sleep_period=3)

def suite():
    test_loader = unittest.TestLoader()
    suite = test_loader.suiteClass()
    for interface in ['pymongo']:
        for cls in ZeroConfCase, ExpirationCase:
            args = [(interface, x) for x in test_loader.getTestCaseNames(cls)]
            suite.addTests(itertools.starmap(cls, args))
    return suite

if __name__ == '__main__':
    unittest.main()
