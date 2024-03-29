from __future__ import print_function

from typing import Tuple, Dict

from faker import Faker
from flask import Flask, request
from halo_app.app.cmd_assembler import AbsCmdAssembler
from halo_app.app.event import AbsHaloEvent
from halo_app.app.notification import Notification
from halo_app.app.request import HaloQueryRequest
from halo_app.app.result import Result
from halo_app.app.uow import AbsUnitOfWork
from halo_app.domain.repository import AbsRepository
from halo_app.domain.service import AbsDomainService
from halo_app.entrypoints import client_util
from halo_app.entrypoints.client_type import ClientType
#from tests.fake import FakeBoundary, FakePublisher
from halo_app.infra.mail import AbsMailService
from halo_app.infra.sql_repository import SqlAlchemyRepository
from halo_app.infra.sql_uow import SqlAlchemyUnitOfWorkManager, SqlAlchemyUnitOfWork
from requests.auth import *
import json
from nose.tools import eq_
import unittest
import pytest
import os
from halo_app.const import LOC

from halo_bian.bian.app.command import AbsBianCommand
from halo_bian.bian.app.context import BianContext
from halo_bian.bian.app.request import BianCommandRequest, BianEventRequest
from halo_bian.bian.domain.model import CurrentAccount
from halo_bian.bian.util import BianUtil
from halo_bian.bian.app.handler import AbsBianCommandHandler, ActivationAbsBianMixin, ConfigurationAbsBianMixin, \
    FeedbackAbsBianMixin, AbsBianEventHandler, AbsBianQueryHandler
from halo_bian.bian.db import AbsBianDbMixin
from halo_app.app.anlytx_filter import RequestFilterClear
from halo_bian.bian.bian import BianCategory, ActionTerms, Feature, ControlRecord, GenericArtifact, BianRequestFilter, FunctionalPatterns
from halo_app.infra.exceptions import ApiException
from halo_bian.bian.exceptions import BianException
from halo_app.infra.apis import *
from halo_app.app.utilx import Util
from halo_app.app.business_event import FoiBusinessEvent, SagaBusinessEvent
from halo_app.ssm import set_app_param_config, set_host_param_config
from halo_app.app.globals import load_global_data
from halo_app.app.bus import IBus, Bus
from halo_app.base_util import BaseUtil
from halo_app.sys_util import SysUtil
from http import HTTPStatus

from tests.fake import FakeBus

faker = Faker()
app = Flask(__name__)


def get_bian_context1(request) -> BianContext:
    context = BianUtil.get_bian_context()
    for i in request.headers.keys():
        if type(i) == str:
            context.put(i, request.headers[i])
    context.put(HaloContext.method, request.method)
    return context


class OutboundApi(AbsRestApi):
    name = 'Outbound'


class CAFeature(Feature):
    pass


class BankingProduct(GenericArtifact):
    pass


class CAControlRecord(BankingProduct):
    pass


class BaseCmdAssembler(AbsCmdAssembler):
    def get_command_type(self,method_id:str)-> str:
        return "halo_bian.bian.app.command.DictBianCommand"

    def write_cmd_for_method(self, method_id: str, data: Dict,action_term:str, flag: str = None) -> AbsBianCommand:
        command_type = self.get_command_type(method_id)
        cmd_instance = Reflect.instantiate(command_type,AbsBianCommand,method_id,data,action_term)
        return cmd_instance

class CAContext(BianContext):
    TESTER = "Tester"
    BianContext.items[TESTER] = "test"


class BianRequestFilterX(BianRequestFilter):
    def augment_event_with_data(self, event, halo_request, halo_response):
        raise BianException("req")
        return event


class BianRequestFilterClear(RequestFilterClear):
    pass


class RequestFilterClearX(RequestFilterClear):
    def run(self):
        for event in self.eventx:
            logger.debug("insert_events_to_repository " + str(event.serialize()))


class CnnApi(AbsRestApi):
    name = 'Cnn'


class GoogleApi(AbsRestApi):
    name = 'Google'


class TstApi(AbsRestApi):
    name = 'Tst'


class Tst2Api(AbsSoapApi):
    name = 'Tst2'

    def do_method1(self, timeout, data=None, headers=None, auth=None):
        soap_ret = self.client.service.Method1(data["first"], data['second'])
        print(str(soap_ret))
        response = SoapResponse(soap_ret)
        #response.payload = {"msg": soap_ret}
        #response.status_code = 200
        #response.headers = {}
        return response


class Tst3Api(AbsRestApi):
    name = 'Tst3'


class Tst4Api(AbsRestApi):
    name = 'Tst4'


class CurrentAccountRepository(SqlAlchemyRepository):
    def get_type(self) ->type:
        return CurrentAccount

class ExCurrentAccountRepository(SqlAlchemyRepository):
    def get_type(self) ->type:
        return CurrentAccount

class CurrentAccountUow(SqlAlchemyUnitOfWork):
    def init_repository(self):
        return CurrentAccountRepository(self.session)

class ExCurrentAccountUow(CurrentAccountUow):

    exRepository:AbsRepository = None

    def __enter__(self):
        self.exRepositoryrepository = ExCurrentAccountRepository(self.session)
        return super().__enter__()

class TestBianEvent(AbsHaloEvent):
    xid:str = None

    def __init__(self, mid, xid:str):
        super(TestBianEvent,self).__init__(mid)
        self.xid = xid

class A0(AbsBianCommandHandler):  # the basic
    bian_action = ActionTerms.REQUEST

    def __init__(self,usecase_id):
        super(A0,self).__init__(usecase_id)
        self.domain_service = AbsDomainService()
        self.infra_service = AbsMailService()

    def handle(self,bian_command_request:BianCommandRequest,uow:AbsUnitOfWork) ->Result:
        with uow:
            var_name =  'cr_reference_id'
            item = None
            if var_name in bian_command_request.command.vars:
                item = uow.repository.get(bian_command_request.command.vars[var_name])
            entity = self.domain_service.validate(item)
            self.infra_service.send(entity)
            uow.commit()
            payload = {"1":{"a":"b"}}
            return Result.ok(payload)

    def set_back_api(self, halo_request, foi=None):
        if not foi:  # not in seq
            if True:
                return CnnApi(halo_request.context, HTTPChoice.get.value)
            else:
                return CnnApi(halo_request.context, HTTPChoice.delete.value)
        return super(A0, self).set_back_api(halo_request, foi)

    def set_added_api_vars(self, bian_request, vars, seq=None, dict=None):
        logger.debug("in set_api_vars " + str(bian_request))
        if seq == '3':
            if "name" in bian_request.request.args:
                name = bian_request.request.args['name']
                if name not in vars:
                    vars['name'] = name
        return vars

    def execute_api(self, halo_request, back_api, back_vars, back_headers, back_auth, back_data=None, seq=None,
                    dict=None):
        logger.debug("in execute_api " + back_api.name)
        if back_api:
            timeout = Util.get_timeout(halo_request.context)
            try:
                seq_msg = ""
                if seq:
                    seq_msg = "seq = " + seq + "."
                if seq == '3':
                    back_api.set_api_url('ID', back_vars['name'])
                ret = back_api.run(timeout, headers=back_headers, auth=back_auth, data=back_data)
                msg = "in execute_api. " + seq_msg + " code= " + str(ret.status_code)
                logger.info(msg)
                return ret
            except ApiException as e:
                raise BianException(e)
        return None

