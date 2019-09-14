#!/usr/bin/env python
import json
import re
from halo_flask.exceptions import ApiError,BadRequestError,HaloMethodNotImplementedException
from halo_flask.flask.mixinx import AbsBaseMixinX as AbsBaseMixin
from halo_flask.flask.utilx import Util
from halo_flask.flask.utilx import status
from halo_flask.logs import log_json
from halo_flask.apis import AbsBaseApi
from halo_flask.flask.mixinx import AbsApiMixinX

from halo_bian.bian.exceptions import *
from halo_bian.bian.bian import *
import importlib

settings = settingsx()

logger = logging.getLogger(__name__)


class AbsBianMixin(AbsApiMixinX):
    __metaclass__ = ABCMeta

    #bian data
    service_domain = None
    asset_type = None
    functional_pattern = None
    generic_artifact =None
    behavior_qualifier = None
    bian_action = None
    control_record = None
    service_operation = None

    #collection filter data
    filter_key_values = None
    filter_chars = None
    filter_sign = "sign"
    filter_key = "key"
    filter_val = "val"
    filter_separator = ";"
    #id masks
    cr_reference_id_mask = None
    bq_reference_id_mask = None

    def __init__(self):
        super(AbsBaseMixin, self).__init__()
        logger.debug("in __init__ ")
        if settings.SERVICE_DOMAIN:
            self.service_domain = settings.SERVICE_DOMAIN
        else:
            raise ServiceDomainNameException("missing Service Domain definition")
        if settings.ASSET_TYPE:
            self.asset_type = settings.ASSET_TYPE
        else:
            raise AssetTypeNameException("missing Asset Type definition")
        if settings.FUNCTIONAL_PATTERN:
            self.functional_pattern = settings.FUNCTIONAL_PATTERN
        else:
            raise FunctionalPatternNameException("missing Functional Pattern definition")
        if self.functional_pattern not in FunctionalPatterns.patterns.keys():
            raise FunctionalPatternNameException("Functional Pattern name not in list")
        if settings.GENERIC_ARTIFACT:
            self.generic_artifact = settings.GENERIC_ARTIFACT
        else:
            raise GenericArtifactNameException("missing GENERIC ARTIFACT definition")
        if settings.BEHAVIOR_QUALIFIER:
            self.behavior_qualifier = self.get_bq_obj()
        else:
            raise BehaviorQualifierNameException("missing Behavior Qualifier definition")
        if settings.CONTROL_RECORD:
            self.control_record = self.get_cr_obj()
        else:
            raise ControlRecordNameException("missing ControlRecord definition")

        if settings.FILTER_SEPARATOR:
            self.filter_separator = settings.FILTER_SEPARATOR
        if settings.CR_REFERENCE_ID_MASK:
            self.cr_reference_id_mask = settings.CR_REFERENCE_ID_MASK
        if settings.BQ_REFERENCE_ID_MASK:
            self.bq_reference_id_mask = settings.BQ_REFERENCE_ID_MASK

    def get_filter_char(self,bian_request, item):
        the_filter_chars = self.get_filter_chars(bian_request)
        if len(the_filter_chars) == 0:
            raise BadRequestError("no defined comperator for query collection-filter defined")
        for c in the_filter_chars:
            if c in item:
                return c
        raise BadRequestError("wrong comperator for query var collection-filter :"+item)

    def validate_collection_filter(self, bian_request):
        logger.debug("in validate_collection_filter ")
        if bian_request:
            if bian_request.collection_filter:
                for f in bian_request.collection_filter:
                    sign = self.get_filter_char(bian_request,f)
                    key = f.split(sign)[0].strip()
                    val = f.split(sign)[1].strip()
                    the_filter_chars = self.get_filter_chars(bian_request)
                    the_filter_key_values = self.get_filter_key_values(bian_request)
                    if sign not in the_filter_chars:
                        raise BadRequestError("filter sign for query var collection-filter is not allowed: " + sign)
                    if key not in the_filter_key_values.keys():
                        raise BadRequestError("filter key value for query var collection-filter is not allowed: " + key)
                    if not val:
                        raise BadRequestError("missing value for query var collection-filter")
        return True

    def break_filter(self,bian_request,f):
        if f:
            sign = self.get_filter_char(bian_request,f)
            key = f.split(sign)[0].strip()
            val = f.split(sign)[1].strip()
            return {self.filter_sign: sign, self.filter_key: key, self.filter_val: val}
        return None

    def check_in_filter(self,bian_request, filter_key):
        if bian_request:
            if bian_request.collection_filter:
                for f in bian_request.collection_filter:
                    if filter_key in f:
                        bf = self.break_filter(bian_request,f)
                        if bf != None and bf.key == filter_key:
                            return {self.filter_sign:bf.sign,self.filter_key:bf.key,self.filter_val:bf.val}
        return None

    def validate_cr_reference_id(self, bian_request):
        logger.debug("in validate_validate_cr_reference_id ")
        if bian_request:
            if bian_request.cr_reference_id and self.cr_reference_id_mask:
                if re.match(self.cr_reference_id_mask,bian_request.cr_reference_id):
                    return
                raise BadRequestError("cr_reference_id value is not of valid format:"+bian_request.cr_reference_id)

    def validate_bq_reference_id(self, bian_request):
        logger.debug("in validate_validate_bq_reference_id ")
        if bian_request:
            if bian_request.bq_reference_id and self.bq_reference_id_mask:
                if re.match(self.bq_reference_id_mask,bian_request.bq_reference_id):
                    return
                raise BadRequestError("bq_reference_id value is not of valid format:"+bian_request.bq_reference_id)

    def validate_filter_key_values(self):
        if self.filter_key_values:
            for bq in self.filter_key_values.keys():
                if bq is not None and bq not in self.behavior_qualifier.keys():
                    raise SystemBQIdException("bq in filter_key_values is not valid:"+bq)

    def validate_filter_chars(self):
        if self.filter_chars:
            for bq in self.filter_chars.keys():
                if bq is not None and bq not in self.behavior_qualifier.keys():
                    raise SystemBQIdException("bq in filter_chars is not valid:"+bq)

    def set_bian_action(self,action):
        self.bian_action = action

    def set_control_record(self, control_record):
        self.control_record = control_record
        #self.bian_service_info = BianServiceInfo(self.get_service_domain(), self.get_functional_pattern(),
        #                                         self.get_control_record())

    def get_control_record(self):
        return self.control_record

    def init_cr(self, ga_class_name):
        if settings.CONTROL_RECORD:
            k = settings.CONTROL_RECORD.rfind(".")
            module_name = settings.CONTROL_RECORD[:k]
            class_name = settings.CONTROL_RECORD[k+1:]
        else:
            module_name = "halo_bian.bian.bian"
            class_name = ga_class_name
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        if not issubclass(class_, ControlRecord):
            raise BianException("class error:"+class_name)
        instance = class_(settings.BEHAVIOR_QUALIFIER)
        return instance

    def get_cr_obj(self):
        cr_class = 'ControlRecord'
        cr_obj = self.init_cr(cr_class)
        return cr_obj

    def init_bq(self, bq_class_name):
        module = importlib.import_module("halo_bian.bian.bian")
        class_ = getattr(module, bq_class_name)
        instance = class_(settings.BEHAVIOR_QUALIFIER)
        return instance

    def get_bq_obj(self):
        bq_class = FunctionalPatterns.patterns[self.functional_pattern][1]
        bq_obj = self.init_bq(bq_class)
        return bq_obj

    def get_behavior_qualifier(self, op, bq):
        bq_obj = self.behavior_qualifier
        for bq_id in bq_obj.keys():
            bq_str = bq_obj.get(bq_id)
            if bq_str.lower() == bq.lower():
                return bq_str.strip().replace("-","_").replace(" ","_")
        raise IllegalBQException(bq)

    def get_behavior_qualifier_by_id(self, op, bq_id):
        bq_obj = self.behavior_qualifier
        if bq_id in bq_obj.keys():
            bq_str = bq_obj.get(bq_id)
            if bq_str:
                return bq_str.strip().replace("-","_").replace(" ","_")
        raise IllegalBQIdException(bq_id)

    def get_collection_filter(self, collection_filter):
        ret = None
        arr = []
        if collection_filter is not None:
            if self.filter_separator and self.filter_separator in collection_filter:
                arr = [x.strip() for x in collection_filter.split(self.filter_separator)]
            else:
                arr.append(collection_filter)
            ret = arr
        return ret

    def get_filter_key_values(self, bian_request):
        if bian_request:
            if bian_request.behavior_qualifier:
                if bian_request.behavior_qualifier in self.filter_key_values.keys():
                    return self.filter_key_values[bian_request.behavior_qualifier]
            if None in self.filter_key_values.keys():
                return self.filter_key_values[None]
        return {}

    def get_filter_chars(self, bian_request):
        if bian_request:
            if bian_request.behavior_qualifier:
                if bian_request.behavior_qualifier in self.filter_chars.keys():
                    return self.filter_chars[bian_request.behavior_qualifier]
            if self.filter_chars and None in self.filter_chars.keys():
                return self.filter_chars[None]
        return []

    def bian_validate_req(self, action, request, vars):
        logger.debug("in bian_validate_req " + str(action) + " vars=" + str(vars))
        action_term = action.upper()
        if action_term not in ActionTerms.ops:
            raise IllegalActionTermException(action)
        cr_reference_id = None
        behavior_qualifier = None
        bq_reference_id = None
        collection_filter = None
        if "cr_reference_id" in vars:
            cr_reference_id = vars["cr_reference_id"]
        if "behavior_qualifier" in vars:
            behavior_qualifier = self.get_behavior_qualifier(action_term, vars["behavior_qualifier"])
            # behavior_qualifier = self.get_behavior_qualifier_by_id(service_op, vars["bq_reference_id"])
        if "bq_reference_id" in vars:
            bq_reference_id = vars["bq_reference_id"]
        if "collection-filter" in request.args:
            collection_filter = self.get_collection_filter(request.args["collection-filter"])
        return BianRequest(action_term, request, cr_reference_id=cr_reference_id, bq_reference_id=bq_reference_id, behavior_qualifier=behavior_qualifier,collection_filter=collection_filter)

    def validate_req(self, bian_request):
        logger.debug("in validate_req ")
        if bian_request:
            self.validate_cr_reference_id(bian_request)
            self.validate_bq_reference_id(bian_request)
            self.validate_filter_key_values()
            self.validate_filter_chars()
            self.validate_collection_filter(bian_request)
            return True
        raise BianException("no Bian Request")

    def validate_pre(self, bian_request):
        return

    @staticmethod
    def set_back_api(bian_request,foi=None):
        logger.debug("in set_back_api "+str(foi))
        if foi:
            k = foi.rfind(".")
            module_name = foi[:k]
            class_name = foi[k + 1:]
            module = importlib.import_module(module_name)
            class_ = getattr(module, class_name)
            if not issubclass(class_, AbsBaseApi):
                raise BianException("class error:" + class_name)
            instance = class_(Util.get_req_context(bian_request.request))
            return instance
        return None

    @staticmethod
    def set_api_headers(bian_request,seq=None,dict=None):
        logger.debug("in set_api_headers ")
        if bian_request:
            return []
        raise BianException()

    @staticmethod
    def set_api_vars(bian_request,seq=None,dict=None):
        logger.debug("in set_api_vars " + str(bian_request))
        if True:
            ret = {}
            ret["bq"] = bian_request.behavior_qualifier
            ret["id"] = bian_request.cr_reference_id
            return ret
        raise BianException()

    @staticmethod
    def set_api_auth(bian_request,seq=None,dict=None):
        return None

    @staticmethod
    def set_api_data(bian_request,seq=None,dict=None):
        return bian_request.request.data

    @staticmethod
    def execute_api(bian_request, back_api, back_vars, back_headers,back_auth,back_data=None,seq=None,dict=None):
        logger.debug("in execute_api ")
        if back_api:
            timeout = Util.get_timeout(bian_request.request)
            try:
                ret = back_api.get(timeout)
                seq_msg = ""
                if seq:
                    seq_msg = "seq = "+seq+"."
                msg = "in execute_api. "+ seq_msg+" code= " + str(ret.status_code)
                logger.info(msg)
                return ret
            except ApiError as e:
                raise BianException(e)
        return None

    @staticmethod
    def extract_json(bian_request, back_response,seq=None):
        logger.debug("in extract_json ")
        if back_response:
            try:
                return json.loads(back_response.content)
            except json.decoder.JSONDecodeError as e:
                pass
        return json.loads("{}")

    def create_resp_payload(self, bian_request, dict_back_json):
        logger.debug("in create_resp_payload " + str(dict_back_json))
        if dict_back_json:
            return dict_back_json
        return {}

    # raise BianException()
    def set_resp_headers(self, bian_request, headers):
        logger.debug("in set_resp_headers " + str(headers))
        if headers:
            return []
        raise BianException()

    def validate_post(self, bian_request,bian_response):
        return

    def process_ok(self, response):
        if response:
            if response.request:
                if response.request.request:
                    if response.request.request.method == 'GET':
                        response.code = status.HTTP_200_OK
                    if response.request.request.method == 'POST':
                        response.code = status.HTTP_201_CREATED
                    if response.request.request.method == 'PUT':
                        response.code = status.HTTP_202_ACCEPTED
                    if response.request.request.method == 'PATCH':
                        response.code = status.HTTP_202_ACCEPTED
                    if response.request.request.method == 'DELETE':
                        response.code = status.HTTP_200_OK
                    logger.info('process_service_operation : '+response.request.request.method,
                                extra=log_json(Util.get_req_context(response.request.request),  {"return": "success"}))
                    return response
                raise ActionTermFailException(response.request.action_term)
        raise ActionTermFailException(response)

    def process_service_operation(self, action, request, vars):
        #logger.debug("in process_service_operation " + str(vars))
        logger.info('process_service_operation : ', extra=log_json(Util.get_req_context(request),vars,{"action":action}))
        bian_request = self.bian_validate_req(action, request, vars)
        functionName = {
            ActionTerms.INITIATE: self.do_initiate,
            ActionTerms.CREATE: self.do_create,
            ActionTerms.ACTIVATE: self.do_activate,
            ActionTerms.CONFIGURE: self.do_configure,
            ActionTerms.UPDATE: self.do_update,
            ActionTerms.REGISTER: self.do_register,
            ActionTerms.RECORD: self.do_record,
            ActionTerms.EXECUTE: self.do_execute,
            ActionTerms.EVALUATE: self.do_evaluate,
            ActionTerms.PROVIDE: self.do_provide,
            ActionTerms.AUTHORIZE: self.do_authorize,
            ActionTerms.REQUEST: self.do_request,
            ActionTerms.TERMINATE: self.do_terminate,
            ActionTerms.NOTIFY: self.do_notify,
            ActionTerms.RETRIEVE: self.do_retrieve
        }[bian_request.action_term]
        if bian_request.action_term in FunctionalPatterns.operations[self.functional_pattern]:
            bian_response = functionName(bian_request)
            return self.process_ok(bian_response)
        raise IllegalActionTermException(bian_request.action_term)

    def do_operation_bq1(self,bian_request):
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        try:
            behavior_qualifier = bian_request.behavior_qualifier.lower()
            # 1. validate input params
            getattr(self, 'validate_req_%s' % behavior_qualifier)(bian_request)
            # 2. Code to access the BANK API  to retrieve data - url + vars dict
            back_api = getattr(self, 'set_back_api_%s' % behavior_qualifier)(bian_request)
            # 3. array to store the headers required for the API Access
            back_headers = getattr(self, 'set_api_headers_%s' % behavior_qualifier)(bian_request)
            # 4. Sending the request to the BANK API with params
            back_vars = getattr(self, 'set_api_vars_%s' % behavior_qualifier)(bian_request)
            back_auth = getattr(self, 'set_api_auth_%s' % behavior_qualifier)(bian_request)
            if bian_request.request.method == 'POST' or bian_request.request.method == 'PUT':
                back_data = getattr(self, 'set_api_data_%s' % behavior_qualifier)(bian_request)
            else:
                back_data = None
            back_response = getattr(self, 'execute_api_%s' % behavior_qualifier)(bian_request, back_api, back_vars, back_headers, back_auth,back_data)
            # 5. extract from Response stored in an object built as per the BANK API Response body JSON Structure
            back_json = getattr(self, 'extract_json_%s' % behavior_qualifier)(bian_request,back_response)
            # 6. Build the payload target response structure which is IFX Compliant
            payload = getattr(self, 'create_resp_payload_%s' % behavior_qualifier)(bian_request,back_json)
            logger.debug("payload=" + str(payload))
            headers = getattr(self, 'set_resp_headers_%s' % behavior_qualifier)(bian_request,bian_request.request.headers)
            # 7. build json and add to bian response
            ret = BianResponse(bian_request, payload, headers)
            # return json response
            return ret
        except AttributeError as ex:
            raise HaloMethodNotImplementedException(ex)
    """
    def do_operation_bq(self,bian_request):
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        try:
            behavior_qualifier = bian_request.behavior_qualifier.lower()
            # 1. validate input params
            getattr(self, 'validate_req_%s' % behavior_qualifier)(bian_request)
            # 2. Code to access the BANK API  to retrieve data - url + vars dict
            getattr(self, 'validate_pre_%s' % behavior_qualifier)(bian_request)
            # 3. processing engine
            dict = self.processing_engine(bian_request,behavior_qualifier)
            # 4. Build the payload target response structure which is Compliant
            payload = getattr(self, 'create_resp_payload_%s' % behavior_qualifier)(bian_request, dict)
            logger.debug("payload=" + str(payload))
            # 5. setup headers for reply
            headers = getattr(self, 'set_resp_headers_%s' % behavior_qualifier)(bian_request,
                                                                                bian_request.request.headers)
            # 6. build json and add to bian response
            ret = BianResponse(bian_request, payload, headers)
            # 7. post condition
            getattr(self, 'validate_post_%s' % behavior_qualifier)(bian_request, ret)
            # return json response
            return ret
        except AttributeError as ex:
            raise BianMethodNotImplementedException(ex)

    def do_operation_1_bq(self, bian_request,behavior_qualifier):#basic maturity - single request
        logger.debug("do_operation_1_bq")
        if behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        logger.debug("do_operation_1")
        # 1. get api definition to access the BANK API  - url + vars dict
        back_api = getattr(self, 'set_back_api_%s' % behavior_qualifier)(bian_request)
        # 2. array to store the headers required for the API Access
        back_headers = getattr(self, 'set_api_headers_%s' % behavior_qualifier)(bian_request)
        # 3. set request params
        back_vars = getattr(self, 'set_api_vars_%s' % behavior_qualifier)(bian_request)
        # 4. Sset request auth
        back_auth = getattr(self, 'set_api_auth_%s' % behavior_qualifier)(bian_request)
        # 5. Sset request data
        if bian_request.request.method == 'POST' or bian_request.request.method == 'PUT':
            back_data = getattr(self, 'set_api_data_%s' % behavior_qualifier)(bian_request)
        else:
            back_data = None
        # 6. Sending the request to the BANK API with params
        back_response = getattr(self, 'execute_api_%s' % behavior_qualifier)(bian_request, back_api, back_vars, back_headers, back_auth, back_data)
        # 7. extract from Response stored in an object built as per the BANK API Response body JSON Structure
        back_json = getattr(self, 'extract_json_%s' % behavior_qualifier)(bian_request, back_response)
        dict = {1:back_json}
        # 8. return json response
        return dict

    def do_operation_2_bq(self,bian_request,behavior_qualifier):#medium maturity - foi
        logger.debug("do_operation_2_bq")
        dict = {}
        for seq in self.business_event.keys():
            # 1. get get first order interaction
            foi = self.business_event.get(seq)
            # 2. get api definition to access the BANK API  - url + vars dict
            back_api = getattr(self, 'set_back_api_%s' % behavior_qualifier)(bian_request,foi)
            # 3. array to store the headers required for the API Access
            back_headers = getattr(self, 'set_api_headers_%s' % behavior_qualifier)(bian_request,seq,dict)
            # 4. set vars
            back_vars = getattr(self, 'set_api_vars_%s' % behavior_qualifier)(bian_request,seq,dict)
            # 5. auth
            back_auth = getattr(self, 'set_api_auth_%s' % behavior_qualifier)(bian_request,seq,dict)
            # 6. set request data
            if bian_request.request.method == 'POST' or bian_request.request.method == 'PUT':
                back_data = getattr(self, 'set_api_data_%s' % behavior_qualifier)(bian_request,seq,dict)
            else:
                back_data = None
            # 7. Sending the request to the BANK API with params
            back_response = getattr(self, 'execute_api_%s' % behavior_qualifier)(bian_request, back_api, back_vars, back_headers, back_auth,back_data,seq,dict)
            # 8. extract from Response stored in an object built as per the BANK API Response body JSON Structure
            back_json = getattr(self, 'extract_json_%s' % behavior_qualifier)(bian_request,back_response,seq)
            # 9. store in dict
            dict[seq] = back_json
        return dict

    def do_operation(self,bian_request):
        # 1. validate input params
        self.validate_req(bian_request)
        # 2. run pre conditions
        self.validate_pre(bian_request)
        # 3. processing engine
        dict = self.processing_engine(bian_request)
        # 4. Build the payload target response structure which is Compliant
        payload = self.create_resp_payload(bian_request,dict)
        logger.debug("payload=" + str(payload))
        # 5. setup headers for reply
        headers = self.set_resp_headers(bian_request,bian_request.request.headers)
        # 6. build json and add to bian response
        ret = BianResponse(bian_request, payload, headers)
        # 7. post condition
        self.validate_post(bian_request,ret)
        # 8. return json response
        return ret

    def do_operation_1(self, bian_request):#basic maturity - single request
        logger.debug("do_operation_1")
        # 1. get api definition to access the BANK API  - url + vars dict
        back_api = self.__class__.set_back_api(bian_request)
        # 2. array to store the headers required for the API Access
        back_headers = self.__class__.set_api_headers(bian_request)
        # 3. set request params
        back_vars = self.__class__.set_api_vars(bian_request)
        # 4. Sset request auth
        back_auth = self.__class__.set_api_auth(bian_request)
        # 5. Sset request data
        if bian_request.request.method == 'POST' or bian_request.request.method == 'PUT':
            back_data = self.__class__.set_api_data(bian_request)
        else:
            back_data = None
        # 6. Sending the request to the BANK API with params
        back_response = self.__class__.execute_api(bian_request, back_api, back_vars, back_headers, back_auth, back_data)
        # 7. extract from Response stored in an object built as per the BANK API Response body JSON Structure
        back_json = self.__class__.extract_json(bian_request, back_response)
        dict = {1:back_json}
        # 8. return json response
        return dict

    def do_operation_2(self,bian_request):#medium maturity - foi
        logger.debug("do_operation_2")
        dict = {}
        for seq in self.business_event.keys():
            # 1. get get first order interaction
            foi = self.business_event.get(seq)
            # 2. get api definition to access the BANK API  - url + vars dict
            back_api = __class__.set_back_api(bian_request, foi)
            # 2. do api work
            back_json = self.__class__.do_api_work(bian_request,back_api,seq)
            # 3. store in dict
            dict[seq] = back_json
        return dict

    @staticmethod
    def do_api_work(bian_request,back_api,seq):
        # 3. array to store the headers required for the API Access
        back_headers = __class__.set_api_headers(bian_request, seq, dict)
        # 4. set vars
        back_vars = __class__.set_api_vars(bian_request, seq, dict)
        # 5. auth
        back_auth = __class__.set_api_auth(bian_request, seq, dict)
        # 6. set request data
        if bian_request.request.method == 'POST' or bian_request.request.method == 'PUT':
            back_data = __class__.set_api_data(bian_request, seq, dict)
        else:
            back_data = None
        # 7. Sending the request to the BANK API with params
        back_response = __class__.execute_api(bian_request, back_api, back_vars, back_headers, back_auth,
                                                   back_data, seq, dict)
        # 8. extract from Response stored in an object built as per the BANK API Response body JSON Structure
        back_json = __class__.extract_json(bian_request, back_response, seq)
        # return
        return  back_json

    def do_saga_work(self, api, results, payload):
        print("do_saga_work=" + str(api) + " result=" + str(results) +"payload="+str(payload))
        return __class__.do_api_work(payload['request'],api,payload['seq'])



    def do_operation_3(self, bian_request):  # high maturity - saga transactions
        logger.debug("do_operation_3")
        from halo_flask.saga import Saga,SagaRollBack,load_saga
        with open("C:\\dev\\projects\\halo\\halo_flask\\halo_flask\\tests\\schema.json") as f1:#settings.SAGA_SCHEMA_URL) as f1:
            schema = json.load(f1)
        sagax = load_saga("test", self.business_event.saga, schema)
        payloads = {}
        apis = {}
        counter = 1
        for state in self.business_event.saga["States"]:
            if 'Resource' in self.business_event.saga["States"][state]:
                api_name = self.business_event.saga["States"][state]['Resource']
                print(api_name)
                payloads[state]  = {"request":bian_request,'seq':str(counter)}
                apis[state] = self.do_saga_work
                counter = counter + 1

        #payloads = {"BookHotel": {"abc": "def"}, "BookFlight": {"abc": "def"}, "BookRental": {"abc": "def"},
        #            "CancelHotel": {"abc": "def"}, "CancelFlight": {"abc": "def"}, "CancelRental": {"abc": "def"}}
        #apis = {"BookHotel": self.create_api1, "BookFlight": self.create_api2, "BookRental": self.create_api3,
        #        "CancelHotel": self.create_api4, "CancelFlight": self.create_api5, "CancelRental": self.create_api6}
        try:
            ret = sagax.execute(Util.get_req_context(bian_request.request), payloads, apis)
            return ret
        except SagaRollBack as e:
            ret = HaloResponse()
            ret.payload = {"test": "bad"}
            ret.code = 500
            ret.headers = []
            return ret

    def processing_engine(self,bian_request,behavior_qualifier=None):
        if self.business_event:
            if self.business_event.get_business_event_type() == SAGA:
                if behavior_qualifier:
                    return self.do_operation_3_bq(bian_request,behavior_qualifier)
                return self.do_operation_3(bian_request)
            if self.business_event.get_business_event_type() == SEQ:
                if self.business_event.keys():
                    if behavior_qualifier:
                        return self.do_operation_2_bq(bian_request,behavior_qualifier)
                    return self.do_operation_2(bian_request)
                else:
                    raise BusinessEventMissingSeqException(self.service_operation)
        else:
            if behavior_qualifier:
                return self.do_operation_1_bq(bian_request,behavior_qualifier)
            return self.do_operation_1(bian_request)
    """
    def do_initiate_bq(self, bian_request):
        logger.debug("in do_initiate_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_initiate(self, bian_request):
        logger.debug("in do_initiate ")
        if bian_request.behavior_qualifier:
            return self.do_initiate_bq(bian_request)
        return self.do_operation(bian_request)

    def do_create_bq(self, bian_request):
        logger.debug("in do_create_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_create(self, bian_request):
        logger.debug("in do_create ")
        if bian_request.behavior_qualifier:
            return self.do_create_bq(bian_request)
        return self.do_operation(bian_request)

    def do_activate_bq(self, bian_request):
        logger.debug("in do_activate_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_activate(self, bian_request):
        logger.debug("in do_activate ")
        if bian_request.behavior_qualifier:
            return self.do_activate_bq(bian_request)
        return self.do_operation(bian_request)

    def do_configure_bq(self, bian_request):
        logger.debug("in do_configure_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_configure(self, bian_request):
        logger.debug("in do_configure ")
        if bian_request.behavior_qualifier:
            return self.do_configure_bq(bian_request)
        return self.do_operation(bian_request)

    def do_update_bq(self, bian_request):
        logger.debug("in do_update_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_update(self, bian_request):
        logger.debug("in do_update ")
        if bian_request.behavior_qualifier:
            return self.do_update_bq(bian_request)
        return self.do_operation(bian_request)

    def do_register_bq(self, bian_request):
        logger.debug("in do_register_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_register(self, bian_request):
        logger.debug("in do_register ")
        if bian_request.behavior_qualifier:
            return self.do_register_bq(bian_request)
        return self.do_operation(bian_request)

    def do_record_bq(self, bian_request):
        logger.debug("in do_record_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_record(self, bian_request):
        logger.debug("in do_record ")
        if bian_request.behavior_qualifier:
            return self.do_record_bq(bian_request)
        return self.do_operation(bian_request)

    def do_execute_bq(self, bian_request):
        logger.debug("in do_execute_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_execute(self, bian_request):
        logger.debug("in do_execute ")
        if bian_request.behavior_qualifier:
            return self.do_execute_bq(bian_request)
        return self.do_operation(bian_request)

    def do_evaluate_bq(self, bian_request):
        logger.debug("in do_evaluate_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_evaluate(self, bian_request):
        logger.debug("in do_evaluate ")
        if bian_request.behavior_qualifier:
            return self.do_evaluate_bq(bian_request)
        return self.do_operation(bian_request)

    def do_provide_bq(self, bian_request):
        logger.debug("in do_provide_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_provide(self, bian_request):
        logger.debug("in do_provide ")
        if bian_request.behavior_qualifier:
            return self.do_provide_bq(bian_request)
        return self.do_operation(bian_request)

    def do_authorize_bq(self, bian_request):
        logger.debug("in do_authorize_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_authorize(self, bian_request):
        logger.debug("in do_authorize ")
        if bian_request.behavior_qualifier:
            return self.do_authorize_bq(bian_request)
        return self.do_operation(bian_request)

    def do_request_bq(self, bian_request):
        logger.debug("in do_request_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_request(self, bian_request):
        logger.debug("in do_request ")
        if bian_request.behavior_qualifier:
            return self.do_request_bq(bian_request)
        return self.do_operation(bian_request)

    def do_terminate_bq(self, bian_request):
        logger.debug("in do_terminate_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_terminate(self, bian_request):
        logger.debug("in do_terminate ")
        if bian_request.behavior_qualifier:
            return self.do_terminate_bq(bian_request)
        return self.do_operation(bian_request)

    def do_notify_bq(self, bian_request):
        logger.debug("in do_notify_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_notify(self, bian_request):
        logger.debug("in do_notify ")
        if bian_request.behavior_qualifier:
            return self.do_notify_bq(bian_request)
        return self.do_operation(bian_request)

    def do_retrieve_bq(self, bian_request):
        logger.debug("in do_retrieve_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_retrieve(self, bian_request):
        logger.debug("in do_retrieve ")
        if bian_request.behavior_qualifier:
            return self.do_retrieve_bq(bian_request)
        return self.do_operation(bian_request)

    #get props

    def get_service_domain(self):
        return self.service_domain

    def get_functional_pattern(self):
        return self.functional_pattern

    def get_bian_info(self):
        return self.bian_service_info

    def get_service_status(self):
        return self.service_status

    def get_bian_action(self,default):
        action = default
        if self.bian_action:
            action = self.bian_action
        return action

    def set_bian_businss_event(self,request,bian_action):
       action = self.get_bian_action(bian_action)
       event_category = ActionTerms.categories[action]
       self.set_businss_event(request, event_category)
       return action




    #this is the http part

    def process_get(self, request, vars):
        logger.debug("sd=" + str(self.service_domain) + " in process_get " + str(vars))
        action = self.set_bian_businss_event(request,ActionTerms.RETRIEVE)
        return self.process_service_operation(action, request, vars)

    def process_post(self, request, vars):
        logger.debug("in process_post " + str(vars))
        action = self.set_bian_businss_event(request,ActionTerms.CREATE)
        return self.process_service_operation(action, request, vars)

    def process_put(self, request, vars):
        logger.debug("in process_put " + str(vars))
        action = self.set_bian_businss_event(request,ActionTerms.UPDATE)
        return self.process_service_operation(action, request, vars)

    def process_patch(self, request, vars):
        logger.debug("in process_patch " + str(vars))
        action = self.set_bian_businss_event(request,ActionTerms.UPDATE)
        return self.process_service_operation(action, request, vars)

    def process_delete(self, request, vars):
        logger.debug("in process_delete " + str(vars))
        action = self.set_bian_businss_event(request,ActionTerms.TERMINATE)
        return self.process_service_operation(action, request, vars)

#@TODO externelize all strings

class AbsBianSrvMixin(AbsBaseMixin):
    __metaclass__ = ABCMeta

    #service data
    service_properties = None
    service_status = None
    bian_service_info = None

    def __init__(self):
        super(AbsBaseMixin, self).__init__()
        logger.debug("in __init__ ")
        if settings.SERVICE_DOMAIN:
            service_domain = settings.SERVICE_DOMAIN
        else:
            raise ServiceDomainNameException("missing Service Domain definition")
        if settings.ASSET_TYPE:
            asset_type = settings.ASSET_TYPE
        else:
            raise AssetTypeNameException("missing Asset Type definition")
        if settings.FUNCTIONAL_PATTERN:
           functional_pattern = settings.FUNCTIONAL_PATTERN
        else:
           raise FunctionalPatternNameException("missing Functional Pattern definition")
        if functional_pattern not in FunctionalPatterns.patterns.keys():
            raise FunctionalPatternNameException("Functional Pattern name not in list")
        generic_artifact = FunctionalPatterns.patterns[functional_pattern][0]
        behavior_qualifier_type = FunctionalPatterns.patterns[functional_pattern][1]
        self.bian_service_info = BianServiceInfo(service_domain, asset_type, functional_pattern, generic_artifact, behavior_qualifier_type)


########################################
import flask_restful as restful
from halo_flask.flask.viewsx import AbsBaseLinkX
from halo_flask.const import HTTPChoice

class Resource(restful.Resource):
    pass

class InfoLinkX(Resource, AbsBianSrvMixin, AbsBaseLinkX):
    def process_get(self, request, vars):
        logger.debug("sd=" + str(self.bian_service_info.service_domain) + " in process_get " + str(vars))
        payload = {"service_domain":self.bian_service_info.get_service_domain(),"asset_type":self.bian_service_info.get_asset_type()}
        return BianResponse(request, payload, {})

    def get(self):
        ret = self.do_process(HTTPChoice.get)
        return Util.json_data_response(ret.payload, ret.code, ret.headers)

    def post(self):
        ret = self.do_process(HTTPChoice.post)
        return Util.json_data_response(ret.payload, ret.code, ret.headers)

    def put(self):
        ret = self.do_process(HTTPChoice.put)
        return Util.json_data_response(ret.payload, ret.code, ret.headers)

    def delete(self):
        ret = self.do_process(HTTPChoice.delete)
        return Util.json_data_response(ret.payload, ret.code, ret.headers)