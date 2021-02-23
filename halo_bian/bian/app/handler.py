#!/usr/bin/env python
import json
import re
import logging
from abc import ABCMeta,abstractmethod
import importlib

from halo_app.app.context import HaloContext
from halo_app.app.notification import Notification
from halo_app.app.request import HaloEventRequest, HaloQueryRequest
from halo_app.app.uow import AbsUnitOfWork
from halo_app.app.exceptions import HaloMethodNotImplementedException, AppException
from halo_app.app.utilx import Util
from halo_app.logs import log_json
from halo_app.infra.apis import AbsBaseApi
from halo_app.app.handler import AbsCommandHandler, AbsBaseHandler, AbsEventHandler, AbsQueryHandler
from halo_app.app.anlytx_filter import RequestFilter
from halo_app.reflect import Reflect
from halo_app.settingsx import settingsx
from halo_app.models import AbsDbMixin

from halo_bian.bian.app.context import BianContext
from halo_bian.bian.exceptions import *
from halo_bian.bian.bian import *
from halo_app.ssm import get_app_config
from halo_app.infra.exceptions import CacheKeyException
from halo_app.ssm import set_app_param_config,get_app_param_config

from halo_bian.bian.app.request import BianCommandRequest, BianEventRequest
from halo_bian.bian.app.response import BianResponse
from halo_bian.bian.util import BianUtil

settings = settingsx()

logger = logging.getLogger(__name__)

#@todo add jsonify to all responses
#@todo support for microservices break down of service domain

SESSION_ID = "session_id"
STATE = "state"

