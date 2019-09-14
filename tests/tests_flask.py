from __future__ import print_function

from faker import Faker
from flask import Flask, request
from requests.auth import *
from flask_restful import Api
import json
from halo_flask.exceptions import BadRequestError,ApiError
from halo_flask.flask.utilx import status
from halo_bian.bian.abs_bian_srv import AbsBianMixin,InfoLinkX
from halo_bian.bian.exceptions import BianException
from halo_flask.apis import AbsBaseApi
from halo_flask.flask.utilx import Util
from halo_flask.flask.servicex import FoiBusinessEvent,SagaBusinessEvent
from halo_bian.bian.bian import BianCategory,ActionTerms

import unittest

fake = Faker()
app = Flask(__name__)
api = Api(app)
#app.config.from_object('settings')


class CnnApi(AbsBaseApi):
	name = 'Cnn'

class GoogleApi(AbsBaseApi):
	name = 'Google'

class TstApi(AbsBaseApi):
	name = 'Tst'

class T1(AbsBianMixin):#the basic
    pass

class T2(AbsBianMixin):# customized
    def validate_req(self, bian_request):
        print("in validate_req ")
        if bian_request:
            if "name" in bian_request.request.args:
                name = bian_request.request.args['name']
                if not name:
                    raise BadRequestError("missing value for query var name")
        return True

    def set_api_headers(bian_request):
        print("in set_api_headers ")
        headers = {'Accept':'application/json'}
        return headers

    def set_api_vars(bian_request):
        print("in set_api_vars " + str(bian_request))
        ret = {}
        name = bian_request.request.args['name']
        if name:
            ret['name'] = name
        if bian_request:
            ret["bq"] = bian_request.behavior_qualifier
            ret["id"] = bian_request.cr_reference_id
        return ret

    def set_api_auth(bian_request):
        print("in set_api_auth ")
        user = ''
        pswd = ''
        return HTTPBasicAuth(user,pswd)

    def execute_api(bian_request, back_api, back_vars, back_headers,back_auth,back_data):
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

    def create_resp_payload(self, bian_request,dict_back_json):
        print("in create_resp_payload " + str(dict_back_json))
        if dict_back_json:
            return self.map_from_json(dict_back_json,{})
        return dict_back_json

    def map_from_json(self,dict_back_json,payload):
        print("in map_from_json")
        payload['name'] = "test"#dict_back_json[1]["title"]
        return payload

class MyBusinessEvent(FoiBusinessEvent):
    pass

class SaBusinessEvent(SagaBusinessEvent):
    pass

class Api(AbsBaseApi):
    name = "Google"

class T3(AbsBianMixin):# the foi
    filter_separator = "#"
    filter_key_values = {None: {'customer-reference-id': 'customerId','amount':'amount','user':'user','page_no':'page_no','count':'count'}}
    filter_chars = {None: ['=','>']}

    def validate_req_deposit(self, bian_request):
        print("in validate_req_deposit ")
        if bian_request:
            if "name" in bian_request.request.args:
                name = bian_request.request.args['name']
                if not name:
                    raise BadRequestError("missing value for query var name")
        return True

    def validate_pre_deposit(self, bian_request):
        print("in validate_req_deposit ")
        if bian_request:
            if "name" in bian_request.request.args:
                name = bian_request.request.args['name']
                if not name:
                    raise BadRequestError("missing value for query var name")
        return True

    def set_back_api_deposit(self,bian_request,foi=None):
        if foi:
            return T3.set_back_api(bian_request,foi)
        print("in set_back_api_deposit ")
        return Api(Util.get_req_context(bian_request.request))

    def set_api_headers_deposit(self, bian_request,foi,dict):
        print("in set_api_headers_deposit ")
        headers = {'Accept':'application/json'}
        return headers

    def set_api_vars_deposit(self, bian_request,foi,dict):
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

    def set_api_auth_deposit(self, bian_request,foi,dict):
        print("in set_api_auth_deposit ")
        user = ''
        pswd = ''
        return HTTPBasicAuth(user,pswd)

    def execute_api_deposit(self, bian_request, back_api, back_vars, back_headers,back_auth,back_data,foi,dict):
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

    def create_resp_payload_deposit(self, bian_request,dict):
        print("in create_resp_payload_deposit " + str(dict))
        if dict:
            return self.map_from_json_deposit(dict,{})
        return {}

    def extract_json_deposit(self,bian_request,back_json,foi):
        print("in extract_json_deposit")
        return {"title":"good"}

    def map_from_json_deposit(self, dict, payload):
        print("in map_from_json_deposit")
        payload['name'] = dict['1']["title"]
        return payload

    def set_resp_headers_deposit(self, bian_request,headers):
        return self.set_resp_headers(bian_request,headers)

    def validate_post_deposit(self, bian_request,ret):
        return True

class T4(AbsBianMixin):# the foi
    def set_back_api(bian_request,foi=None):
        if foi:
            return super(T4).set_back_api(bian_request,foi)
        print("in set_back_api_deposit ")
        return TstApi(Util.get_req_context(bian_request.request))

