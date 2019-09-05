from __future__ import print_function

from faker import Faker
from flask import Flask, request
from requests.auth import *
from flask_restful import Api
import json
from halo_flask.exceptions import BadRequestError,ApiError
from halo_flask.flask.utilx import status
from halo_bian.bian.abs_bian_srv import AbsBianMixin
from halo_bian.bian.exceptions import BianException
from halo_flask.apis import AbsBaseApi
from halo_flask.flask.utilx import Util
from halo_bian.bian.bian import BusinessEvent,BianCategory,ActionTerms

import unittest

fake = Faker()
app = Flask(__name__)
api = Api(app)
app.config.from_object('settings')



class T1(AbsBianMixin):
    pass

class T2(AbsBianMixin):
    def validate_req(self, bian_request):
        print("in validate_req ")
        if bian_request:
            if "name" in bian_request.request.args:
                name = bian_request.request.args['name']
                if not name:
                    raise BadRequestError("missing value for query var name")
        return True

    def set_back_api(self,bian_request):
        print("in set_back_api ")
        class Api(AbsBaseApi):
            name = "Google"
        return Api(Util.get_req_context(bian_request.request))

    def set_api_headers(self, bian_request):
        print("in set_api_headers ")
        headers = {'Accept':'application/json'}
        return headers

    def set_api_vars(self, bian_request):
        print("in set_api_vars " + str(bian_request))
        ret = {}
        name = bian_request.request.args['name']
        if name:
            ret['name'] = name
        if bian_request:
            ret["bq"] = bian_request.behavior_qualifier
            ret["id"] = bian_request.cr_reference_id
        return ret

    def set_api_auth(self, bian_request):
        print("in set_api_auth ")
        user = ''
        pswd = ''
        return HTTPBasicAuth(user,pswd)

    def execute_api(self, bian_request, back_api, back_vars, back_headers,back_auth,back_data):
        print("in execute_api ")
        if back_api:
            timeout = Util.get_timeout(bian_request.request)
            try:
                back_api.set_api_url('ID',back_vars['name'])
                ret = back_api.get(timeout,headers=back_headers,auth=back_auth)
                return ret
            except ApiError as e:
                raise BianException(e)
        return None

    def extract_json(self, bian_request,back_response):
        print("in extract_json: "+str(back_response.status_code))
        if back_response:
            return json.loads(back_response.content)
        return json.loads("{}")

    def create_resp_payload(self, bian_request,back_json):
        print("in create_resp_payload " + str(back_json))
        if back_json:
            return self.map_from_json(back_json,{})
        return back_json

    def map_from_json(self,back_json,payload):
        print("in map_from_json")
        payload['name'] = back_json["title"]
        return payload

class MyBusinessEvent(BusinessEvent):
    pass


class Api(AbsBaseApi):
    name = "Google"

