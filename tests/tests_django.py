from __future__ import print_function

import json
import os

from faker import Faker
from nose.tools import eq_
from rest_framework import status
from rest_framework.test import APITestCase

fake = Faker()

import django

from halolib.util import Util
from halolib.apis import ApiTest
from halolib.exceptions import ApiError
from halolib.logs import log_json
from halolib import saga
from halolib.models import AbsModel

# from django.conf import settings
# settings.configure(default_settings=settings, DEBUG=True)
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()


class TestDjangoTestCase(APITestCase):
    """
    Tests /users detail operations.
    """

    def setUp(self):
        self.url = 'http://127.0.0.1:8000/?abc=def'
        self.perf_url = 'http://127.0.0.1:8000/perf'

    def mock_request(self, type, header={}):
        from django.test.client import RequestFactory
        rf = RequestFactory()
        if type == 'GET':
            get_request = rf.get('/hello/', **header)
            return get_request
        else:
            post_request = rf.post('/submit/', {'foo': 'bar'}, **header)
            return post_request

    def test_get_request_returns_a_given_string(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(json.loads(response.content), {'data': {'test': 'good'}})

    def test_api_request_returns_a_given_string(self):
        request = self.mock_request('GET')
        api = ApiTest(Util.get_req_context(request))
        timeout = Util.get_timeout(request)
        response = api.get(timeout)
        print("google response " + str(response.content))
        eq_(response.status_code, status.HTTP_200_OK)

    def test_api_request_returns_a_fail(self):
        request = self.mock_request('GET')
        api = ApiTest(Util.get_req_context(request))
        api.url = api.url + "/lgkmlgkhm??l,mhb&&,g,hj "
        timeout = Util.get_timeout(request)
        try:
            response = api.get(timeout)
        except ApiError as e:
            eq_(e.status_code, status.HTTP_404_NOT_FOUND)

    def test_send_event(self):
        from halolib.events import AbsBaseEvent
        class Event1Event(AbsBaseEvent):
            target_service = 'func1'
            key_name = 'def'
            key_val = '456'

        event = Event1Event()
        dict = {"name": "david"}
        response = event.send_event(dict)
        print("event response " + str(response))
        eq_(response, 'sent event')

    def test_system_debug_enabled(self):
        os.environ['DEBUG_LOG'] = 'true'
        flag = 'false'
        for i in range(0, 60):
            ret = Util.get_system_debug_enabled()
            print(ret)
            if ret == 'true':
                flag = ret
        eq_(flag, 'true')

    def test_debug_enabled(self):
        header = {'HTTP_DEBUG_LOG_ENABLED': 'true'}
        req = self.mock_request('GET', header)
        ret = Util.get_req_context(req)
        eq_(ret["debug-log-enabled"], 'true')

    def test_json_log(self):
        import traceback
        header = {'HTTP_DEBUG_LOG_ENABLED': 'true'}
        req = self.mock_request('GET', header)
        req_context = Util.get_req_context(req)
        try:
            raise Exception("test it")
        except Exception as e:
            e.stack = traceback.format_exc()
            ret = log_json(req_context, {"abc": "def"}, err=e)
            print(str(ret))
            eq_(ret["debug-log-enabled"], 'true')

    def test_get_request_with_debug(self):
        header = {'HTTP_DEBUG_LOG_ENABLED': 'true'}
        req = self.mock_request('GET', header)
        ret = Util.get_debug_enabled(req)
        eq_(ret, 'true')

    def test_debug_event(self):
        event = {'debug-log-enabled': 'true'}
        ret = Util.get_correlation_from_event(event)
        eq_(Util.event_req_context["debug-log-enabled"], 'true')
        ret = Util.get_correlation_from_event(event)
        eq_(ret["debug-log-enabled"], 'true')

    def test_pref_mixin(self):
        response = self.client.get(self.perf_url)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_model_get_pre(self):
        from pynamodb.attributes import UTCDateTimeAttribute, UnicodeAttribute
        class TestModel(AbsModel):
            class Meta:
                table_name = 'tbl-upc-53-loc'
                host = "http://localhost:8600"

            created_on = UTCDateTimeAttribute(null=False)
            pkey = UnicodeAttribute(hash_key=True)

        m = TestModel()
        a, b = m.get_pre()
        eq_(a, "pkey")

    def test_model_get_pre_val(self):
        from pynamodb.attributes import UTCDateTimeAttribute, UnicodeAttribute
        class TestModel(AbsModel):
            class Meta:
                table_name = 'tbl-upc-53-loc'
                host = "http://localhost:8600"

            created_on = UTCDateTimeAttribute(null=False)
            pkey = UnicodeAttribute(hash_key=True)

        m = TestModel()
        m.pkey = "123"
        a, b = m.get_pre_val()
        eq_(a, "123")

    def test_model_idem_id(self):
        from pynamodb.attributes import UTCDateTimeAttribute, UnicodeAttribute
        class TestModel(AbsModel):
            class Meta:
                table_name = 'tbl-upc-53-loc'
                host = "http://localhost:8600"

            created_on = UTCDateTimeAttribute(null=False)
            pkey = UnicodeAttribute(hash_key=True)

        m = TestModel()
        m.pkey = "456"
        ret = m.get_idempotent_id("123")
        eq_(ret, "8b077e79d995ac82ea9217c7b34c8b57")

    def test_model_idem_db(self):
        from pynamodb.attributes import UTCDateTimeAttribute, UnicodeAttribute
        from pynamodb.exceptions import PutError
        import datetime
        import uuid
        class TestModel(AbsModel):
            class Meta:
                table_name = 'tbl-upc-53-tst'
                host = "http://localhost:8600"

            created_on = UTCDateTimeAttribute(null=False)
            pkey = UnicodeAttribute(hash_key=True)

        if not TestModel.exists():
            TestModel.create_table(read_capacity_units=1, write_capacity_units=1)
        m = TestModel()
        m.pkey = str(uuid.uuid4())
        m.created_on = datetime.datetime.utcnow()
        request_id = str(uuid.uuid4())
        ret = m.save(request_id)
        try:
            ret1 = m.save(request_id)
        except PutError as e:
            print(str(e))
            ret1 = ret
        eq_(ret, ret1)

    def test_load_saga(self):
        with open("saga.json") as f:
            jsonx = json.load(f)
        with open("schema.json") as f1:
            schema = json.load(f1)
        sagax = saga.load_saga("test", jsonx, schema)
        eq_(len(sagax.actions), 6)

    def test_run_saga(self):
        response = self.client.put(self.url)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_rollback_saga(self):
        response = self.client.post(self.url)
        eq_(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_ssm(self):
        from halolib.ssm import get_app_config
        ret = get_app_config("us-east-1")
        print(str(ret.get_param("halolib")))
        eq_(ret.get_param("halolib")["url"], 'https://127.0.0.1:8000/loc')

    def test_error_handler(self):
        response = self.client.delete(self.url)
        eq_(json.loads(response.content)['error']['message'], 'test error msg')
        eq_(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_timeout(self):
        os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "halolib"
        request = self.mock_request('GET')
        timeout = Util.get_timeout(request)
        eq_(timeout, 0.3)

    def test_timeout_mili(self):
        class Ctx:
            def get_remaining_time_in_millis(self):
                return 5500

        ctx = Ctx()
        os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "halolib"
        request = self.mock_request('GET', {"context": ctx})
        timeout = Util.get_timeout(request)
        eq_(timeout, 5.0)