class S1(InfoLinkX):
    pass

class TestUserDetailTestCase(unittest.TestCase):
    """
    Tests /users detail operations.
    """

    def setUp(self):
        app.config.from_pyfile('../settings.py')

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


    def test_post_request_returns_a_given_error(self):
        with app.test_request_context(method='POST',path='/tst'):
            self.t1 = T1()
            try:
                ret = self.t1.process_post(request, {})
                assert False
            except Exception as e:
                print(str(e) + " " + str(type(e)))
                assert type(e).__name__ == "BusinessEventMissingSeqException"

    def test_post_request_returns_a_given_error1(self):
        with app.test_request_context(method='POST',path='/'):
            self.t1 = T1()
            try:
                ret = self.t1.process_post(request, {})
                assert False
            except Exception as e:
                print(str(e) + " " + str(type(e)))
                assert type(e).__name__ == "IllegalActionTermException"

    def test_post_request_returns_a_given_string(self):
        with app.test_request_context(method='POST',path='/?name=Peter'):
            self.t1 = T1()
            self.t1.bian_action = ActionTerms.INITIATE
            ret = self.t1.process_post(request, {})
            assert ret.code == status.HTTP_200_OK

    def test_patch_request_returns_a_given_string(self):
        with app.test_request_context(method='PATCH',path='/?name=Peter'):
            self.t1 = T1()
            ret = self.t1.process_patch(request, {})
            assert ret.code == status.HTTP_200_OK

    def test_put_request_returns_a_given_string(self):
        with app.test_request_context(method='PUT',path='/tst?name=Peter'):
            self.t1 = T1()
            ret = self.t1.process_put(request, {})
            assert ret.code == status.HTTP_200_OK

    def test_delete_request_returns_a_given_string(self):
        with app.test_request_context(method='DELETE',path='/tst'):
            self.t1 = T1()
            ret = self.t1.process_delete(request, {})
            assert ret.code == status.HTTP_200_OK

    def test_delete_request_returns_a_given_error(self):
        with app.test_request_context(method='DELETE',path='/?name=Peter'):
            self.t1 = T1()
            try:
                ret = self.t1.process_delete(request, {})
                assert False
            except Exception as e:
                assert type(e).__name__ == "BusinessEventMissingSeqException"

    def test_get_request_returns_a_given_stringx_for_test(self):
        with app.test_request_context('/tst'):
            self.t1 = T1()
            ret = self.t1.process_get(request, {})
            assert ret.code == status.HTTP_200_OK


    def test_full_request_returns_a_given_string(self):
        with app.test_request_context('/?name=1'):
            self.t2 = T2()
            try:
                ret = self.t2.process_get(request, {"cr_reference_id":"1"})
                assert ret.code == status.HTTP_200_OK
                #assert ret.payload["name"] == 'delectus aut autem'
            except Exception as e:
                assert False

    def test_request_returns_a_given_string(self):
        with app.test_request_context('/x?name=1'):
            self.t4 = T4()
            ret = self.t4.process_get(request, {})
            assert ret.code == status.HTTP_200_OK
            assert ret.payload["name"] == 'delectus aut autem'

    def test_bq_request_returns_a_given_string(self):
        with app.test_request_context('/?name=1'):
            self.t3 = T3()
            self.t3.filter_separator = ";"
            ret = self.t3.process_get(request, {"behavior_qualifier":"deposit"})
            assert ret.code == status.HTTP_200_OK
            assert ret.payload["name"] == 'good'

    def test_cf_request_returns_a_given_string(self):
        with app.test_request_context('/?collection-filter=amount>100'):
            self.t3 = T3()
            ret = self.t3.process_get(request, {})
            assert ret.request.collection_filter[0] == "amount>100"
   
    def test_cf_request_returns_a_given_list(self):
        with app.test_request_context('/?collection-filter=amount>100; user = 100   ; page_no = 2 ; count=20'):
            self.t3 = T3()
            self.t3.filter_separator = ";"
            ret = self.t3.process_get(request, {})
            assert ret.request.collection_filter[0] == "amount>100"
            assert ret.request.collection_filter[1] == "user = 100"
            assert ret.request.collection_filter[2] == "page_no = 2"
            assert ret.request.collection_filter[3] == "count=20"
    
    def test_action_request_returns_a_given_error(self):
        with app.test_request_context('/?collection-filter=amount>100'):
            self.t3 = T3()
            self.t3.bian_action = ActionTerms.EVALUATE
            try:
                ret = self.t3.process_get(request, {})
                assert ret.request.collection_filter[0] != "amount>100"
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
            assert len(ret.request.collection_filter) == 1
            assert ret.request.action_term == ActionTerms.EXECUTE
            assert ret.request.cr_reference_id == "1"
            assert ret.request.bq_reference_id == "1"
            assert ret.request.cr_reference_id == "1"
            assert ret.request.request == request

    def test_sp_request_returns_a_given_list(self):
        with app.test_request_context('/info'):
            self.s1 = S1()
            ret = self.s1.process_get(request, {})
            print("x="+str(ret.payload))
            assert ret.code == status.HTTP_200_OK
