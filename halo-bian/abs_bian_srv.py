#!/usr/bin/env python
import json
import logging

from halolib.flask.mixinx import AbsBaseMixinX as AbsBaseMixin
from halolib.flask.utilx import Util
from halolib.settingsx import settingsx

try:
    from halolib.flask.utilx import status
except:
    try:
        from halolib.util import status
    except:
        pass
# flask

settings = settingsx()

logger = logging.getLogger(__name__)

from bian import *


class AbsBianMixin(AbsBaseMixin):
    __metaclass__ = ABCMeta

    service_domain = None
    service_properties = None
    service_status = None
    control_record = None
    functional_pattern = None
    bian_service_info = None

    def __init__(self):
        super(AbsBaseMixin, self).__init__()
        self.service_domain = settings.SERVICE_DOMAIN
        self.functional_pattern = settings.FUNCTIONAL_PATTERN
        self.bian_service_info = BianServiceInfo(self.service_domain, self.functional_pattern,
                                                 self.get_control_record())

    def set_control_record(self, control_record):
        self.control_record = control_record
        self.bian_service_info = BianServiceInfo(self.get_service_domain(), self.get_functional_pattern(),
                                                 self.get_control_record())

    def get_control_record(self):
        return self.control_record

    def bian_validate_req(self, action, request, vars):
        logger.debug("in bian_validate_req " + str(action) + " vars=" + str(vars))
        service_op = action.upper()
        if service_op not in ServiceOperations.ops:
            raise IllegalServiceOperationException(action)
        behavior_qualifier = None
        cr_reference_id = None
        if "behavior_qualifier" in vars:
            behavior_qualifier = vars["behavior_qualifier"]
        if "cr_reference_id" in vars:
            cr_reference_id = vars["cr_reference_id"]
        return BianRequest(service_op, behavior_qualifier, cr_reference_id, request)

    # raise BianException()

    def validate_req(self, bianRequest):
        logger.debug("in validate_req ")
        if bianRequest:
            return True
        raise BianException()

    def set_back_api(self):
        logger.debug("in set_back_api ")
        return None

    # raise BianException()
    def set_api_headers(self, request):
        logger.debug("in set_api_headers ")
        if request:
            return []
        raise BianException()

    def set_api_vars(self, bq, id):
        logger.debug("in set_api_vars " + str(bq) + " " + str(id))
        if True:
            ret = {}
            ret["bq"] = bq
            ret["id"] = id
            return ret
        raise BianException()

    def execute_api(self, bianRequest, back_api, back_vars, back_headers):
        logger.debug("in execute_api ")
        if back_api:
            timeout = Util.get_timeout(bianRequest.request)
            try:
                ret = back_api.get(timeout)
                return ret
            except ApiError as e:
                raise BianException(e)
        return None

    # raise BianException()
    def extract_json(self, back_response):
        logger.debug("in extract_json ")
        if back_response:
            return json.loads(back_response.content)
        return json.loads("{}")

    # raise BianException()
    def create_resp_payload(self, back_json):
        logger.debug("in create_resp_payload " + str(back_json))
        if back_json:
            return back_json
        return back_json

    # raise BianException()
    def set_resp_headers(self, headers):
        logger.debug("in set_resp_headers " + str(headers))
        if headers:
            return []
        raise BianException()

    def process_ok(self, response):
        if response:
            if response.bian_request:
                if response.bian_request.request:
                    if response.bian_request.request.method == 'get':
                        response.code = status.HTTP_200_OK
                    if response.bian_request.request.method == 'post':
                        response.code = status.HTTP_201_CREATED
                    if response.bian_request.request.method == 'put':
                        response.code = status.HTTP_202_ACCEPTED
                    if response.bian_request.request.method == 'patch':
                        response.code = status.HTTP_202_ACCEPTED
                    if response.bian_request.request.method == 'delete':
                        response.code = status.HTTP_200_OK
                    return response
        raise ServiceOperationFailException(response)

    def process_service_operation(self, action, request, vars):
        logger.debug("in process_service_operation " + str(vars))
        bian_request = self.bian_validate_req(action, request, vars)
        functionName = {
            ServiceOperations.INITIATE: self.do_initiate,
            ServiceOperations.CREATE: self.do_create,
            ServiceOperations.ACTIVATE: self.do_activate,
            ServiceOperations.CONFIGURE: self.do_configure,
            ServiceOperations.UPDATE: self.do_update,
            ServiceOperations.REGISTER: self.do_register,
            ServiceOperations.RECORD: self.do_record,
            ServiceOperations.EXECUTE: self.do_execute,
            ServiceOperations.EVALUATE: self.do_evaluate,
            ServiceOperations.PROVIDE: self.do_provide,
            ServiceOperations.AUTHORIZE: self.do_authorize,
            ServiceOperations.REQUEST: self.do_request,
            ServiceOperations.TERMINATE: self.do_terminate,
            ServiceOperations.NOTIFY: self.do_notify,
            ServiceOperations.RETRIEVE: self.do_retrieve
        }[bian_request.service_operation]
        if bian_request.service_operation in FunctionalPatterns.operations[self.functional_pattern]:
            bian_response = functionName(bian_request)
            return self.process_ok(bian_response)
        raise IllegalServiceOperationException(bian_request.service_operation)

    def do_initiate(self, bianRequest):
        pass

    def do_create(self, bianRequest):
        pass

    def do_activate(self, bianRequest):
        pass

    def do_configure(self, bianRequest):
        pass

    def do_update(self, bianRequest):
        pass

    def do_register(self, bianRequest):
        pass

    def do_record(self, bianRequest):
        pass

    def do_execute(self, bianRequest):
        pass

    def do_evaluate(self, bianRequest):
        pass

    def do_provide(self, bianRequest):
        pass

    def do_authorize(self, bianRequest):
        pass

    def do_request(self, bianRequest):
        pass

    def do_terminate(self, bianRequest):
        pass

    def do_notify(self, bianRequest):
        pass

    def do_retrieve(self, bian_request):
        logger.debug("in do_retrieve ")
        # 1. validate in params
        self.validate_req(bian_request)
        # 2. Code to access the BANK API  to retrieve data - url + vars dict
        back_api = self.set_back_api()
        # 3. array to store the headers required for the API Access
        back_headers = self.set_api_headers(bian_request.request)
        # 4. Sending the request to the BANK API with params
        back_vars = self.set_api_vars(bian_request.behaviorQualifier, bian_request.referenceId)
        back_response = self.execute_api(bian_request, back_api, back_vars, back_headers)
        # 5. extract from Response stored in an object built as per the BANK API Response body JSON Structure
        back_json = self.extract_json(back_response)
        # 6. Build the payload target response structure which is IFX Compliant
        payload = self.create_resp_payload(back_json)
        logger.debug("payload=" + str(payload))
        headers = self.set_resp_headers(bian_request.request.headers)
        # 7. build json and add to bian response
        ret = BianResponse(bian_request, payload, headers)
        # 8. return json response
        return ret

    def get_service_domain(self):
        return self.service_domain

    def get_functional_pattern(self):
        return self.functional_pattern

    def get_bian_info(self):
        return self.bian_service_info

    def get_service_status(self):
        return self.service_status

    def process_get(self, request, vars):
        logger.debug("sd=" + str(self.service_domain) + " in process_get " + str(vars))
        action = "retrieve"
        return self.process_service_operation(action, request, vars)

    def process_post(self, request, vars):
        logger.debug("in process_post " + str(vars))
        action = "create"
        return self.process_service_operation(action, request, vars)

    def process_put(self, request, vars):
        logger.debug("in process_put " + str(vars))
        action = "update"
        return self.process_service_operation(action, request, vars)

    def process_patch(self, request, vars):
        logger.debug("in process_patch " + str(vars))
        action = "update"
        return self.process_service_operation(action, request, vars)

    def process_delete(self, request, vars):
        logger.debug("in process_delete " + str(vars))
        action = "terminate"
        return self.process_service_operation(action, request, vars)
