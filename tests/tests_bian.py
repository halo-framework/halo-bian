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
from halo_flask.apis import *
from halo_flask.flask.utilx import Util
from halo_flask.flask.servicex import FoiBusinessEvent,SagaBusinessEvent
from halo_bian.bian.bian import BianCategory,ActionTerms,Feature,ControlRecord,GenericArtifact,BianContext

import unittest

fake = Faker()
app = Flask(__name__)
api = Api(app)

class OutboundApi(AbsBaseApi):
    name = 'Outbound'

class CAFeature(Feature):
    pass

class BankingProduct(GenericArtifact):
    pass

class CAControlRecord(BankingProduct):
    pass

class CAContext(BianContext):
    TESTER = "Tester"
    BianContext.items[TESTER]="test"


class A1(AbsBianMixin):#the basic
    def set_back_api(self, halo_request, foi=None):
        if not foi:#not in seq
            if halo_request.request.method == HTTPChoice.get.value:
                return CnnApi(Util.get_req_context(halo_request.request),HTTPChoice.get.value)
            if halo_request.request.method == HTTPChoice.delete.value:
                return CnnApi(Util.get_req_context(halo_request.request),HTTPChoice.delete.value)
        return super(A1,self).set_back_api(halo_request,foi)

    def set_added_api_vars(self, bian_request,vars, seq=None, dict=None):
        logger.debug("in set_api_vars " + str(bian_request))
        if seq == '3':
            if "name" in bian_request.request.args:
                name = bian_request.request.args['name']
                if name not in vars:
                    vars['name'] = name
        return vars


    def execute_api(self,halo_request, back_api, back_vars, back_headers, back_auth, back_data=None, seq=None, dict=None):
        logger.debug("in execute_api "+back_api.name)
        if back_api:
            timeout = Util.get_timeout(halo_request.request)
            try:
                seq_msg = ""
                if seq:
                    seq_msg = "seq = " + seq + "."
                if seq == '3':
                    back_api.set_api_url('ID', back_vars['name'])
                ret = back_api.run(timeout, headers=back_headers,auth=back_auth, data=back_data)
                msg = "in execute_api. " + seq_msg + " code= " + str(ret.status_code)
                logger.info(msg)
                return ret
            except ApiError as e:
                raise BianException(e)
        return None

class A2(A1):# customized
    def validate_req(self, bian_request):
        print("in validate_req ")
        if bian_request:
            if "name" in bian_request.request.args:
                name = bian_request.request.args['name']
                if not name:
                    raise BadRequestError("missing value for query var name")
        return True

    def set_api_headers(self,bian_request, seq=None, dict=None):
        print("in set_api_headers ")
        headers = {'Accept':'application/json'}
        return headers

    def set_api_vars(self,bian_request, seq=None, dict=None):
        print("in set_api_vars " + str(bian_request))
        ret = {}
        name = bian_request.request.args['name']
        if name:
            ret['name'] = name
        if bian_request:
            ret["bq"] = bian_request.behavior_qualifier
            ret["id"] = bian_request.cr_reference_id
        return ret

    def set_api_auth(self,bian_request, seq=None, dict=None):
        print("in set_api_auth ")
        user = ''
        pswd = ''
        return HTTPBasicAuth(user,pswd)

    def execute_api(self,bian_request, back_api, back_vars, back_headers,back_auth,back_data, seq=None, dict=None):
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