class T3(AbsBianMixin):
    filter_separator = "#"
    filter_key_values = {None: {'customer-reference-id': 'customerId','amount':'amount','user':'user','page_no':'page_no','count':'count'}}
    filter_chars = {None: ['=','>']}
    business_event = MyBusinessEvent("test event",BianCategory.DELEGATION, {1:Api})

    def do_retrieve_deposit(self, bian_request):
        print("in do_retrieve_deposit ")
        return self.do_retrieve_bq(bian_request)

    def do_execute_deposit(self, bian_request):
        print("in do_retrieve_deposit ")
        return self.do_execute_bq(bian_request)

    def validate_req_deposit(self, bian_request):
        print("in validate_req_deposit ")
        if bian_request:
            if "name" in bian_request.request.args:
                name = bian_request.request.args['name']
                if not name:
                    raise BadRequestError("missing value for query var name")
        return True

    def set_back_api_deposit(self,bian_request):
        print("in set_back_api_deposit ")
        return Api(Util.get_req_context(bian_request.request))

    def set_api_headers_deposit(self, bian_request):
        print("in set_api_headers_deposit ")
        headers = {'Accept':'application/json'}
        return headers

    def set_api_vars_deposit(self, bian_request):
        print("in set_api_vars_deposit " + str(bian_request))
        ret = {}
        name = None
        if 'name' in bian_request.request.args:
            name = bian_request.request.args['name']
        if name:
            ret['name'] = name
        if bian_request:
            ret["bq"] = bian_request.behavior_qualifier
            ret["id"] = bian_request.cr_reference_id
        return ret

    def set_api_auth_deposit(self, bian_request):
        print("in set_api_auth_deposit ")
        user = ''
        pswd = ''
        return HTTPBasicAuth(user,pswd)

    def execute_api_deposit(self, bian_request, back_api, back_vars, back_headers,back_auth,back_data):
        print("in execute_api_deposit ")
        if back_api:
            timeout = Util.get_timeout(bian_request.request)
            try:
                back_api.set_api_url('ID',back_vars['name'])
                ret = back_api.get(timeout,headers=back_headers,auth=back_auth)
                return ret
            except ApiError as e:
                raise BianException(e)
        return None

    def extract_json_deposit(self, bian_request,back_response):
        print("in extract_json_deposit: "+str(back_response.status_code))
        if back_response:
            return json.loads(back_response.content)
        return json.loads("{}")

    def create_resp_payload_deposit(self, bian_request,back_json):
        print("in create_resp_payload_deposit " + str(back_json))
        if back_json:
            return self.map_from_json_deposit(back_json,{})
        return back_json

    def map_from_json_deposit(self,back_json,payload):
        print("in map_from_json_deposit")
        payload['name'] = back_json["title"]
        return payload

    def set_resp_headers_deposit(self, bian_request,headers):
        return self.set_resp_headers(bian_request,headers)

from halo_flask.flask.viewsx import AbsBaseLinkX as AbsBaseLink,PerfLinkX as PerfLink
class S1(PerfLink):
    pass

