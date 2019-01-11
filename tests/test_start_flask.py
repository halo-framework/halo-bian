from __future__ import print_function

import json

from faker import Faker
from nose.tools import eq_

fake = Faker()

import unittest


# settings.configure(default_settings=settings, DEBUG=True)
# app = FlaskAPI(__name__)
# app.config.from_object('settings')


class TestUserDetailTestCase(unittest.TestCase):
    """
    Tests /users detail operations.
    """

    def setUp(self):
        self.url = 'http://127.0.0.1:8000/?abc=def'
        self.perf_url = 'http://127.0.0.1:8000/perf'
        from app import create_app
        app = create_app()
        app.run(debug=False, use_reloader=False, host='127.0.0.1', port=8000, threaded=True)

    def test(self):
        tester = app.test_client()
        response = tester.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(json.loads(response.content), {"test": "good"})