class A3(AbsBianMixin):# the foi
    filter_separator = "#"
    filter_key_values = {None: {'customer-reference-id': 'customerId','amount':'amount','user':'user','page_no':'page_no','count':'count'}}
    filter_chars = {None: ['=','>']}

    def set_back_api(self,bian_request,foi=None):
        if foi:
            return super(A3,self).set_back_api(bian_request,foi)
        print("in set_back_api ")
        api = TstApi(Util.get_req_context(bian_request.request))
        api.set_api_url("ID","1")
        return api

    def validate_req_depositsandwithdrawals(self, bian_request):
        print("in validate_req_deposit ")
        if bian_request:
            if "name" in bian_request.request.args:
                name = bian_request.request.args['name']
                if not name:
                    raise BadRequestError("missing value for query var name")
        return True

    def validate_pre_depositsandwithdrawals(self, bian_request):
        print("in validate_req_deposit ")
        if bian_request:
            if "name" in bian_request.request.args:
                name = bian_request.request.args['name']
                if not name:
                    raise BadRequestError("missing value for query var name")
        return True

    def set_back_api_depositsandwithdrawals(self,bian_request,foi=None):
        if foi:
            return self.set_back_api(bian_request,foi)
        print("in set_back_api_deposit ")
        TstApi(Util.get_req_context(bian_request.request))

    def set_api_headers_depositsandwithdrawals(self, bian_request,foi=None,dict=None):
        print("in set_api_headers_deposit ")
        headers = {'Accept':'application/json'}
        return headers

    def set_api_vars_depositsandwithdrawals(self, bian_request,foi=None,dict=None):
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

    def set_api_auth_depositsandwithdrawals(self, bian_request,foi=None,dict=None):
        print("in set_api_auth_deposit ")
        user = ''
        pswd = ''
        return HTTPBasicAuth(user,pswd)

    def execute_api_depositsandwithdrawals(self, bian_request, back_api, back_vars, back_headers,back_auth,back_data,foi=None,dict=None):
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

    def create_resp_payload_depositsandwithdrawals(self, bian_request,dict):
        print("in create_resp_payload_deposit " + str(dict))
        if dict:
            return self.map_from_json_depositsandwithdrawals(dict,{})
        return {}

    def extract_json_depositsandwithdrawals(self,bian_request,back_json,foi=None):
        print("in extract_json_deposit")
        return {"title":"good"}

    def map_from_json_depositsandwithdrawals(self, dict, payload):
        print("in map_from_json_deposit")
        payload['name'] = dict[1]["title"]
        return payload

    def set_resp_headers_depositsandwithdrawals(self, bian_request,headers):
        return self.set_resp_headers(bian_request,headers)

    def validate_post_depositsandwithdrawals(self, bian_request,ret):
        return True

class A4(AbsBianMixin):# the foi
    def set_back_api(self,bian_request,foi=None):
        print("in set_back_api ")
        if foi:
            return super(A4,self).set_back_api(bian_request,foi)
        api = TstApi(Util.get_req_context(bian_request.request))
        api.set_api_url("ID", "1")
        return api

    def create_resp_payload(self,halo_request, dict):
        print("in create_resp_payload")
        json = dict[1]
        return {"name":json["title"]}

class A5(A3):
    def set_back_api_depositsandwithdrawals(self, bian_request, foi=None):
        if foi:
            return self.set_back_api(bian_request, foi)
        print("in set_back_api_deposit ")
        return GoogleApi(Util.get_req_context(bian_request.request))


class S1(InfoLinkX):
    pass