class TestUserDetailTestCase(unittest.TestCase):
    """
    Tests /users detail operations.
    """

    # def setUp(self):
    # self.t1 = T1()

    def test_get_request_returns_a_given_string(self):
        with app.test_request_context('/?name=Peter'):
            self.t1 = T1()
            ret = self.t1.process_get(request, {})
            assert ret.code == status.HTTP_200_OK

    def test_get_request_with_ref_returns_a_given_string(self):
        with app.test_request_context('/?name=Peter'):
            self.t1 = T1()
            ret = self.t1.process_get(request, {"cr_reference_id": "123"})
            assert ret.code == status.HTTP_200_OK

    def test_get_request_with_ref_bq_returns_a_given_string(self):
        with app.test_request_context('/?name=Peter'):
            self.t1 = T1()
            try:
                ret = self.t1.process_get(request, {"cr_reference_id": "123", "behavior_qualifier": "Deposit"})
                assert False
            except Exception as e:
                print(str(e) + " " + str(type(e).__name__))
                assert type(e).__name__ == 'BianMethodNotImplementedException'

    def test_get_request_with_bad_bq_returns_a_given_string(self):
        with app.test_request_context('/?name=Peter'):
            self.t1 = T1()
            try:
                ret = self.t1.process_get(request, {"cr_reference_id": "123", "behavior_qualifier": "456"})
                assert False
            except Exception as e:
                print(str(e) + " " + str(type(e).__name__))
                assert type(e).__name__ == 'IllegalBQException'

    def test_get_request_with_ref_bq_not_returns_a_given_string_remote(self):
        with app.test_request_context('/?name=Peter'):
            self.t2 = T2()
            try:
                ret = self.t2.process_get(request, {"cr_reference_id": "123", "bq_reference_id": "457"})
                assert False
            except Exception as e:
                print(str(e) + " " + str(type(e)))
                assert type(e).__name__ == "BianException"


    def test_post_request_returns_a_given_string(self):
        with app.test_request_context('/?name=Peter'):
            self.t1 = T1()
            try:
                ret = self.t1.process_post(request, {})
                assert ret.code == status.HTTP_200_OK
            except Exception as e:
                print(str(e) + " " + str(type(e)))
                assert type(e).__name__ == "IllegalActionTermException"

    def test_patch_request_returns_a_given_string(self):
        with app.test_request_context('/?name=Peter'):
            self.t1 = T1()
            ret = self.t1.process_patch(request, {})
            assert ret.code == status.HTTP_200_OK

    def test_put_request_returns_a_given_string(self):
        with app.test_request_context('/?name=Peter'):
            self.t1 = T1()
            ret = self.t1.process_put(request, {})
            assert ret.code == status.HTTP_200_OK

    def test_delete_request_returns_a_given_string(self):
        with app.test_request_context('/?name=Peter'):
            self.t1 = T1()
            ret = self.t1.process_delete(request, {})
            assert ret.code == status.HTTP_200_OK

    def test_full_request_returns_a_given_string(self):
        with app.test_request_context('/?name=1'):
            self.t2 = T2()
            ret = self.t2.process_get(request, {"cr_reference_id":"1"})
            assert ret.code == status.HTTP_200_OK
            assert ret.payload["name"] == 'delectus aut autem'

    def test_bq_request_returns_a_given_string(self):
        with app.test_request_context('/?name=1'):
            self.t3 = T3()
            ret = self.t3.process_get(request, {"behavior_qualifier":"deposit"})
            assert ret.code == status.HTTP_200_OK
            assert ret.payload["name"] == 'delectus aut autem'

    def test_bq_request_returns_a_given_string(self):
        with app.test_request_context('/?name=1'):
            self.t3 = T3()
            self.t3.filter_separator = ";"
            ret = self.t3.process_get(request, {"behavior_qualifier":"deposit"})
            assert ret.code == status.HTTP_200_OK
            assert ret.payload["name"] == 'delectus aut autem'

    def test_cf_request_returns_a_given_string(self):
        with app.test_request_context('/?collection-filter=amount>100'):
            self.t3 = T3()
            ret = self.t3.process_get(request, {})
            assert ret.bian_request.collection_filter[0] == "amount>100"

    def test_cf_request_returns_a_given_list(self):
        with app.test_request_context('/?collection-filter=amount>100; user = 100   ; page_no = 2 ; count=20'):
            self.t3 = T3()
            self.t3.filter_separator = ";"
            ret = self.t3.process_get(request, {})
            assert ret.bian_request.collection_filter[0] == "amount>100"
            assert ret.bian_request.collection_filter[1] == "user = 100"
            assert ret.bian_request.collection_filter[2] == "page_no = 2"
            assert ret.bian_request.collection_filter[3] == "count=20"

    def test_action_request_returns_a_given_error(self):
        with app.test_request_context('/?collection-filter=amount>100'):
            self.t3 = T3()
            self.t3.bian_action = ActionTerms.EVALUATE
            try:
                ret = self.t3.process_get(request, {})
                assert ret.bian_request.collection_filter[0] != "amount>100"
            except Exception as e:
                assert type(e).__name__ == "IllegalActionTermException"

    def test_mask_cr_request_returns_a_given_error(self):
        with app.test_request_context('/?collection-filter=amount>100'):
            self.t3 = T3()
            self.t3.bian_action = ActionTerms.EXECUTE
            try:
                ret = self.t3.process_get(request, {"cr_reference_id":"1a","bq_reference_id":"1"})
                assert False
            except Exception as e:
                assert type(e).__name__ == "BadRequestError"

    def test_mask_bq_request_returns_a_given_error(self):
        with app.test_request_context('/?collection-filter=amount>100'):
            self.t3 = T3()
            self.t3.bian_action = ActionTerms.EXECUTE
            try:
                ret = self.t3.process_get(request, {"cr_reference_id":"1","bq_reference_id":"1b"})
                assert False
            except Exception as e:
                assert type(e).__name__ == "BadRequestError"

    def test_request_returns_a_response(self):
        with app.test_request_context('/?name=peter&collection-filter=amount>100'):
            self.t3 = T3()
            self.t3.bian_action = ActionTerms.EXECUTE
            ret = self.t3.process_get(request, {"cr_reference_id":"1","bq_reference_id":"1"})
            assert len(ret.bian_request.collection_filter) == 1
            assert ret.bian_request.action_term == ActionTerms.EXECUTE
            assert ret.bian_request.cr_reference_id == "1"
            assert ret.bian_request.bq_reference_id == "1"
            assert ret.bian_request.cr_reference_id == "1"
            assert ret.bian_request.request == request

    def test_sp_request_returns_a_given_list(self):
        with app.test_request_context('/perf'):
            self.s1 = S1()
            ret = self.s1.process_get(request, {})
            assert ret.code == status.HTTP_200_OK