class A1(A0):
    def handle(self, bian_command_request: BianCommandRequest, uow: AbsUnitOfWork) -> Result:
        with uow:
            item = uow.repository.get(bian_command_request.cr_reference_id)
            entity = self.domain_service.validate(item)
            self.infra_service.send(entity)
            uow.commit()
            return Result.ok({"1": {"a": "d"}})

class A2(A1):  # customized
    def validate_req(self, bian_request):
        print("in validate_req ")
        notification:Notification = Notification()
        if bian_request:
            if "name" in bian_request.command.vars:
                name = bian_request.command.vars['name']
                if not name:
                    notification.addError("missing_query_var","missing value for query var name")
        return notification

    def set_api_headers(self, bian_request, api, seq=None, dict=None):
        print("in set_api_headers ")
        headers = {'Accept': 'application/json'}
        return headers

    def set_api_vars(self, bian_request, api, seq=None, dict=None):
        print("in set_api_vars " + str(bian_request))
        ret = {}
        name = bian_request.command.vars['name']
        if name:
            ret['name'] = name
        if bian_request:
            ret["bq"] = bian_request.behavior_qualifier
            ret["id"] = bian_request.cr_reference_id
        return ret

    def set_api_auth(self, bian_request, api, seq=None, dict=None):
        print("in set_api_auth ")
        user = ''
        pswd = ''
        return HTTPBasicAuth(user, pswd)

    def execute_api(self, bian_request, back_api, back_vars, back_headers, back_auth, back_data, seq=None, dict=None):
        print("in execute_api ")
        if back_api:
            timeout = Util.get_timeout(bian_request.context)
            try:
                back_api.set_api_url('ID', back_vars['name'])
                ret = back_api.get(timeout, headers=back_headers, auth=back_auth)
                return ret
            except ApiException as e:
                raise BianException(e)
        return None

    def create_resp_payload(self, bian_request, dict_back_json):
        print("in create_resp_payload " + str(dict_back_json))
        if dict_back_json:
            return self.map_from_json(dict_back_json, {})
        return dict_back_json

    def map_from_json(self, dict_back_json, payload):
        print("in map_from_json")
        payload['name'] = "test"  # dict_back_json[1]["title"]
        return payload


class MyBusinessEvent(FoiBusinessEvent):
    pass


class SaBusinessEvent(SagaBusinessEvent):
    pass


class A3(AbsBianCommandHandler):  # the foi
    bian_action = ActionTerms.REQUEST
    filter_separator = "#"
    filter_key_values = {
        None: {'customer-reference-id': 'customerId', 'amount': 'amount', 'user': 'user', 'page_no': 'page_no',
               'count': 'count'}}
    filter_chars = {None: ['=', '>']}

    def __init__(self,usecase_id):
        super(A3,self).__init__(usecase_id)
        self.domain_service = AbsDomainService()
        self.infra_service = AbsMailService()

    def handle(self,bian_command_request:BianCommandRequest,uow:AbsUnitOfWork) ->Result:
        with uow:
            item = uow.repository.get(bian_command_request.cr_reference_id)
            entity = self.domain_service.validate(item)
            self.infra_service.send(entity)
            api1 = ApiMngr.get_api_instance("Cnn", bian_command_request.context)
            ret1 = api1.run(100)
            api2 = ApiMngr.get_api_instance("Tst2", bian_command_request.context)
            api2.op = 'method1'
            data = {}
            data['first'] = 'start'
            data['second'] = 'end'
            ret2 = api2.run(100,data)
            uow.commit()

        return Result.ok({"1":ret1.content,"2":ret2.content})

    def set_back_api(self, bian_request, foi=None):
        if foi:
            return super(A3, self).set_back_api(bian_request, foi)
        print("in set_back_api ")
        api = TstApi(bian_request.context)
        api.set_api_url("ID", "1")
        return api

    def validate_pre(self, bian_request)->Notification:
        print("in validate_req_deposit ")
        notification: Notification = Notification()
        if bian_request and hasattr(bian_request, 'collection_filter') and bian_request.collection_filter:
            for f in bian_request.collection_filter:
                if "amount" == f.field:
                    pass
        return notification

    def set_back_api(self, bian_request, foi=None):
        if foi:
            return self.set_back_api(bian_request, foi)
        print("in set_back_api_deposit ")
        TstApi(bian_request.context)

    def set_api_headers(self, bian_request, api, foi=None, dict=None):
        print("in set_api_headers_deposit ")
        headers = {'Accept': 'application/json'}
        return headers

    def set_api_vars(self, bian_request, api, foi=None, dict=None):
        print("in set_api_vars_deposit " + str(bian_request))
        ret = {}
        name = None
        if bian_request.body and 'name' in bian_request.body:
            name = bian_request.body['name']
        if name:
            ret['name'] = name
        if bian_request:
            ret["bq"] = bian_request.behavior_qualifier
            ret["id"] = bian_request.cr_reference_id
        return ret

    def set_api_auth(self, bian_request, api, foi=None, dict=None):
        print("in set_api_auth_deposit ")
        user = ''
        pswd = ''
        return HTTPBasicAuth(user, pswd)

    def execute_api(self, bian_request, back_api, back_vars, back_headers, back_auth, back_data,
                                           foi=None, dict=None):
        print("in execute_api_deposit ")
        if back_api:
            timeout = Util.get_timeout(bian_request.timeout)
            try:
                back_api.set_api_url('ID', back_vars['name'])
                ret = back_api.get(timeout, headers=back_headers, auth=back_auth)
                return ret
            except ApiException as e:
                raise BianException(e)
        return None

    def create_resp_payload(self, bian_request, create_resp_payload_dict):
        print("in create_resp_payload_deposit " + str(create_resp_payload_dict))
        if create_resp_payload_dict:
            return self.map_from_json(create_resp_payload_dict, {"name":""})
        return {}

    def extract_json(self, bian_request, api, back_json, foi=None):
        print("in extract_json_deposit")
        return {"title": "good"}

    def map_from_json(self, dict, payload):
        print("in map_from_json_deposit")
        if 'name' in payload:
            payload['name'] = dict['1']
            payload['more'] = dict['2']
        return payload



    def validate_post(self, bian_request, ret):
        return True


class A4(AbsBianCommandHandler):  # the foi
    bian_action = ActionTerms.INITIATE
    def set_back_api(self, bian_request, foi=None):
        print("in set_back_api ")
        if foi:
            return super(A4, self).set_back_api(bian_request, foi)
        api = TstApi(bian_request.context)
        api.set_api_url("ID", "1")
        return api

    def create_resp_payload(self, halo_request, api, dict):
        print("in create_resp_payload")
        json = dict['1']
        return {"name": json["title"]}


