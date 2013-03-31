from __future__ import with_statement

import unittest
import uuid
import re
import time
from datetime import timedelta

import test_apps


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = test_apps.create_app(self._db_interface)
        self.client = self.app.test_client()


class ZeroConfCase(BaseTestCase):
    def _test_with_sid(self, sid):
        test_data = "This_is_a_test_data."
        self.client.set_cookie(self.app.config['SERVER_NAME'],
                               key='session',
                               value=sid)
        r = self.client.get('/set?d='+test_data)
        cookies = [h[1] for h in r.headers
                   if h[0] == 'Set-Cookie' and h[1].startswith('session=')]
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


class ExpirationCase(BaseTestCase):
    def setUp(self):
        super(ExpirationCase, self).setUp()
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=5)

    def _test_with_sleep(self, data_in, data_out, sleep_period):
        r = self.client.get('/setpermanent?d='+data_in)
        cookies = [h[1] for h in r.headers
                   if h[0] == 'Set-Cookie' and h[1].startswith('session=')]
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
    for interface in ['pymongo', 'mongoengine']:
        for base in [ZeroConfCase, ExpirationCase]:
            def __init__(self, *args, **kwargs):
                self._db_interface = interface
                super(self.__class__, self).__init__(*args, **kwargs)
            name = '{0}_{1}'.format(base.__name__, interface)
            cls = type(name, (base,), {'__init__': __init__})
            args = test_loader.getTestCaseNames(cls)
            suite.addTests(map(cls, args))
    return suite