class AbsBianHandler(AbsBaseHandler):
    __metaclass__ = ABCMeta

    #bian data
    service_domain = None
    asset_type = None
    functional_pattern = None
    generic_artifact = None
    behavior_qualifier_type = None
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
    sd_reference_id_mask = None
    cr_reference_id_mask = None
    bq_reference_id_mask = None
    #service state
    service_state = None
    servicing_session = None


    def __init__(self):
        super(AbsBianHandler, self).__init__()
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
            self.behavior_qualifier_type = BianUtil.get_bq_obj()
        else:
            raise BehaviorQualifierNameException("missing Behavior Qualifier definition")
        if settings.CONTROL_RECORD:
            self.control_record = self.get_cr_obj(self.behavior_qualifier_type)
        else:
            raise ControlRecordNameException("missing ControlRecord definition")

        if settings.FILTER_SEPARATOR:
            self.filter_separator = settings.FILTER_SEPARATOR
        if settings.SD_REFERENCE_ID_MASK:
            self.sd_reference_id_mask = settings.SD_REFERENCE_ID_MASK
        if settings.CR_REFERENCE_ID_MASK:
            self.cr_reference_id_mask = settings.CR_REFERENCE_ID_MASK
        if settings.BQ_REFERENCE_ID_MASK:
            self.bq_reference_id_mask = settings.BQ_REFERENCE_ID_MASK
        if settings.SERVICING_SESSION:
            self.service_state = BianGlobalService.get_service_state()
            if not self.service_state:
                raise ServiceStateException("missing service state")
            self.servicing_session = BianGlobalService.get_service_session()

    def get_filter_char(self,bian_request, item):
        the_filter_chars = self.get_filter_chars(bian_request)
        if len(the_filter_chars) == 0:
            raise AppException("no defined comperator for query collection-filter defined")
        for c in the_filter_chars:
            if c in item:
                return c
        raise AppException("wrong comperator for query var collection-filter :"+item)

    def validate_collection_filter(self, bian_request,notification):
        #@todo check filter validation works
        logger.debug("in validate_collection_filter ")
        if bian_request:
            if hasattr(bian_request, 'collection_filter') and bian_request.collection_filter:
                the_filter_chars = self.get_filter_chars(bian_request)
                the_filter_key_values = self.get_filter_key_values(bian_request)
                for f in bian_request.collection_filter:
                    sign = f.op
                    key = f.field
                    val = f.value
                    if sign not in the_filter_chars:
                        raise AppException("filter sign for query var collection-filter is not allowed: " + sign)
                    if key not in the_filter_key_values.keys():
                        raise AppException("filter key value for query var collection-filter is not allowed: " + key)
                    if not val:
                        raise AppException("missing value for query var collection-filter")

    def validate_queryparams(self, bian_request,notification):
        #@todo check filter validation works
        logger.debug("in validate_collection_filter ")
        if bian_request:
            if hasattr(bian_request, 'collection_filter') and bian_request.collection_filter:
                the_filter_chars = self.get_filter_chars(bian_request)
                the_filter_key_values = self.get_filter_key_values(bian_request)
                for f in bian_request.collection_filter:
                    sign = f.op
                    key = f.field
                    val = f.value
                    if sign not in the_filter_chars:
                        raise AppException("filter sign for query var collection-filter is not allowed: " + sign)
                    if key not in the_filter_key_values.keys():
                        raise AppException("filter key value for query var collection-filter is not allowed: " + key)
                    if not val:
                        raise AppException("missing value for query var collection-filter")

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

    def validate_sd_reference_id(self, bian_request,notification):
        logger.debug("in validate_sd_reference_id ")
        if bian_request:
            if bian_request.sd_reference_id:
                if self.sd_reference_id_mask:
                    if not re.match(self.sd_reference_id_mask,bian_request.sd_reference_id):
                        notification.addError("sd_reference_id value is not of valid format:"+bian_request.sd_reference_id)
                        #raise AppException("sd_reference_id value is not of valid format:"+bian_request.sd_reference_id)
                if settings.SERVICING_SESSION:
                    if self.servicing_session:
                        if bian_request.sd_reference_id != self.servicing_session.get_session_id():
                            raise AppException("sd_reference_id value is not valid:" + bian_request.sd_reference_id)
                    else:
                        raise AppException("no service session available:" + bian_request.sd_reference_id)

    def validate_cr_reference_id(self, bian_request,notification):
        logger.debug("in validate_validate_cr_reference_id ")
        if bian_request:
            if bian_request.cr_reference_id and self.cr_reference_id_mask:
                if re.match(self.cr_reference_id_mask,bian_request.cr_reference_id):
                    return
                notification.addError("cr_reference_id value is not of valid format:"+bian_request.cr_reference_id)
                #raise AppException("cr_reference_id value is not of valid format:"+bian_request.cr_reference_id)

    def validate_bq_reference_id(self, bian_request,notification):
        logger.debug("in validate_validate_bq_reference_id ")
        if bian_request:
            if bian_request.bq_reference_id and self.bq_reference_id_mask:
                if re.match(self.bq_reference_id_mask,bian_request.bq_reference_id):
                    return
                notification.addError("bq_reference_id value is not of valid format:"+bian_request.bq_reference_id)
                #raise AppException("bq_reference_id value is not of valid format:"+bian_request.bq_reference_id)

    def validate_service_state(self,bian_request):
        if self.service_state:
            if self.service_state.get_current_state() and self.service_state.get_current_state().allows(bian_request.action_term):
                return True
            raise ServiceNotOpenException("Service not open for processing ")
        raise ServiceStateException("missing Service State ")

    def set_bian_action(self,action:ActionTerms):
        self.bian_action = action

    def set_control_record(self, control_record):
        self.control_record = control_record
        #self.bian_service_info = BianServiceInfo(self.get_service_domain(), self.get_functional_pattern(),
        #                                         self.get_control_record())

    def get_control_record(self):
        return self.control_record

    def init_cr(self, cr_class_name, behavior_qualifier_type=None, init_vars=None):
        if settings.CONTROL_RECORD:
            k = settings.CONTROL_RECORD.rfind(".")
            module_name = settings.CONTROL_RECORD[:k]
            class_name = settings.CONTROL_RECORD[k+1:]
        else:
            module_name = "halo_bian.bian.bian"
            class_name = cr_class_name
        return Reflect.do_instantiate(module_name,class_name,GenericArtifact,behavior_qualifier_type)

    def init_cr1(self, cr_class_name,behavior_qualifier_type=None,init_vars=None):
        if settings.CONTROL_RECORD:
            k = settings.CONTROL_RECORD.rfind(".")
            module_name = settings.CONTROL_RECORD[:k]
            class_name = settings.CONTROL_RECORD[k+1:]
        else:
            module_name = "halo_bian.bian.bian"
            class_name = cr_class_name
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        if not issubclass(class_, GenericArtifact):
            raise BianException("CONTROL RECORD class error:"+class_name)
        instance = class_(behavior_qualifier_type)#init_vars)
        return instance

    def get_cr_obj(self,behavior_qualifier_type=None,init_var=None):
        cr_class = 'ControlRecord'
        cr_obj = self.init_cr(cr_class,behavior_qualifier_type,init_var)
        return cr_obj

    def init_ga(self, ga_class_name, init_var=None):
        if settings.GENERIC_ARTIFACT:
            k = settings.GENERIC_ARTIFACT.rfind(".")
            module_name = settings.GENERIC_ARTIFACT[:k]
            class_name = settings.GENERIC_ARTIFACT[k+1:]
        else:
            module_name = "halo_bian.bian.bian"
            class_name = ga_class_name
        return Reflect.do_instantiate(module_name, class_name, GenericArtifact, init_var)


    def init_ga1(self, ga_class_name,init_var=None):
        if settings.GENERIC_ARTIFACT:
            k = settings.GENERIC_ARTIFACT.rfind(".")
            module_name = settings.GENERIC_ARTIFACT[:k]
            class_name = settings.GENERIC_ARTIFACT[k+1:]
        else:
            module_name = "halo_bian.bian.bian"
            class_name = ga_class_name
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        if not issubclass(class_, GenericArtifact):
            raise BianException("GENERIC ARTIFACT class error:"+class_name)
        instance = class_(init_var)
        return instance

    def get_ga_obj(self,init_var=None):
        ga_class = 'GenericArtifact'
        ga_obj = self.init_cr(ga_class,init_var)
        return ga_obj

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

    def validate_match(self, bian_request,notification):
        if bian_request.action_term != self.bian_action:
            notification.addError("request action:"+str(bian_request.action_term)+" -> handler action:"+str(self.bian_action))
            #raise BianMethodMisMatch("request action:"+str(bian_request.action_term)+" -> handler action:"+str(self.bian_action))
        #if bian_request.method_id != self.method_id:
        #    raise BianMethodMisMatch(
        #        "request method:" + str(bian_request.method_id) + " -> handler method:" + str(self.method_id))

    def validate_req(self, bian_request):
        logger.debug("in validate_req ")
        if bian_request:
            notification:Notification = Notification()
            self.validate_match(bian_request,notification)
            self.validate_sd_reference_id(bian_request,notification)
            self.validate_cr_reference_id(bian_request,notification)
            self.validate_bq_reference_id(bian_request,notification)
            self.validate_collection_filter(bian_request,notification)
            self.validate_queryparams(bian_request, notification)
            # admin work
            if settings.SERVICING_SESSION:
                self.validate_service_state(bian_request)
            return notification

    def get_request_filter(self,halo_request):
        logger.debug("get_request_filter for bian")
        filter = super(AbsBianHandler, self).get_request_filter(halo_request)
        filter.set(self)
        return filter

    def process_ok(self, halo_response):
        return halo_response

    def do_bian_operation(self, bian_request):
        #pre = self.do_pre(bian_request)
        return self.do_operation(bian_request)
        #post = self.do_post(pre,op)
        #return post

    def process_service_operation(self, bian_request):
        #logger.debug("in process_service_operation " + str(vars))
        logger.info('process_service_operation : ', extra=log_json(bian_request.context,{},{"action":bian_request.action_term}))
        functionName = {
            ActionTerms.INITIATE: self.do_initiate,
            ActionTerms.CREATE: self.do_create,
            ActionTerms.ACTIVATE: self.do_activate,
            ActionTerms.CONFIGURE: self.do_configure,
            ActionTerms.UPDATE: self.do_update,
            ActionTerms.REGISTER: self.do_register,
            #ActionTerms.RECORD: self.do_record,
            ActionTerms.EXECUTE: self.do_execute,
            ActionTerms.EVALUATE: self.do_evaluate,
            ActionTerms.PROVIDE: self.do_provide,
            #ActionTerms.AUTHORIZE: self.do_authorize,
            ActionTerms.REQUEST: self.do_request,
            #ActionTerms.TERMINATE: self.do_terminate,
            ActionTerms.NOTIFY: self.do_notify,
            ActionTerms.RETRIEVE: self.do_retrieve,
            #new
            ActionTerms.CAPTURE: self.do_capture,
            ActionTerms.CONTROL: self.do_control,
            ActionTerms.EXCHANGE: self.do_exchange,
            ActionTerms.GRANT: self.do_grant,
            ActionTerms.FEEDBACK: self.do_feedback
        }[bian_request.action_term]
        if bian_request.action_term in FunctionalPatterns.operations[self.functional_pattern]:
            bian_response = functionName(bian_request)
            return self.process_ok(bian_response)
        raise IllegalActionTermException(bian_request.action_term)

    def do_initiate(self, bian_request):
        logger.debug("in do_initiate ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    #@todo implement common create action logic
    def do_create(self, bian_request):
        logger.debug("in do_create ")
        return self.do_bian_operation(bian_request)

    def do_activate(self, bian_request):
        logger.debug("in do_activate ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_configure(self, bian_request):
        logger.debug("in do_configure ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_update(self, bian_request):
        logger.debug("in do_update ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_register(self, bian_request):
        logger.debug("in do_register ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_record(self, bian_request):
        logger.debug("in do_record ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_execute(self, bian_request):
        logger.debug("in do_execute ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_evaluate(self, bian_request):
        logger.debug("in do_evaluate ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_provide(self, bian_request):
        logger.debug("in do_provide ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_authorize(self, bian_request):
        logger.debug("in do_authorize ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_request(self, bian_request):
        logger.debug("in do_request ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_terminate(self, bian_request):
        logger.debug("in do_terminate ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_command_bq(self, bian_request):
        logger.debug("in do_notify_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_notify(self, bian_request):
        logger.debug("in do_notify ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_query_bq(self, bian_request):
        logger.debug("in do_retrieve_bq ")
        if bian_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        return self.do_operation_bq(bian_request)

    def do_retrieve(self, bian_request):
        logger.debug("in do_retrieve ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_capture(self, bian_request):
        logger.debug("in do_capture ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_control(self, bian_request):
        logger.debug("in do_capture ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_exchange(self, bian_request):
        logger.debug("in do_capture ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_grant(self, bian_request):
        logger.debug("in do_capture ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    def do_feedback(self, bian_request):
        logger.debug("in do_capture ")
        if bian_request.behavior_qualifier:
            return self.do_operation_bq(bian_request)
        return self.do_bian_operation(bian_request)

    #@todo get original back to use
    def do_operation_bq(self,bian_request):
        return self.do_bian_operation(bian_request)

    #@todo replace importlib with reflect
    def set_back_api(self, halo_request, foi=None):
        logger.debug("in set_back_api " + str(foi))
        if foi:
            foi_name = foi["name"]
            if not foi_name.startswith('bian.'):
                return super(AbsBianHandler, self).set_back_api(halo_request, foi)
            foi_op = foi["op"]
            sd_class_name,sd_module_name,sd_base_url = self.get_api_from_sd(foi_name)
            module = importlib.import_module(sd_module_name)
            class_ = getattr(module, sd_class_name)
            if not issubclass(class_, AbsBaseApi):
                from halo_app.exceptions import ApiClassErrorException
                raise ApiClassErrorException(sd_class_name)
            instance = class_(halo_request.context)
            instance.op = foi_op
            instance.set_api_base(sd_base_url)
            return instance
        from halo_app.infra.exceptions import NoApiClassException
        raise NoApiClassException("api class not defined")

    def get_api_from_sd(self, foi_name):
        k = foi_name.rfind(".")
        module_name = foi_name[:k]
        class_name = foi_name[k + 1:]
        sd_name = module_name.replace("bian.","")
        sd = settings.SERVICE_DOMAINS[sd_name]
        sd_url = sd["details"]["url"]
        sd_api_name = sd["api"][class_name]
        k = sd_api_name.rfind(".")
        sd_module_name = sd_api_name[:k]
        sd_class_name = sd_api_name[k + 1:]
        return sd_class_name,sd_module_name,sd_url

    def set_api_vars(self, bian_request,api, seq=None, dict=None):
        logger.debug("in set_api_vars " + str(bian_request))
        ret = {}
        ret["sd_reference_id"] = bian_request.sd_reference_id
        ret["behavior_qualifier"] = bian_request.behavior_qualifier
        ret["cr_reference_id"] = bian_request.cr_reference_id
        ret["bq_reference_id"] = bian_request.bq_reference_id
        if hasattr(bian_request, 'collection_filter'):
            ret["collection_filter"] = bian_request.collection_filter
        if hasattr(bian_request, 'body'):
            ret["body"] = bian_request.body
        ret = self.set_added_api_vars(bian_request,ret, seq, dict)
        return ret

    def set_added_api_vars(self, bian_request,vars, seq=None, dict=None):
        logger.debug("in set_api_vars " + str(bian_request))
        return vars

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

    def set_bian_business_event(self,request,bian_action):
       event_category = ActionTerms.categories[bian_action]
       self.set_business_event(request, event_category)

    def process_bian_request(self,bian_request):
        logger.debug("sd=" + str(self.service_domain))
        self.set_bian_business_event(bian_request, bian_request.action_term)
        return self.process_service_operation(bian_request)

class AbsBianCommandHandler(AbsBianHandler,AbsCommandHandler):

    def __run_command(self,bian_request:HaloCommandRequest,uow:AbsUnitOfWork)->AbsHaloResponse:
        self.uow = uow
        return self.process_bian_request(bian_request)

    @classmethod
    def run_command_class(cls, halo_request: HaloCommandRequest, uow: AbsUnitOfWork) -> AbsHaloResponse:
        handler = cls()
        return handler.__run_command(halo_request, uow)

class AbsBianEventHandler(AbsBianHandler,AbsEventHandler):
    #def set_bian_business_event(self,bian_request, action_term):
    #    return None

    def __run_event(self, bian_request: HaloEventRequest,uow:AbsUnitOfWork):
        self.uow = uow
        return self.process_bian_request(bian_request)

    @classmethod
    def run_event_class(cls, halo_request: HaloEventRequest, uow: AbsUnitOfWork) -> AbsHaloResponse:
        handler = cls()
        return handler.__run_event(halo_request, uow)

class AbsBianQueryHandler(AbsBianHandler,AbsQueryHandler):

    def __run_query(self, bian_request: HaloQueryRequest,uow:AbsUnitOfWork):
        self.uow = uow
        return self.process_bian_request(bian_request)

    @classmethod
    def run_query_class(cls, halo_request: HaloQueryRequest, uow: AbsUnitOfWork) -> AbsHaloResponse:
        handler = cls()
        return handler.__run_query(halo_request, uow)

#@TODO externelize all strings
#@todo add log print of the method name and add x-header with method name to headers
#@todo api finish authorization issues : curl -v -u "admin:secret" http://127.0.0.1:5000/secrets
# service management

class AbsBianSrvMixin(AbsBianCommandHandler):
    __metaclass__ = ABCMeta

    #service data
    service_configuration = None
    #bian_service_info = None

    def __init__(self):
        super(AbsBianSrvMixin, self).__init__()
        logger.debug("in __init__ ")
        #self.bian_service_info = BianServiceInfo(self.service_domain, self.asset_type, self.functional_pattern, self.generic_artifact, self.behavior_qualifier_type)
        self.service_configuration = BianGlobalService.get_service_properties()
        self.service_state = BianGlobalService.get_service_state()


class ActivationAbsBianMixin(AbsBianSrvMixin):
    __metaclass__ = ABCMeta

    bian_action = ActionTerms.ACTIVATE

    def process_request(self, bian_request):
        data = {}
        if 'body' in bian_request.command.vars:
            data = bian_request.command.vars['body']
        self.center_id = data["serviceDomainCenterReference"]
        self.service_id = data["serviceDomainServiceReference"]
        self.configuration_setting_id = data["serviceDomainServiceConfigurationRecord"][
            "serviceDomainServiceConfigurationSettingReference"]
        param_type = data["serviceDomainServiceConfigurationRecord"][
            "serviceDomainServiceConfigurationSettingType"]
        param_value = data["serviceDomainServiceConfigurationRecord"][
            "serviceDomainServiceConfigurationSetup"]["serviceDomainServiceConfigurationParameter"]
        if self.service_configuration.get_configuration_setting(self.configuration_setting_id):
            self.service_configuration.get_configuration_setting(self.configuration_setting_id).set_value(param_type,param_value)
        self.service_state.set_new_state(self.service_state.Active)
        self.servicing_session = BianServicingSession(None,self.center_id,self.service_id,self.service_configuration,self.service_state)
        self.persist_servicing_session(bian_request,self.servicing_session)
        global global_service_session
        global_service_session = self.servicing_session

    def persist_servicing_session(self,bian_request, servicing_session):
        #@todo implement persistance
        """Method documentation"""
        #dbaccess = self.get_dbaccess(bian_request)
        #dbaccess.save_servicing_session(servicing_session)
        params = {}
        params[SESSION_ID] = self.get_session_id()
        params[STATE] = self.service_state.get_current_state().state_name
        set_app_param_config(settings.SSM_TYPE, params)
        #set_app_param_config(settings.SSM_TYPE, SESSION_ID, self.get_session_id())
        #set_app_param_config(settings.SSM_TYPE, STATE, self.service_state.get_current_state().state_name)
        return

    def get_activation_id(self):
        return ""

    def get_activation_rec(self):
        return ""

    def get_session_id(self):
        return self.servicing_session.get_session_id()

    def get_session_rec(self):
        return ""

    def get_configuration_setting_id(self):
        return self.configuration_setting_id

    def get_configuration_desc(self):
        return ""

    def get_configuration_param(self):
        return ""

    def get_subscriber_id(self):
        return ""

    def get_subscriber_access(self):
        return ""

    def get_agreement_id(self):
        return ""

    def get_agree_terms(self):
        return ""

    def get_sdservice_status(self):
        return ""

    def get_user_id(self):
        return ""

    def get_session_status(self):
        return ""

    def do_operation_1(self,bian_request):
        logger.debug("in do_operation_1 " + str(bian_request))
        self.process_request(bian_request)
        payload = {
            "serviceDomainActivationActionTaskReference": self.get_activation_id(),
            "serviceDomainActivationActionTaskRecord": self.get_activation_rec(),
            "serviceDomainServicingSessionReference": self.get_session_id(),
            "serviceDomainServicingSessionRecord": self.get_session_rec(),
            "serviceDomainServiceConfigurationRecord": {
                "serviceDomainServiceConfigurationSettingReference": self.get_configuration_setting_id(),
                "serviceDomainServiceConfigurationSettingDescription": self.get_configuration_desc(),
                "serviceDomainServiceConfigurationSetup": {
                    "serviceDomainServiceConfigurationParameter": self.get_configuration_param(),
                },
                "serviceDomainServiceSubscription": {
                    "serviceDomainServiceSubscriberReference": self.get_subscriber_id(),
                    "serviceDomainServiceSubscriberAccessProfile": self.get_subscriber_access()
                },
                "serviceDomainServiceAgreement": {
                    "serviceDomainServiceAgreementReference": self.get_agreement_id(),
                    "serviceDomainServiceUserReference": self.get_user_id(),
                    "serviceDomainServiceAgreementTermsandConditions": self.get_agree_terms(),
                },
                "serviceDomainServiceStatus": self.get_sdservice_status()
            },
            "serviceDomainServicingSessionStatus": self.get_session_status()
        }
        dict = {'1': payload}
        return dict


class ConfigurationAbsBianMixin(AbsBianSrvMixin):
    __metaclass__ = ABCMeta

    bian_action = ActionTerms.CONFIGURE

    def process_request(self, bian_request):
        data = bian_request.request.get_json()
        self.servicing_session_id = data["serviceDomainServicingSessionReference"]
        self.service_id = data["serviceDomainServiceReference"]
        self.configuration_setting_id = data["serviceDomainServiceConfigurationRecord"][
            "serviceDomainServiceConfigurationSettingReference"]
        self.configuration_setting_param = data["serviceDomainServiceConfigurationRecord"][
            "serviceDomainServiceConfigurationSetup"]["serviceDomainServiceConfigurationParameter"]
        self.subscriber_id = data["serviceDomainServiceConfigurationRecord"][
            "serviceDomainServiceSubscription"]["serviceDomainServiceSubscriberReference"]
        self.agreement_id = data["serviceDomainServiceConfigurationRecord"][
            "serviceDomainServiceAgreement"]["serviceDomainServiceAgreementReference"]
        self.user_id = data["serviceDomainServiceConfigurationRecord"][
            "serviceDomainServiceAgreement"]["serviceDomainServiceUserReference"]
        self.persist_config_setting(bian_request)

    def persist_config_setting(self,bian_request):
        #@todo implement persistance
        """Method documentation"""
        #dbaccess = self.get_dbaccess(bian_request)
        #dbaccess.save_servicing_session(servicing_session)
        params = {}
        params[self.get_configuration_setting_id()] = self.get_configuration_param()
        set_app_param_config(settings.SSM_TYPE,params)
        #set_app_param_config(settings.SSM_TYPE, self.get_configuration_setting_id(), self.get_configuration_param())
        return

    def get_activation_id(self):
        return ""

    def get_session_id(self):
        return ""

    def get_configuration_setting_id(self):
        return self.configuration_setting_id

    def get_configuration_rec(self):
        return ""

    def get_configuration_desc(self):
        return ""

    def get_configuration_param(self):
        return self.configuration_setting_param

    def get_subscriber_id(self):
        return self.subscriber_id

    def get_agreement_id(self):
        return self.agreement_id

    def get_user_id(self):
        return self.user_id

    def get_subscriber_access(self):
        return ""

    def get_sdservice_status(self):
        return ""

    def get_agreement_terms(self):
        return ""

    def get_session_status(self):
        return ""

    def do_operation_1(self,bian_request):
        logger.debug("in process_put ")
        self.process_request(bian_request)
        payload = {
            "serviceDomainConfigurationActionTaskReference": self.get_configuration_setting_id(),
            "serviceDomainConfigurationActionTaskRecord": self.get_configuration_rec(),
            "serviceDomainServiceConfigurationRecord": {
                "serviceDomainServiceConfigurationSettingDescription": self.get_configuration_desc(),
                "serviceDomainServiceConfigurationSetup": {
                    "serviceDomainServiceConfigurationParameter": self.get_configuration_param()
                },
                "serviceDomainServiceSubscription": {
                    "serviceDomainServiceSubscriberReference": self.get_subscriber_id(),
                    "serviceDomainServiceSubscriberAccessProfile": self.get_subscriber_access()
                },
                "serviceDomainServiceAgreement": {
                    "serviceDomainServiceAgreementReference": self.get_agreement_id(),
                    "serviceDomainServiceUserReference": self.get_user_id(),
                    "serviceDomainServiceAgreementTermsandConditions": self.get_agreement_terms()
                },
                "serviceDomainServiceStatus": self.get_sdservice_status()
            },
            "serviceDomainServicingSessionStatus": self.get_session_status()
        }
        dict = {'1': payload}
        return dict

class FeedbackAbsBianMixin(AbsBianSrvMixin):
    __metaclass__ = ABCMeta

    bian_action = ActionTerms.FEEDBACK

    feedback_id = ""
    feedback_rec = ""
    feedback_dt = ""
    feedback_status = ""
    emp_id = ""

    def process_request(self, bian_request):
        data = bian_request.request.get_json()
        self.servicing_session_id = data["serviceDomainFeedbackActionRecord"]["serviceDomainServicingSessionReference"]
        self.cr_id = data["serviceDomainFeedbackActionRecord"]["controlRecordInstanceReference"]
        self.bq_id = data["serviceDomainFeedbackActionRecord"]["behaviorQualifierInstanceReference"]
        self.persist_feedback_request(bian_request, self.servicing_session_id,self.cr_id,self.bq_id)


    def get_feedback_id(self):
        return self.feedback_id

    def get_feedback_rec(self):
        return self.feedback_rec

    def get_feedback_dt(self):
        return self.feedback_dt

    def get_feedback_status(self):
        return self.feedback_status

    def get_emp_id(self):
        return self.emp_id

    def do_operation_1(self, bian_request):
        logger.debug("in process_put ")
        self.process_request(bian_request)
        payload = {
            "serviceDomainFeedbackActionTaskReference": self.get_feedback_id(),
            "serviceDomainFeedbackActionTaskRecord": self.get_feedback_rec(),
            "serviceDomainFeedbackActionRecord": {
                "feedbackRecordDateTime": self.get_feedback_dt(),
                "feedbackRecordStatus": self.get_feedback_status(),
                "employeeBusinessUnitReference": self.get_emp_id()
            }
        }
        dict = {'1': payload}
        return dict

from halo_app.app.globals import GlobalService
global_service_state = None
global_service_props = None
global_service_session = None
class BianGlobalService(GlobalService):

    def load_global_data(self):
        initial_state = self.data_map["INIT_STATE"]
        prop_url = self.data_map["PROP_URL"]
        self.load_bian_global_data(initial_state, prop_url)

    def load_bian_global_data(self,initial_state,prop_url):
        global global_service_state
        global global_service_props
        global global_service_session
        global_service_state = BianServiceLifeCycleStates(initial_state)
        global_service_props = BianServiceConfiguration(prop_url)
        self.load_app_param(global_service_props)


    def load_app_param(self,global_service_props):
        """
        1. load on start
        2. if no url data its the first instance - need to write url
        3. if url data compare to halo_host - if different update url
        3. if url data and same as halo_host then not first - read other params (session_id...)
        4. if no session_id service closed - do load from 3 again next time
        5. if session_id update val in list

        """
        config = get_app_config(settings.SSM_TYPE)
        try:
            app_config = config.get_param(settings.FUNC_NAME)
            for param_name in global_service_props.get_list():
                if param_name in app_config:
                    param_val = app_config[param_name]
                    logger.info("in load_app_param " + param_name + " = " + param_val)
                    global_service_props.update_list(param_name,param_val)
        except CacheKeyException as e:
            logger.debug(e.message)
        if settings.FUNC_NAME != settings.SERVICE_DOMAIN + '_service':
            try:
                session_id = get_app_param_config(settings.SSM_TYPE, settings.SERVICE_DOMAIN + '_service',
                                                  SESSION_ID)
                print("session_id=" + str(session_id))
                if session_id:
                    global global_service_session
                    global_service_session = BianServicingSession(session_id)
            except CacheKeyException as e:
                logger.debug(e.message)
            try:
                state = get_app_param_config(settings.SSM_TYPE, settings.SERVICE_DOMAIN + '_service',
                                                      STATE)
                print("state=" + str(state))
                found = False
                global global_service_state
                for s in global_service_state.states:
                    if s.state_name == state:
                        global_service_state.set_new_state(s)
                        found = True
                if not found:
                    if state == None:
                        global_service_state.set_new_state(global_service_state.Idle)
                    else:
                        raise BianException("bad state :"+str(state))
            except CacheKeyException as e:
                global_service_state.set_new_state(global_service_state.Idle)
                logger.debug(e.message)

    @staticmethod
    def get_service_properties():
        global global_service_props
        return global_service_props

    @staticmethod
    def get_service_state():
        global global_service_state
        return global_service_state

    @staticmethod
    def get_service_session():
        global global_service_session
        return global_service_session