class A5(A3):
    def set_back_api_depositsandwithdrawals(self, bian_request, foi=None):
        if foi:
            return self.set_back_api(bian_request, foi)
        print("in set_back_api_deposit ")
        return GoogleApi(bian_request.context)


class A6(A5):
    def validate_req_depositsandwithdrawals_deposits(self, bian_request):
        return

    def validate_pre_depositsandwithdrawals_deposits(self, bian_request):
        return

    def set_back_api_depositsandwithdrawals_deposits(self, bian_request):
        return

    def set_api_headers_depositsandwithdrawals_deposits(self, bian_request, api):
        return

    def set_api_vars_depositsandwithdrawals_deposits(self, bian_request, api):
        return

    def set_api_auth_depositsandwithdrawals_deposits(self, bian_request, api):
        return

    def execute_api_depositsandwithdrawals_deposits(self, bian_request, back_api, back_vars,
                                                    back_headers, back_auth, back_data):
        return

    def extract_json_depositsandwithdrawals_deposits(self, bian_request, api, back_response):
        return

    def create_resp_payload_depositsandwithdrawals_deposits(self, bian_request, dict):
        return

    def set_resp_headers_depositsandwithdrawals_deposits(self, bian_request, headers):
        return

    def validate_post_depositsandwithdrawals_deposits(self, halo_request, halo_response):
        return


class A7(AbsBianCommandHandler):  # the foi
    bian_action = ActionTerms.INITIATE

    def __init__(self,usecase_id):
        super(A7,self).__init__(usecase_id)
        self.domain_service = AbsDomainService()
        self.infra_service = AbsMailService()

    def handle(self,bian_command_request:BianCommandRequest,uow:AbsUnitOfWork) ->Result:
        with uow:
            item = uow.repository.get(bian_command_request.cr_reference_id)
            entity = self.domain_service.validate(item)
            self.infra_service.send(entity)
            api1 = ApiMngr.get_api_instance("Cnn", bian_command_request.context)
            ret1 = api1.run(100)
            api2 = ApiMngr.get_api_instance("Tst2", bian_command_request.context)
            api2.op = 'method1'
            data = {}
            data['first'] = 'start'
            data['second'] = 'end'
            ret2 = api2.run(100,data)
            uow.commit()

        return Result.ok({"1":ret1.content,"2":ret2.content})

    def set_back_api(self, bian_request, foi=None):
        print("in set_back_api ")
        if foi:
            return super(A7, self).set_back_api(bian_request, foi)
        api = Tst2Api(bian_request.context)
        api.set_api_url("ID", "1")
        return api

    def create_resp_payload(self, halo_request, dict):
        print("in create_resp_payload")
        json = dict['2']
        return {"name": json}

class A8(AbsBianEventHandler):
    def __init__(self,usecase_id):
        super(A8, self).__init__(usecase_id)
        self.domain_service = AbsDomainService()
        self.infra_service = AbsMailService()

    def handle(self, bian_event_request: BianEventRequest, uow: AbsUnitOfWork)->Result:
        var_name = 'cr_reference_id'
        item = None
        if var_name in bian_event_request.event.vars:
            item = uow.repository.get(bian_event_request.event.vars[var_name])
        entity = self.domain_service.validate(item)
        self.infra_service.send(entity)
        return {"1": {"a": "b"}}

class A9(AbsBianQueryHandler):
    bian_action = ActionTerms.RETRIEVE

    def __init__(self,usecase_id):
        super(A9, self).__init__(usecase_id)

    def set_query_data(self,halo_query_request: HaloQueryRequest)->Tuple[str,dict]:
        return "select 1",{}


class X1(Bus,ActivationAbsBianMixin):
    pass


class X2(Bus,ConfigurationAbsBianMixin):
    pass


class X3(Bus,FeedbackAbsBianMixin):
    def persist_feedback_request(self, bian_request, servicing_session_id, cr_id, bq_id):
        pass

    def validate_req_depositsandwithdrawals(self, req):
        pass


class BianDbMixin(AbsBianDbMixin):
    pass


class FakeBoundry(Bus):
    def fake_process(self,event):
        super(FakeBoundry,self)._process_event(event)



boundary = None

@pytest.fixture
def sqlite_boundary(sqlite_session_factory):
    app.config.from_object(f"halo_bian.config.Config_{os.getenv('HALO_STAGE', 'loc')}")
    with app.test_request_context(method='GET', path='/?abc=def'):
        from halo_app import bootstrap
        from tests.fake import FakePublisher
        global boundary
        if boundary:
            return boundary
        boundary = bootstrap.bootstrap(
            start_orm=True,
            uowm=SqlAlchemyUnitOfWorkManager(sqlite_session_factory),
            publish=FakePublisher()
        )
        return boundary