class TestUserDetailTestCase(unittest.TestCase):
    """
    Tests /users detail operations.
    """

    def setUp(self):
        #app.config.from_pyfile('../settings.py')
        app.config.from_object('settings')

    def test_1_get_request_returns_a_given_string(self):
        with app.test_request_context('/?name=Peter'):
            self.a1 = A1()
            ret = self.a1.process_get(request, {})
            assert ret.code == status.HTTP_200_OK

    def test_2_get_request_with_ref_returns_a_given_string(self):
        with app.test_request_context('/?name=Peter'):
            self.a1 = A1()
            ret = self.a1.process_get(request, {"cr_reference_id": "123"})
            assert ret.code == status.HTTP_200_OK

    def test_3_get_request_with_ref_bq_returns_a_given_string(self):
        with app.test_request_context('/?name=Peter'):
            self.a1 = A1()
            try:
                ret = self.a1.process_get(request, {"cr_reference_id": "123", "behavior_qualifier": "DepositsandWithdrawals"})
                assert False
            except Exception as e:
                print(str(e) + " " + str(type(e).__name__))
                assert type(e).__name__ == 'HaloMethodNotImplementedException'

    def test_4_get_request_with_bad_bq_returns_a_given_string(self):
        with app.test_request_context('/?name=Peter'):
            self.a1 = A1()
            try:
                ret = self.a1.process_get(request, {"cr_reference_id": "123", "behavior_qualifier": "456"})
                assert False
            except Exception as e:
                print(str(e) + " " + str(type(e).__name__))
                assert type(e).__name__ == 'IllegalBQException'


    def test_5_post_request_returns_a_given_error(self):
        with app.test_request_context(method='POST',path='/tst'):
            self.a1 = A1()
            try:
                ret = self.a1.process_post(request, {})
                assert False
            except Exception as e:
                print(str(e) + " " + str(type(e)))
                assert type(e).__name__ == "IllegalActionTermException"

    def test_6_post_request_returns_a_given_error1(self):
        with app.test_request_context(method='POST',path='/'):
            self.a1 = A1()
            try:
                ret = self.a1.process_post(request, {})
                assert False
            except Exception as e:
                print(str(e) + " " + str(type(e)))
                assert type(e).__name__ == "IllegalActionTermException"

    def test_7_post_request_returns_a_given_string(self):
        with app.test_request_context(method='POST',path='/?name=Peter'):
            self.a1 = A1()
            self.a1.bian_action = ActionTerms.INITIATE
            ret = self.a1.process_post(request, {})
            assert ret.code == status.HTTP_201_CREATED

    def test_8_patch_request_returns_a_given_string(self):
        with app.test_request_context(method='PATCH',path='/?name=Peter'):
            self.a1 = A1()
            ret = self.a1.process_patch(request, {})
            assert ret.code == status.HTTP_202_ACCEPTED

    def test_90_put_request_returns_a_given_string(self):
        with app.test_request_context(method='PUT',path='/tst?name=1'):
            self.a1 = A1()
            ret = self.a1.process_put(request, {})
            assert ret.code == status.HTTP_202_ACCEPTED

    def test_91_delete_request_returns_a_given_string(self):
        with app.test_request_context(method='DELETE',path='/tst'):
            self.a1 = A1()
            ret = self.a1.process_delete(request, {})
            assert ret.code == status.HTTP_200_OK

    def test_92_get_request_returns_a_given_stringx_for_test(self):
        with app.test_request_context('/tst'):
            self.a1 = A1()
            ret = self.a1.process_get(request, {})
            assert ret.code == status.HTTP_200_OK


    def test_93_full_request_returns_a_given_string(self):
        with app.test_request_context('/?name=1'):
            self.a2 = A2()
            ret = self.a2.process_get(request, {"cr_reference_id":"1"})
            assert ret.code == status.HTTP_200_OK
            assert ret.payload["name"] == 'test'


    def test_94_request_returns_a_given_string(self):
        with app.test_request_context('/x?name=1'):
            self.a4 = A4()
            ret = self.a4.process_get(request, {})
            assert ret.code == status.HTTP_200_OK
            assert ret.payload["name"] == 'delectus aut autem'

    def test_95_bq_request_returns_a_given_string(self):
        with app.test_request_context('/?name=1'):
            self.a3 = A3()
            self.a3.filter_separator = ";"
            ret = self.a3.process_get(request, {"behavior_qualifier":"DepositsandWithdrawals"})
            assert ret.code == status.HTTP_200_OK
            assert ret.payload["name"] == 'good'

    def test_96_cf_request_returns_a_given_string(self):
        with app.test_request_context('/?collection-filter=amount>100'):
            self.a3 = A3()
            ret = self.a3.process_get(request, {})
            assert ret.request.collection_filter[0] == "amount>100"
   
    def test_97_cf_request_returns_a_given_list(self):
        with app.test_request_context(method='POST',path='/?name=john&collection-filter=amount>100; user = 100   ; page_no = 2 ; count=20'):
            self.a3 = A3()
            self.a3.bian_action = ActionTerms.EXECUTE
            self.a3.filter_separator = ";"
            ret = self.a3.process_post(request, {})
            assert ret.request.collection_filter[0] == "amount>100"
            assert ret.request.collection_filter[1] == "user = 100"
            assert ret.request.collection_filter[2] == "page_no = 2"
            assert ret.request.collection_filter[3] == "count=20"
    
    def test_98_action_request_returns_a_given_error(self):
        with app.test_request_context('/?collection-filter=amount>100'):
            self.a3 = A3()
            self.a3.bian_action = ActionTerms.EVALUATE
            try:
                ret = self.a3.process_get(request, {})
                assert ret.request.collection_filter[0] != "amount>100"
            except Exception as e:
                assert type(e).__name__ == "IllegalActionTermException"

    def test_990_mask_cr_request_returns_a_given_error(self):
        with app.test_request_context('/?collection-filter=amount>100'):
            self.a3 = A3()
            self.a3.bian_action = ActionTerms.EXECUTE
            try:
                ret = self.a3.process_get(request, {"cr_reference_id":"1a","bq_reference_id":"1"})
                assert False
            except Exception as e:
                assert type(e).__name__ == "BadRequestError"

    def test_991_mask_bq_request_returns_a_given_error(self):
        with app.test_request_context('/?collection-filter=amount>100'):
            self.a3 = A3()
            self.a3.bian_action = ActionTerms.EXECUTE
            try:
                ret = self.a3.process_get(request, {"cr_reference_id":"1","bq_reference_id":"1b"})
                assert False
            except Exception as e:
                assert type(e).__name__ == "BadRequestError"

    def test_992_request_returns_a_response(self):
        with app.test_request_context('/?name=peter&collection-filter=amount>100'):
            self.a3 = A3()
            self.a3.bian_action = ActionTerms.EXECUTE
            ret = self.a3.process_get(request, {"cr_reference_id":"1","bq_reference_id":"1"})
            assert ret.code == status.HTTP_200_OK
            assert len(ret.request.collection_filter) == 1
            assert ret.request.action_term == ActionTerms.EXECUTE
            assert ret.request.cr_reference_id == "1"
            assert ret.request.bq_reference_id == "1"
            assert ret.request.request == request

    def test_993_request_returns_a_response(self):
        with app.test_request_context('/?name=peter&collection-filter=amount>100'):
            self.a3 = A3()
            self.a3.bian_action = ActionTerms.EXECUTE
            ret = self.a3.process_put(request, {"cr_reference_id":"1","bq_reference_id":"1"})
            assert ret.code == 200

    def test_994_sp_request_returns_a_given_list(self):
        with app.test_request_context('/info'):
            self.s1 = S1()
            ret = self.s1.process_get(request, {})
            print("x="+str(ret.payload))
            assert ret.code == status.HTTP_200_OK

    def test_995_control_record_returns_a_given_list(self):
        with app.test_request_context('/?name=1&queryparams=amount>100@x=y'):
            self.a3 = A3()
            ret = self.a3.process_get(request, {"sd_reference_id":"1","behavior_qualifier":"DepositsandWithdrawals"})
            print("x=" + str(ret.payload))
            assert ret.code == status.HTTP_200_OK
            assert ret.request.behavior_qualifier == 'DepositsandWithdrawals'
            assert ret.request.request == request
            assert ret.request.sd_reference_id == "1"
            assert len(ret.request.query_params) == 2
            assert ret.request.query_params[0] == 'amount>100'
            assert ret.request.query_params[1] == 'x=y'

    def test_996_request_sub_returns_a_response(self):
        with app.test_request_context('/?name=peter&collection-filter=amount>100',headers={'x-bian-devparty': 'Your value'}):
            app.config["BIAN_CONTEXT_LIST"] = [BianContext.DPARTY]
            self.a5 = A5()
            self.a5.bian_action = ActionTerms.EXECUTE
            ret = self.a5.process_put(request, {"sd_reference_id":"1","cr_reference_id":"1","bq_reference_id":"1"})
            assert ret.code == 200

    def test_997_request_sub_returns_a_response(self):
        with app.test_request_context('/?name=peter&collection-filter=amount>100',headers={'x-bian-devparty1': 'Your value'}):
            app.config["BIAN_CONTEXT_LIST"] = [BianContext.DPARTY]
            self.a5 = A5()
            self.a5.bian_action = ActionTerms.EXECUTE
            try:
                ret = self.a5.process_put(request, {"sd_reference_id":"1","cr_reference_id":"1","bq_reference_id":"1"})
            except Exception as e:
                assert type(e).__name__ == "MissingBianContextException"

    def test_998_request_sub_returns_a_response(self):
        with app.test_request_context('/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/servicefees/3/?name=peter&collection-filter=amount>100',headers={'x-bian-devparty': 'Your value'}):
            app.config["BIAN_CONTEXT_LIST"] = [BianContext.DPARTY]
            self.a5 = A5()
            self.a5.bian_action = ActionTerms.EXECUTE
            ret = self.a5.process_put(request, {"cr_reference_id":"1","behavior_qualifier":"DepositsandWithdrawals","bq_reference_id":"1","sub_qualifier":"Deposits","sbq_reference_id":"1"})
            assert ret.code == 200

    def test_999_request_sub_returns_a_response(self):
        with app.test_request_context('/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/servicefees/3/?name=peter&collection-filter=amount>100',headers={'x-bian-devparty': 'Your value'}):
            app.config["BIAN_CONTEXT_CLASS"] = None
            self.a5 = A5()
            self.a5.bian_action = ActionTerms.EXECUTE
            ret = self.a5.process_put(request, {"sd_reference_id":"1","cr_reference_id":"1","bq_reference_id":"3"})
            assert ret.code == 200

    def test_9991_request_sub_returns_a_response(self):
        with app.test_request_context('/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/servicefees/3/?name=peter&collection-filter=amount>100',headers={'x-bian-devparty': 'Your value'}):
            self.a5 = A5()
            self.a5.bian_action = ActionTerms.EXECUTE
            ret = self.a5.process_put(request, {"sd_reference_id":"1","cr_reference_id":"1","bq_reference_id":"3"})
            assert ret.code == 200

    def test_9992_request_sub_returns_a_response(self):
        with app.test_request_context('/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/servicefees/3/?name=peter&collection-filter=amount>100',headers={'x-bian-devparty': 'Your value'}):
            app.config["BIAN_CONTEXT_LIST"] = [CAContext.TESTER]
            self.a5 = A5()
            self.a5.bian_action = ActionTerms.EXECUTE
            try:
                ret = self.a5.process_put(request, {"sd_reference_id":"1","cr_reference_id":"1","bq_reference_id":"3"})
            except Exception as e:
                assert type(e).__name__ == "MissingBianContextException"

    def test_9993_request_sub_returns_a_response(self):
        with app.test_request_context('/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/deposits/4/?name=peter&collection-filter=amount>100',headers={'x-bian-devparty': 'Your value'}):
            app.config["BIAN_CONTEXT_CLASS"] = None
            self.a5 = A5()
            self.a5.bian_action = ActionTerms.EXECUTE
            ret = self.a5.process_put(request, {"sd_reference_id":"1","cr_reference_id":"2","bq_reference_id":"3","sbq_reference_id":"4"})
            assert ret.code == 200

    def test_9994_request_sub_returns_a_response(self):
        with app.test_request_context('/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/servicefees/3/?name=peter&collection-filter=amount>100',headers={'x-bian-devparty': 'Your value'}):
            self.a5 = A5()
            self.a5.bian_action = ActionTerms.EXECUTE
            ret = self.a5.process_put(request, {"cr_reference_id":"1","behavior_qualifier":"DepositsandWithdrawals","bq_reference_id":"1","sub_qualifier":"Deposits","sbq_reference_id":"1"})
            assert ret.code == 200