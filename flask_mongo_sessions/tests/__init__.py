from __future__ import with_statement

import unittest
import uuid
import re
import time
from datetime import timedelta

import test_apps


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = test_apps.create_app(self._get_db_interface())
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

        session = cookies[0] if cookies else None
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
        session = cookies[0] if cookies else None
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


class MultipleAppsCase(unittest.TestCase):
    def setUp(self):
        self.app1 = test_apps.create_app(
            self._get_db_interface(), 'testapp1', '__test-db__')
        self.app2 = test_apps.create_app(
            self._get_db_interface(), 'testapp2', '__test-db__')
        self.app3 = test_apps.create_app(
            self._get_db_interface(), 'testapp3', '__another-test-db__')
        self.client1 = self.app1.test_client()
        self.client2 = self.app2.test_client()
        self.client3 = self.app3.test_client()

    def test_multiapp(self):
        sid1 = uuid.uuid4().hex
        sid2 = uuid.uuid4().hex
        sid3 = uuid.uuid4().hex

        test_data1 = "This_is_a_test_data_for_app_1."
        test_data2 = "This_is_a_test_data_for_app_2."
        test_data3 = "This_is_a_test_data_for_app_3."
        self.client1.set_cookie(self.app1.config['SERVER_NAME'],
                                key='session',
                                value=sid1)
        self.client2.set_cookie(self.app2.config['SERVER_NAME'],
                                key='session',
                                value=sid2)
        self.client3.set_cookie(self.app3.config['SERVER_NAME'],
                                key='session',
                                value=sid3)
        r1 = self.client1.get('/set?d='+test_data1)
        r2 = self.client2.get('/set?d='+test_data2)
        r3 = self.client3.get('/set?d='+test_data3)
        cookies1 = [h[1] for h in r1.headers
                    if h[0] == 'Set-Cookie' and h[1].startswith('session=')]
        cookies2 = [h[1] for h in r2.headers
                    if h[0] == 'Set-Cookie' and h[1].startswith('session=')]
        cookies3 = [h[1] for h in r3.headers
                    if h[0] == 'Set-Cookie' and h[1].startswith('session=')]
        session1 = cookies1[0] if cookies1 else None
        session2 = cookies2[0] if cookies2 else None
        session3 = cookies3[0] if cookies3 else None
        self.assertTrue(session1)
        self.assertTrue(session2)
        self.assertTrue(session3)
        m = re.search('session=(\w{32})', session1)
        self.assertTrue(m)
        returned_sid1 = m.group(1)
        m = re.search('session=(\w{32})', session2)
        self.assertTrue(m)
        returned_sid2 = m.group(1)
        m = re.search('session=(\w{32})', session3)
        self.assertTrue(m)
        returned_sid3 = m.group(1)

        self.client1.set_cookie(self.app1.config['SERVER_NAME'],
                                key='session',
                                value=returned_sid1)
        self.client2.set_cookie(self.app2.config['SERVER_NAME'],
                                key='session',
                                value=returned_sid2)
        self.client3.set_cookie(self.app3.config['SERVER_NAME'],
                                key='session',
                                value=returned_sid3)
        r1 = self.client1.get('/get')
        r2 = self.client2.get('/get')
        r3 = self.client3.get('/get')
        self.assertEquals(r1.data, test_data1)
        self.assertEquals(r2.data, test_data2)
        self.assertEquals(r3.data, test_data3)


def suite():
    test_loader = unittest.TestLoader()
    suite = test_loader.suiteClass()
    for interface in ['mongoengine', 'pymongo']:
        for base in [ZeroConfCase, ExpirationCase, MultipleAppsCase]:
            def wrapper_get_db_interface(i):
                return lambda self: i
            name = '%s_%s' % (base.__name__, interface)
            attrs = {'_get_db_interface': wrapper_get_db_interface(interface)}
            cls = type(name, (base,), attrs)
            args = test_loader.getTestCaseNames(cls)
            suite.addTests(map(cls, args))
    return suite