@pytest.mark.usefixtures("sqlite_boundary")
class TestUserDetailTestCase(unittest.TestCase):
    """
    Tests /users detail operations.
    """

    session_id = None

    @classmethod
    def setUpClass(cls):
        app.config.from_object(f"halo_bian.config.Config_{os.getenv('HALO_STAGE', 'loc')}")
        with app.test_request_context(method='GET', path='/?abc=def'):
            from halo_app.const import LOC
            app.config['ENV_TYPE'] = LOC
            app.config['SSM_TYPE'] = "AWS"
            app.config['FUNC_NAME'] = "FUNC_NAME"
            # app.config['API_CONFIG'] =
            app.config['AWS_REGION'] = 'us-east-1'

            # config
            from halo_app import bootstrap
            bootstrap.COMMAND_HANDLERS["z0"] = A0.run_command_class
            bootstrap.COMMAND_HANDLERS["z1"] = A1.run_command_class
            bootstrap.COMMAND_HANDLERS["z1a"] = A1.run_command_class
            bootstrap.COMMAND_HANDLERS["z3"] = A3.run_command_class
            bootstrap.COMMAND_HANDLERS["z7"] = A7.run_command_class
            bootstrap.COMMAND_HANDLERS["z2"] = A2.run_command_class
            bootstrap.COMMAND_HANDLERS["z2a"] = A2.run_command_class
            bootstrap.COMMAND_HANDLERS["z2b"] = A2.run_command_class
            #bootstrap.COMMAND_HANDLERS["z8"] = A8.run_command_class
            bootstrap.EVENT_HANDLERS[TestBianEvent] = [A8.run_event_class]
            bootstrap.QUERY_HANDLERS["q1"] = A9.run_query_class


    def setUp(self):
        print("starting...")
        # app.config.from_pyfile('../settings.py')
        #app.config.from_object('settings')
        app.config.from_object(f"halo_bian.config.Config_{os.getenv('HALO_STAGE', 'loc')}")

        with app.test_request_context(method='GET', path='/?abc=def'):
            try:
                load_api_config(app.config['ENV_TYPE'], app.config['SSM_TYPE'], app.config['FUNC_NAME'],
                                app.config['API_CONFIG'])
            except Exception as e:
                eq_(e.__class__.__name__, "NoApiClassException")
        print("do setup")

    @pytest.fixture(autouse=True)
    def init_boundary(self, sqlite_boundary):
        self.boundary = sqlite_boundary

    def test_00_get_request_returns_a_given_string(self):
        #from halo_app.app.viewsx import load_global_data
        app.config['ENV_TYPE'] = LOC
        app.config['SSM_TYPE'] = "AWS"
        # app.config['FUNC_NAME'] = "FUNC_NAME"
        app.config['HALO_HOST'] = "halo_bian"
        app.config['AWS_REGION'] = 'us-east-1'
        app.config["INIT_CLASS_NAME"] = 'halo_bian.bian.abs_bian_srv.BianGlobalService'
        app.config["INIT_DATA_MAP"] = {'INIT_STATE': "Idle",
                                       'PROP_URL': "C:\\dev\projects\\halo\\framework\\test179\\bian_service_domains\\halo_contact_dialogue\\env\\config\\bian_setting_mapping.json"}
        with app.test_request_context('/?name=Peter'):
            try:
                if 'INIT_DATA_MAP' in app.config and 'INIT_CLASS_NAME' in app.config:
                    data_map = app.config['INIT_DATA_MAP']
                    class_name = app.config['INIT_CLASS_NAME']
                    load_global_data(class_name, data_map)
            except Exception as e:
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_0_get_request_returns_a_given_string(self):
        json = {
            "serviceDomainActivationActionTaskRecord": {},
            "serviceDomainCenterReference": "SCR793499",
            "serviceDomainServiceReference": "CPASSR703914",
            "serviceDomainServiceConfigurationRecord": {
                "serviceDomainServiceConfigurationSettingReference": "700761",
                "serviceDomainServiceConfigurationSettingType": "string",
                "serviceDomainServiceConfigurationSetup": {
                    "serviceDomainServiceConfigurationParameter": "string"
                }
            }
        }
        app.config["DBACCESS_CLASS"] = "tests.test_bian.BianDbMixin"
        app.config['ENV_TYPE'] = LOC
        app.config['SSM_TYPE'] = "AWS"
        app.config['HALO_HOST'] = "halo_bian"
        # app.config['FUNC_NAME'] = "FUNC_NAME"
        app.config['AWS_REGION'] = 'us-east-1'
        app.config["INIT_CLASS_NAME"] = 'halo_bian.bian.abs_bian_srv.BianGlobalService'
        app.config["INIT_DATA_MAP"] = {'INIT_STATE': "Idle",
                                       'PROP_URL': "C:\\dev\projects\\halo\\framework\\test179\\bian_service_domains\\halo_contact_dialogue\\env\\config\\bian_setting_mapping.json"}

        with app.test_request_context('/?name=Peter', json=json):
            app.config['HALO_HOST'] = "halo_bian"
            if 'INIT_DATA_MAP' in app.config and 'INIT_CLASS_NAME' in app.config:
                data_map = app.config['INIT_DATA_MAP']
                class_name = app.config['INIT_CLASS_NAME']
                load_global_data(class_name, data_map)

            action_term = ActionTerms.ACTIVATE
            functional_pattern = FunctionalPatterns.FULFILL
            filter_separator = ";"
            method_id = "X"
            bian_context = client_util.get_halo_context(request.headers)
            bian_request = BianUtil.create_bian_request(bian_context,method_id, {"body":json},ActionTerms.CONTROL)
            ret = self.boundary.execute(bian_request)
            assert ret.code == HTTPStatus.OK

    def test_1_do_handle(self):
        os.environ['DEBUG_LOG'] = 'true'
        with app.test_request_context('/?cr_reference_id=123'):
            bian_context = client_util.get_halo_context(request.headers,request)
            action_term = ActionTerms.REQUEST
            bian_request = BianUtil.create_bian_request(bian_context, "z0", request.args,action_term)
            bian_response = self.boundary.execute(bian_request)
            response = SysUtil.process_response_for_client(bian_response)
            if response.error:
                print(json.dumps(response.error, indent=4, sort_keys=True))
            assert response.success == True

    def test_1a_do_query(self):
        with app.test_request_context('/?cr_reference_id=123'):
            bian_context = client_util.get_halo_context(request.headers,request)
            method_id = "q1"
            action_term = ActionTerms.RETRIEVE
            bian_request = BianUtil.create_bian_request(bian_context, method_id, request.args,action_term)
            bian_response = self.boundary.execute(bian_request)
            response = SysUtil.process_response_for_client(bian_response)
            if response.error:
                print(json.dumps(response.error, indent=4, sort_keys=True))
            d = response.__dict__
            for i in d:
                print(str(i)+":"+str(d[i]))
            assert response.success == True

    def test_1b_do_query_error(self):
        with app.test_request_context('/?cr_reference_id=123'):
            bian_context = client_util.get_halo_context(request.headers,request)
            method_id = "q2"
            action_term = ActionTerms.RETRIEVE
            bian_request = BianUtil.create_bian_request(bian_context, method_id, request.args,action_term)
            bian_response = self.boundary.execute(bian_request)
            response = SysUtil.process_response_for_client(bian_response)
            if response.error:
                print(json.dumps(response.error, indent=4, sort_keys=True))
            d = response.__dict__
            for i in d:
                print(str(i)+":"+str(d[i]))
            assert bian_response.success == False

    def test_1c_do_vars(self):
        with app.test_request_context('/queryparams=a'):
            sd_reference_id = '1'
            cr_reference_id = '2'
            bq_reference_id = '3'
            behavior_qualifier = 'abc'
            queryparams = '{"field": "a", "op": "<", "value": 4}'
            collection_filter = '{"field": "b", "op": "<", "value": 5}'
            body = {}
            varsx = BianUtil.get_bian_vars(vars())
            assert varsx['sd_reference_id'] == '1'
            assert varsx['cr_reference_id'] == '2'
            assert varsx['bq_reference_id'] == '3'
            assert varsx['behavior_qualifier'] == 'abc'
            assert varsx['queryparams'].__len__() == 1
            assert varsx['collection_filter'].__len__() == 1
            assert varsx['body'] == {}

    def test_2_do_api(self):
        with app.test_request_context('/?name=Peter'):
            bian_context = client_util.get_halo_context(request.headers)
            method_id = "z1"
            action_term = ActionTerms.REQUEST
            bian_request = BianUtil.create_bian_request(bian_context,method_id, {"cr_reference_id": "123"},action_term)
            ret = self.boundary.execute(bian_request)
            assert ret.success == True

    def test_3_handle_bian(self):
        with app.test_request_context('/?name=Peter'):
            bian_context = client_util.get_halo_context(request.headers)
            method_id = "z1a"
            action_term = ActionTerms.REQUEST
            try:
                bian_request = BianUtil.create_bian_request(bian_context,method_id,
                                          {"cr_reference_id": "123", "behavior_qualifier": "DepositsandWithdrawals"},action_term)
                ret = self.boundary.execute(bian_request)
                assert ret.success == True
                assert ret.payload['1'] == {}
            except Exception as e:
                print(str(e) + " " + str(type(e).__name__))
                assert type(e).__name__ == 'HaloMethodNotImplementedException'

    def test_4_handle_bian_soap(self):
        with app.test_request_context('/?name=Peter'):
            bian_context = client_util.get_halo_context(request.headers,request)
            method_id = "z3"
            action_term = ActionTerms.REQUEST
            try:
                bian_request = BianUtil.create_bian_request(bian_context,method_id, {"cr_reference_id": "123"},action_term)
                bian_response = self.boundary.execute(bian_request)
                response = SysUtil.process_response_for_client(bian_response)
                if response.error:
                    print(json.dumps(response.error, indent=4, sort_keys=True))
                assert bian_response.success == True
                eq_(bian_response.payload["2"],'Your input parameters are start and end')
            except Exception as e:
                print(str(e) + " " + str(type(e).__name__))
                assert type(e).__name__ == 'IllegalBQError'

    def test_5_api(self):
        with app.test_request_context(method='POST', path='/tst'):
            bian_context = client_util.get_halo_context(request.headers,request)
            method_id = "z2"
            action_term = ActionTerms.REQUEST
            try:
                bian_request = BianUtil.create_bian_request(bian_context,method_id,{"name":"x"},action_term)
                bian_response = self.boundary.execute(bian_request)
                response = SysUtil.process_response_for_client(bian_response)
                if response.error:
                    print(json.dumps(response.error, indent=4, sort_keys=True))
                assert bian_response.success == True
            except Exception as e:
                print(str(e) + " " + str(type(e)))
                assert type(e).__name__ == "IllegalActionTermError"

    def test_6_seq(self):
        with app.test_request_context(method='POST', path='/'):
            bian_context = client_util.get_halo_context(request.headers,request)
            method_id = "z2a"
            action_term = ActionTerms.EXECUTE
            try:
                bian_request = BianUtil.create_bian_request(bian_context, method_id, {"name":"c"}, action_term)
                bian_response = self.boundary.execute(bian_request)
                response = SysUtil.process_response_for_client(bian_response)
                if response.error:
                    print(json.dumps(response.error, indent=4, sort_keys=True))
                assert response.success == True
                assert response.payload == {'1': {'a': 'd'}}
            except Exception as e:
                print(str(e) + " " + str(type(e)))
                assert type(e).__name__ == "IllegalActionTermError"

    def test_7_saga(self):
        with app.test_request_context(method='POST', path='/?name=Peter'):
            bian_context = client_util.get_halo_context(request.headers)
            method_id = "z2b"
            action_term = ActionTerms.INITIATE
            bian_request = BianUtil.create_bian_request(bian_context, method_id, request.args, action_term)
            ret = self.boundary.execute(bian_request)
            assert ret.success == True

    def test_8_soap(self):
        os.environ['DEBUG_LOG'] = 'true'
        with app.test_request_context(method='PATCH', path='/?name=Peter'):
            bian_context = client_util.get_halo_context(request.headers,request)
            action_term = ActionTerms.INITIATE
            method_id = "z7"
            bian_request = BianUtil.create_bian_request(bian_context,method_id,request.args,action_term)
            bian_response = self.boundary.execute(bian_request)
            response = SysUtil.process_response_for_client(bian_response)
            if response.error:
                print(json.dumps(response.error, indent=4, sort_keys=True))
            assert response.success == True
            assert response.payload["2"] == 'Your input parameters are start and end'

    def test_10_event(self):
        halo_context = client_util.get_halo_context({},client_type=ClientType.cli)
        halo_event = TestBianEvent( "z9","12")
        halo_request = SysUtil.create_event_request(halo_context,halo_event)
        fake_boundary = FakeBus(self.boundary.uowm,self.boundary.publisher,self.boundary.event_handlers,self.boundary.command_handlers,self.boundary.query_handlers)
        fake_boundary.fake_process(halo_request)

    def test_10a_event(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            halo_context = client_util.get_halo_context(request.headers,request)
            halo_event = TestBianEvent( "z9", "12")
            halo_request = SysUtil.create_event_request(halo_context,halo_event)
            fake_boundary = FakeBus(self.boundary.uowm,self.boundary.publisher, self.boundary.event_handlers, self.boundary.command_handlers,
                                        self.boundary.query_handlers)
            fake_boundary.fake_process(halo_request)

    def test_90_put_request_returns_a_given_string(self):
        os.environ['DEBUG_LOG'] = 'true'
        with app.test_request_context(method='PUT', path='/tst?name=news'):
            bian_context = client_util.get_halo_context(request.headers,request)
            action_term = ActionTerms.INITIATE
            method_id = "z8"
            bian_request = BianUtil.create_bian_request(bian_context,method_id,request.args,action_term)
            bian_response = self.boundary.execute(bian_request)
            response = SysUtil.process_response_for_client(bian_response)
            if response.error:
                print(json.dumps(response.error, indent=4, sort_keys=True))
            assert response.success == True

    def test_91_delete_request_returns_a_given_string(self):
        with app.test_request_context(method='DELETE', path='/tst'):
            bian_context = client_util.get_halo_context(request.headers)
            action_term = ActionTerms.INITIATE
            method_id = "z9"
            bian_request = BianUtil.create_bian_request(bian_context,method_id,request.args,action_term)
            ret = self.boundary.execute(bian_request)
            assert ret.code == HTTPStatus.OK

    def test_92_get_request_returns_a_given_stringx_for_test(self):
        with app.test_request_context('/tst'):
            bian_context = client_util.get_halo_context(request.headers)
            action_term = ActionTerms.INITIATE
            method_id = "z10"
            bian_request = BianUtil.create_bian_request(bian_context,method_id, request.args,action_term)
            ret = self.boundary.execute(bian_request)
            assert ret.code == HTTPStatus.OK

    def test_93_full_request_returns_a_given_string(self):
        with app.test_request_context('/?name=news'):
            bian_context = client_util.get_halo_context(request.headers)
            action_term = ActionTerms.INITIATE
            method_id = "z11"
            bian_request = BianUtil.create_bian_request(bian_context,method_id, {"cr_reference_id": "1"},action_term)
            ret = self.boundary.execute(bian_request)
            assert ret.code == HTTPStatus.OK
            assert ret.payload["name"] == 'test'

    def test_95_bq_request_returns_a_given_string(self):
        with app.test_request_context('/?name=1'):
            bian_context = client_util.get_halo_context(request.headers)
            action_term = ActionTerms.INITIATE
            method_id = "z12"
            self.a3.filter_separator = ";"
            bian_request = BianUtil.create_bian_request(bian_context, method_id, {"behavior_qualifier": "DepositsandWithdrawals"}, action_term)
            ret = self.boundary.execute(bian_request)
            assert ret.code == HTTPStatus.OK
            assert ret.payload["name"] == 'b'

    def test_96_cf_request_returns_a_given_string(self):
        with app.test_request_context('/?collection-filter=amount>100'):
            bian_context = client_util.get_halo_context(request.headers)
            action_term = ActionTerms.INITIATE
            method_id = "z13"
            bian_request = BianUtil.create_bian_request(bian_context,method_id,request.args,action_term)
            ret = self.boundary.execute(bian_request)
            assert ret.request.collection_filter[0] == "amount>100"

    def test_961_cf_request_returns_a_given_string(self):
        with app.test_request_context('/?collection-filter={"field": "amount", "op": ">", "value": 10.24}'):
            q = request.args['collection-filter']
            import json
            from flask_filter.schemas import FilterSchema
            filter_schema = FilterSchema()
            try:
                collection_filter_json = json.loads(q)
                if "field" in collection_filter_json:
                    many = False
                else:
                    many = True
                filters = filter_schema.load(collection_filter_json, many=many)
                if not many:
                    filters = [filters]
                from halo_app.app.query_filters import Filter
                arr = []
                for f in filters:
                    filter = Filter(f.field, f.OP, f.value)
                    arr.append(filter)
            except Exception as e:
                raise e
            vars = {'collection_filter':arr}
            bian_context = client_util.get_halo_context(request.headers)
            action_term = ActionTerms.INITIATE
            method_id = "z14"
            bian_request = BianUtil.create_bian_request(bian_context,method_id, vars,action_term)
            ret = self.boundary.execute(bian_request)
            assert str(ret.request.collection_filter[0]) == "Filter(field='amount', op='>', value=10.24)"
            assert ret.payload == {'name': 'good'}

    def test_97_cf_request_returns_a_given_list(self):
        with app.test_request_context(method='POST',
                                      path='/?name=john&collection-filter={"field": "amount", "op": ">", "value": 10.24}'):
            action_term = ActionTerms.INITIATE
            method_id = "z15"
            self.a3.filter_separator = ";"
            bian_context = client_util.get_halo_context(request.headers)
            bian_request = BianUtil.create_bian_request(bian_context,method_id,request.args,action_term)
            ret = self.boundary.execute(bian_request)
            assert ret.request.collection_filter[0] == "amount>100"
            assert ret.request.collection_filter[1] == "user = 100"
            assert ret.request.collection_filter[2] == "page_no = 2"
            assert ret.request.collection_filter[3] == "count=20"

    def test_98_action_request_returns_a_given_error(self):
        with app.test_request_context('/?collection-filter={"field": "amount", "op": ">", "value": 10.24}'):
            bian_context = client_util.get_halo_context(request.headers)
            action_term = ActionTerms.EVALUATE
            method_id = "z16"
            try:
                bian_request = BianUtil.create_bian_request(bian_context,method_id, request.args,action_term)
                ret = self.boundary.execute(bian_request)
                assert ret.request.collection_filter[0] != "amount>100"
            except Exception as e:
                assert type(e).__name__ == "IllegalActionTermError"

    def test_990_mask_cr_request_returns_a_given_error(self):
        with app.test_request_context(
                '/consumer-loan/1a/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/?collection-filter={"field": "amount", "op": ">", "value": 10.24}'):
            bian_context = client_util.get_halo_context(request.headers)
            action_term = ActionTerms.EVALUATE
            method_id = "z17"
            try:
                bian_request = BianUtil.create_bian_request(bian_context,method_id, {"cr_reference_id": "2", "bq_reference_id": "3a"},action_term)
                ret = self.boundary.execute(bian_request)
                assert False
            except Exception as e:
                assert type(e).__name__ == "IllegalBQError"

    def test_991_mask_bq_request_returns_a_given_error(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/1b/?collection-filter={"field": "amount", "op": ">", "value": 10.24}'):
            bian_context = client_util.get_halo_context(request.headers)
            action_term = ActionTerms.EVALUATE
            method_id = "z18"
            try:
                bian_request = BianUtil.create_bian_request(bian_context,method_id, {"cr_reference_id": "2", "bq_reference_id": "1b","collection-filter":""},action_term)
                ret = self.boundary.execute(bian_request)
                assert False
            except Exception as e:
                assert type(e).__name__ == "IllegalBQError"

    def test_992_request_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/1/depositsandwithdrawals/1/?name=peter&collection-filter=amount>100'):
            bian_context = client_util.get_halo_context(request.headers)
            bian_action = ActionTerms.EXECUTE
            method_id = "z19"
            bian_request = BianUtil.create_bian_request(bian_context,method_id, {"cr_reference_id": "1", "bq_reference_id": "1"},bian_action)
            ret = self.boundary.execute(bian_request)
            assert ret.code == HTTPStatus.OK
            assert len(ret.request.collection_filter) == 1
            assert ret.request.action_term == ActionTerms.EXECUTE
            assert ret.request.cr_reference_id == "1"
            assert ret.request.bq_reference_id == "1"
            assert ret.request.request == request

    def test_993_request_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/1/depositsandwithdrawals/1/?name=peter&collection-filter=amount>100'):
            bian_context = client_util.get_halo_context(request.headers)
            self.a3 = A3()
            self.a3.bian_action = ActionTerms.EXECUTE
            ret = self.a3.process_put(bian_context,"x", {"cr_reference_id": "1", "bq_reference_id": "1"})
            assert ret.code == 200

    def test_995_control_record_returns_a_given_list(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement//?name=1&queryparams=amount>100@x=y'):
            bian_context = client_util.get_halo_context(request.headers)
            self.a3 = A3()
            ret = self.a3.process_get(bian_context,"x", {"sd_reference_id": "1", "behavior_qualifier": "DepositsandWithdrawals"})
            print("x=" + str(ret.payload))
            assert ret.code == HTTPStatus.OK
            assert ret.request.behavior_qualifier == 'DepositsandWithdrawals'
            assert ret.request.request == request
            assert ret.request.sd_reference_id == "1"
            assert len(ret.request.query_params) == 2
            assert ret.request.query_params[0] == 'amount>100'
            assert ret.request.query_params[1] == 'x=y'

    def test_996_request_sub_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/1/depositsandwithdrawals/1/?name=peter&collection-filter=amount>100',
                headers={'x-bian-devparty': 'Your value'}):
            app.config["BIAN_CONTEXT_LIST"] = [BianContext.APP_CLIENT]
            bian_context = client_util.get_halo_context(request.headers)
            self.a5 = A5()
            self.a5.bian_action = ActionTerms.EXECUTE
            ret = self.a5.process_put(bian_context,"x", {"sd_reference_id": "1", "cr_reference_id": "1", "bq_reference_id": "1"})
            assert ret.code == 200

    def test_997_request_sub_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/1/depositsandwithdrawals/1/?name=peter&collection-filter=amount>100',
                headers={'x-bian-devparty1': 'Your value'}):
            app.config["BIAN_CONTEXT_LIST"] = [BianContext.APP_CLIENT]
            bian_context = client_util.get_halo_context(request.headers)
            self.a5 = A5()
            self.a5.bian_action = ActionTerms.EXECUTE
            try:
                ret = self.a5.execute(bian_context,"x",
                                          {"sd_reference_id": "1", "cr_reference_id": "1", "bq_reference_id": "1"})
            except Exception as e:
                assert type(e).__name__ == "MissingBianContextException"

    def test_998_request_sub_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/?name=peter&collection-filter=amount>100',
                headers={'x-bian-devparty': 'Your value'}):
            app.config["BIAN_CONTEXT_LIST"] = [BianContext.APP_CLIENT]
            bian_context = client_util.get_halo_context(request.headers)
            self.a5 = A5()
            self.a5.bian_action = ActionTerms.EXECUTE
            ret = self.a5.execute(bian_context,"x",
                                      {"cr_reference_id": "2", "bq_reference_id": "3", "sbq_reference_id": "4"})
            assert ret.code == 200

    def test_999_request_sub_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/?name=peter&collection-filter=amount>100',
                headers={'x-bian-devparty': 'Your value'}):
            app.config["HALO_CONTEXT_CLASS"] = None
            bian_context = client_util.get_halo_context(request.headers)
            self.a5 = A5()
            self.a5.bian_action = ActionTerms.EXECUTE
            ret = self.a5.execute(bian_context,"x", {"sd_reference_id": "1", "cr_reference_id": "2", "bq_reference_id": "3"})
            assert ret.code == 200

    def test_9991_request_sub_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/?name=peter&collection-filter=amount>100',
                headers={'x-bian-devparty': 'Your value'}):
            bian_context = client_util.get_halo_context(request.headers)
            self.a5 = A5()
            self.a5.bian_action = ActionTerms.EXECUTE
            ret = self.a5.execute(bian_context,"x", {"sd_reference_id": "1", "cr_reference_id": "1", "bq_reference_id": "3"})
            assert ret.code == 200

    def test_9992_request_sub_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/servicefees/3/?name=peter&collection-filter=amount>100',
                headers={'x-bian-devparty': 'Your value'}):
            bian_context = client_util.get_halo_context(request.headers)
            app.config["BIAN_CONTEXT_LIST"] = [CAContext.TESTER]
            self.a5 = A5()
            self.a5.bian_action = ActionTerms.EXECUTE
            try:
                ret = self.a5.execute(bian_context,"x",
                                          {"sd_reference_id": "1", "cr_reference_id": "1", "bq_reference_id": "3"})
            except Exception as e:
                assert type(e).__name__ == "HaloMethodNotImplementedException"

    def test_9993_request_sub_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/deposits/4/?name=peter&collection-filter=amount>100',
                headers={'x-bian-devparty': 'Your value'}):
            bian_context = client_util.get_halo_context(request.headers)
            app.config["HALO_CONTEXT_CLASS"] = None
            self.a6 = A6()
            self.a6.bian_action = ActionTerms.EXECUTE
            ret = self.a6.execute(bian_context,"x", {"sd_reference_id": "1", "cr_reference_id": "2", "bq_reference_id": "3",
                                                "sbq_reference_id": "4"})
            assert ret.code == 200

    def test_99931_request_sub_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/deposits/1/?name=peter&collection-filter=amount>100',
                headers={'x-bian-devparty': 'Your value'}):
            bian_context = client_util.get_halo_context(request.headers)
            app.config["HALO_CONTEXT_CLASS"] = None
            self.a6 = A6()
            self.a6.bian_action = ActionTerms.EXECUTE
            ret = self.a6.execute(bian_context,"x", {"sd_reference_id": "1", "cr_reference_id": "2", "bq_reference_id": "3",
                                                "sbq_reference_id": "1"})
            assert ret.code == 200

    def test_9994_request_sub_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/?name=peter&collection-filter=amount>100',
                headers={'x-bian-devparty': 'Your value'}):
            bian_context = client_util.get_halo_context(request.headers)
            self.a5 = A5()
            self.a5.bian_action = ActionTerms.EXECUTE
            try:
                ret = self.a5.execute(bian_context,"x",
                                          {"cr_reference_id": "1", "bq_reference_id": "1", "sbq_reference_id": "1"})
            except Exception as e:
                assert type(e).__name__ == "IllegalBQError"

    def test_9995_request_sub_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/deposits/1/?name=peter&collection-filter=amount>100',
                headers={'x-bian-devparty': 'Your value'}):
            bian_context = client_util.get_halo_context(request.headers)
            app.config["REQUEST_FILTER_CLASS"] = 'halo_bian.bian.bian.BianRequestFilter'
            self.a6 = A6()
            self.a6.bian_action = ActionTerms.EXECUTE
            ret = self.a6.execute(bian_context,"x", {"sd_reference_id": "1", "cr_reference_id": "2", "bq_reference_id": "3",
                                                "sbq_reference_id": "1"})
            assert ret.code == 200

    def test_9996_request_sub_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/deposits/1/?name=peter&collection-filter=amount>100',
                headers={'x-bian-devparty': 'Your value'}):
            bian_context = client_util.get_halo_context(request.headers)
            app.config["REQUEST_FILTER_CLASS"] = 'tests_bian.BianRequestFilterX'
            self.a6 = A6()
            self.a6.bian_action = ActionTerms.EXECUTE
            try:
                ret = self.a6.execute(bian_context,"x",
                                          {"sd_reference_id": "1", "cr_reference_id": "2", "bq_reference_id": "3",
                                           "sbq_reference_id": "1"})
            except Exception as e:
                assert type(e).__name__ == "BianException"

    def test_9997_request_sub_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/deposits/1/?name=peter&collection-filter=amount>100',
                headers={'x-bian-devparty': 'Your value'}):
            bian_context = client_util.get_halo_context(request.headers)
            app.config["REQUEST_FILTER_CLEAR_CLASS"] = 'tests_bian.BianRequestFilterClear'
            self.a6 = A6()
            self.a6.bian_action = ActionTerms.EXECUTE
            ret = self.a6.execute(bian_context,"x", {"sd_reference_id": "1", "cr_reference_id": "2", "bq_reference_id": "3",
                                                "sbq_reference_id": "1"})
            assert ret.code == 200

    def test_9998_request_sub_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/deposits/1/?name=peter&collection-filter=amount>100',
                headers={'x-bian-devparty': 'Your value'}):
            bian_context = client_util.get_halo_context(request.headers)
            app.config["REQUEST_FILTER_CLEAR_CLASS"] = 'tests_bian.RequestFilterClearX'
            self.a6 = A6()
            self.a6.bian_action = ActionTerms.EXECUTE
            try:
                ret = self.a6.execute(bian_context,"x",
                                          {"sd_reference_id": "1", "cr_reference_id": "2", "bq_reference_id": "3",
                                           "sbq_reference_id": "1"})
            except Exception as e:
                assert type(e).__name__ == "BianException"

    def test_99981_request_sub_returns_a_response(self):
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/deposits/1/?name=peter&collection-filter=amount>100',
                headers={'x-bian-devparty': 'Your value'}):
            bian_context = client_util.get_halo_context(request.headers)
            app.config["REQUEST_FILTER_CLEAR_CLASS"] = 'tests_bian.RequestFilterClearX'
            self.a7 = A7()
            self.a7.bian_action = ActionTerms.EXECUTE
            method_id = "execute_x"
            bian_request = BianUtil.create_bian_request(bian_context,method_id,{"sd_reference_id": "1", "cr_reference_id": "2"})
            try:
                ret = self.a7.execute(bian_request)
                assert ret.code == 200
            except Exception as e:
                assert type(e).__name__ == "BianException"

    def test_99991_request_sub_returns_a_response(self):
        json = {
            "serviceDomainActivationActionTaskRecord": {},
            "serviceDomainCenterReference": "SCR793499",
            "serviceDomainServiceReference": "CPASSR703914",
            "serviceDomainServiceConfigurationRecord": {
                "serviceDomainServiceConfigurationSettingReference": "700761",
                "serviceDomainServiceConfigurationSettingType": "string",
                "serviceDomainServiceConfigurationSetup": {
                    "serviceDomainServiceConfigurationParameter": "string"
                }
            }
        }
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/deposits/1/?name=peter',
                headers={'x-bian-devparty': 'Your value'}, json=json):
            bian_context = client_util.get_halo_context(request.headers)
            self.x1 = X1()
            self.x1.bian_action = ActionTerms.ACTIVATE
            ret = self.x1.execute(bian_context,"x", {})
            print(ret.payload)
            self.session_id = ret.payload["serviceDomainServicingSessionReference"]
            assert ret.code == 200

    def test_99992_request_sub_returns_a_response(self):
        json = {
            "serviceDomainConfigurationActionTaskRecord": {},
            "serviceDomainServicingSessionReference": "SSSR764367",
            "serviceDomainServiceReference": "CPASSR744740",
            "serviceDomainServiceConfigurationRecord": {
                "serviceDomainServiceConfigurationSettingReference": "710630",
                "serviceDomainServiceConfigurationSettingType": "string",
                "serviceDomainServiceConfigurationSetup": {
                    "serviceDomainServiceConfigurationParameter": "string"
                },
                "serviceDomainServiceSubscription": {
                    "serviceDomainServiceSubscriberReference": "756221",
                    "serviceDomainServiceSubscriberAccessProfile": "string"
                },
                "serviceDomainServiceAgreement": {
                    "serviceDomainServiceAgreementReference": "721156",
                    "serviceDomainServiceUserReference": "733696",
                    "serviceDomainServiceAgreementTermsandConditions": "string"
                }
            }
        }
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/deposits/1/?name=peter',
                headers={'x-bian-devparty': 'Your value'}, json=json):
            bian_context = client_util.get_halo_context(request.headers)
            from halo_app.app.globals import load_global_data
            app.config['SSM_TYPE'] = "AWS"
            app.config["INIT_CLASS_NAME"] = 'halo_bian.bian.abs_bian_srv.BianGlobalService'
            app.config["INIT_DATA_MAP"] = {'INIT_STATE': "Idle", 'PROP_URL':
                "C:\\dev\\projects\\halo\\halo_bian\\halo_bian\\env\\config\\bian_setting_mapping.json"}
            load_global_data(app.config["INIT_CLASS_NAME"], app.config["INIT_DATA_MAP"])
            self.x2 = X2()
            self.x2.bian_action = ActionTerms.CONFIGURE
            ret = self.x2.execute(bian_context,"x", {"sd_reference_id": self.session_id})
            assert ret.code == 200

    def test_99993_request_sub_returns_a_response(self):
        json = {
            "serviceDomainFeedbackActionTaskRecord": {},
            "serviceDomainFeedbackActionRecord": {
                "serviceDomainServicingSessionReference": "796678",
                "controlRecordInstanceReference": "724385",
                "behaviorQualifierInstanceReference": "789747",
                "feedbackRecordType": "string",
                "feedbackRecord": {}
            }
        }
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/deposits/1/?name=peter',
                headers={'x-bian-devparty': 'Your value'}, json=json):
            bian_context = client_util.get_halo_context(request.headers)
            from halo_app.app.globals import load_global_data
            app.config['SSM_TYPE'] = "AWS"
            app.config["INIT_CLASS_NAME"] = 'halo_bian.bian.abs_bian_srv.BianGlobalService'
            app.config["INIT_DATA_MAP"] = {'INIT_STATE': "Idle", 'PROP_URL':
                "C:\\dev\\projects\\halo\\halo_bian\\halo_bian\\env\\config\\bian_setting_mapping.json"}
            load_global_data(app.config["INIT_CLASS_NAME"], app.config["INIT_DATA_MAP"])
            self.x3 = X3()
            self.x3.bian_action = ActionTerms.FEEDBACK
            ret = self.x3.execute(bian_context,"x", {"sd_reference_id": self.session_id})
            assert ret.code == 200

    def test_99994_request_sub_returns_a_response(self):
        json = {
            "serviceDomainFeedbackActionTaskRecord": {},
            "serviceDomainFeedbackActionRecord": {
                "serviceDomainServicingSessionReference": "796678",
                "controlRecordInstanceReference": "724385",
                "behaviorQualifierInstanceReference": "789747",
                "feedbackRecordType": "string",
                "feedbackRecord": {}
            }
        }
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/deposits/1/?name=peter',
                headers={'x-bian-devparty': 'Your value'}, json=json):
            bian_context = client_util.get_halo_context(request.headers)
            self.x3 = X3()
            self.x3.bian_action = ActionTerms.FEEDBACK
            ret = self.x3.execute(bian_context,"x", {"sd_reference_id": self.session_id, "cr_reference_id": "2"})
            assert ret.code == 200

    def test_99995_request_sub_returns_a_response(self):
        json = {
            "serviceDomainFeedbackActionTaskRecord": {},
            "serviceDomainFeedbackActionRecord": {
                "serviceDomainServicingSessionReference": "796678",
                "controlRecordInstanceReference": "724385",
                "behaviorQualifierInstanceReference": "789747",
                "feedbackRecordType": "string",
                "feedbackRecord": {}
            }
        }
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/deposits/1/?name=peter',
                headers={'x-bian-devparty': 'Your value'}, json=json):
            bian_context = client_util.get_halo_context(request.headers)
            self.x3 = X3()
            self.x3.bian_action = ActionTerms.FEEDBACK
            ret = self.x3.execute(bian_context,"x", {"sd_reference_id": self.session_id, "cr_reference_id": "2",
                                                "bq_reference_id": "3"})
            assert ret.code == 200

    def test_99996_request_sub_returns_a_response(self):
        json = {
            "serviceDomainFeedbackActionTaskRecord": {},
            "serviceDomainFeedbackActionRecord": {
                "serviceDomainServicingSessionReference": "796678",
                "controlRecordInstanceReference": "724385",
                "behaviorQualifierInstanceReference": "789747",
                "feedbackRecordType": "string",
                "feedbackRecord": {}
            }
        }
        with app.test_request_context(
                '/consumer-loan/1/consumer-loan-fulfillment-arrangement/2/depositsandwithdrawals/3/deposits/1/?name=peter',
                headers={'x-bian-devparty': 'Your value'}, json=json):
            bian_context = client_util.get_halo_context(request.headers)
            self.x3 = X3()
            self.x3.bian_action = ActionTerms.FEEDBACK
            ret = self.x3.execute(bian_context,"x", {"sd_reference_id": self.session_id, "cr_reference_id": "2",
                                                "bq_reference_id": "3", "sbq_reference_id": "1"})
            assert ret.code == 200