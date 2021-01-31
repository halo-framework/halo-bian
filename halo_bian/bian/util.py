
import logging

from halo_app.const import OPType
from halo_app.app.command import HaloCommand
from halo_app.app.request import AbsHaloRequest
from halo_app.classes import AbsBaseClass
from halo_app.errors import status
from halo_app.logs import log_json
from halo_app.reflect import Reflect

from halo_bian.bian.bian import ActionTerms, FunctionalPatterns, BehaviorQualifierType
from halo_bian.bian.app.command import BianCommand
from halo_bian.bian.domain.event import AbsBianEvent
from halo_bian.bian.app.context import BianContext, BianCtxFactory
from halo_bian.bian.exceptions import IllegalActionTermError, IllegalBQError, BehaviorQualifierNameException, \
    FunctionalPatternNameException, BianRequestActionException, ActionTermFailException
from halo_bian.bian.app.request import BianCommandRequest, BianEventRequest, BianQueryRequest
from halo_app.settingsx import settingsx

from halo_bian.bian.view.query import BianQuery

settings = settingsx()

logger = logging.getLogger(__name__)

class BianUtil(AbsBaseClass):

    @classmethod
    def get_bian_context(cls, api_key=None, x_correlation_id=None, x_user_agent=None, dlog=None, request_id=None):
        """
        :param request:
        :param api_key:
        :return:
        """

        env = {BianContext.items[BianContext.USER_AGENT]: x_user_agent,
               BianContext.items[BianContext.REQUEST]: request_id,
               BianContext.items[BianContext.CORRELATION]: x_correlation_id,
               BianContext.items[BianContext.DEBUG_LOG]: dlog}
        if api_key:
            env[BianContext.items[BianContext.API_KEY]] = api_key
        ctx = BianCtxFactory.get_initial_context(env)
        return ctx

    @classmethod
    def create_bian_request(cls,bian_context:BianContext, method_id:str, vars:dict,action: ActionTerms=None,op_type:OPType=OPType.command) -> AbsHaloRequest:
        logger.debug("in bian_validate_req " + str(action) + " vars=" + str(vars))
        if action:
            action_term = action
        else:
            action_term = cls.set_action(method_id)
        if action_term not in ActionTerms.ops:
            raise IllegalActionTermError(action_term)
        if action_term == ActionTerms.RETRIEVE:
            op_type = OPType.query
        if settings.COMMANDS_ONLY:
            op_type = OPType.command
        sd_reference_id = None
        cr_reference_id = None
        behavior_qualifier_type = None
        behavior_qualifier = None
        bq_reference_id = None
        sub_qualifiers = None
        collection_filter = None
        body = None
        if "sd_reference_id" in vars:
            sd_reference_id = vars["sd_reference_id"]
        if "cr_reference_id" in vars:
            cr_reference_id = vars["cr_reference_id"]
        if "behavior_qualifier" in vars:
            behavior_qualifier = cls.get_behavior_qualifier(action_term, vars["behavior_qualifier"])
        if "bq_reference_id" in vars:
            bq_reference_id = vars["bq_reference_id"]
            #behavior_qualifier = cls.get_behavior_qualifier_from_path(action_term,bq_reference_id)
        if "sbq_reference_id" in vars:
            sub_qualifiers = cls.get_sub_qualifiers(behavior_qualifier, vars)
        if "collection_filter" in vars:
            collection_filter = vars["collection_filter"]
        if "body" in vars:
            body = vars["body"]

        if op_type == OPType.command:
            bian_command = BianCommand(bian_context, method_id, vars,action_term)
            request = BianCommandRequest(bian_command,action_term,sd_reference_id=sd_reference_id, cr_reference_id=cr_reference_id, bq_reference_id=bq_reference_id, behavior_qualifier=behavior_qualifier,body=body,sub_qualifiers=sub_qualifiers)
        else:
            bian_query = BianQuery(bian_context, method_id, vars,action_term)
            request = BianQueryRequest(bian_query,action_term,sd_reference_id=sd_reference_id, cr_reference_id=cr_reference_id, bq_reference_id=bq_reference_id, behavior_qualifier=behavior_qualifier,collection_filter=collection_filter,sub_qualifiers=sub_qualifiers)
        return request

    @classmethod
    def get_behavior_qualifier(cls, op, bq_name):
        bqt_obj = cls.get_behavior_qualifier_type()
        for bq_id in bqt_obj.keys():
            bq_obj = bqt_obj.get(bq_id)
            if bq_obj.name == bq_name.strip().replace("-","_").replace(" ","_"):
                return bq_name
        raise IllegalBQError(bq_name)

    @classmethod
    def get_behavior_qualifier_type(cls):
        if settings.BEHAVIOR_QUALIFIER:
            return cls.get_bq_obj()
        else:
            raise BehaviorQualifierNameException("missing Behavior Qualifier definition")

    @classmethod
    def get_bq_obj(cls):
        if settings.FUNCTIONAL_PATTERN:
            functional_pattern = settings.FUNCTIONAL_PATTERN
        else:
            raise FunctionalPatternNameException("missing Functional Pattern definition")
        bq_class = FunctionalPatterns.patterns[functional_pattern][1]
        bq_obj = cls.init_bq(bq_class)
        return bq_obj

    @classmethod
    def init_bq(cls, bq_class_name):
        if settings.BEHAVIOR_QUALIFIER_TYPE:
            k = settings.BEHAVIOR_QUALIFIER_TYPE.rfind(".")
            module_name = settings.BEHAVIOR_QUALIFIER_TYPE[:k]
            class_name = settings.BEHAVIOR_QUALIFIER_TYPE[k+1:]
        else:
            module_name = "halo_bian.bian.bian"
            class_name = bq_class_name
        return Reflect.do_instantiate(module_name, class_name, BehaviorQualifierType,settings.BEHAVIOR_QUALIFIER,settings.SUB_QUALIFIER)

    @classmethod
    def set_action(cls,method_id:str)->ActionTerms:
        if method_id.startswith("retrieve_"):
            return ActionTerms.RETRIEVE
        if method_id.startswith("control_"):
            return ActionTerms.CONTROL
        if method_id.startswith("request_"):
            return ActionTerms.REQUEST
        if method_id.startswith("initiate_"):
            return ActionTerms.INITIATE
        if method_id.startswith("execute_"):
            return ActionTerms.EXECUTE
        if method_id.startswith("capture_"):
            return ActionTerms.CAPTURE
        if method_id.startswith("create_"):
            return ActionTerms.CREATE
        if method_id.startswith("evaluate_"):
            return ActionTerms.EVALUATE
        if method_id.startswith("exchange_"):
            return ActionTerms.EXCHANGE
        if method_id.startswith("grant_"):
            return ActionTerms.GRANT
        if method_id.startswith("provide_"):
            return ActionTerms.PROVIDE
        if method_id.startswith("register_"):
            return ActionTerms.REGISTER
        if method_id.startswith("update_"):
            return ActionTerms.UPDATE
        if method_id.startswith("notify_"):
            return ActionTerms.NOTIFY
        raise IllegalActionTermError(method_id)

    @classmethod
    def process_ok(cls, response):
        if response:
            if response.success:
                if response.request:
                    if response.request.context:
                        response.code = status.HTTP_200_OK
                        if response.request.context.get(BianContext.method) == 'GET':
                            response.code = status.HTTP_200_OK
                        if response.request.context.get(BianContext.method) == 'POST':
                            response.code = status.HTTP_201_CREATED
                        if response.request.context.get(BianContext.method) == 'PUT':
                            response.code = status.HTTP_202_ACCEPTED
                        if response.request.context.get(BianContext.method) == 'PATCH':
                            response.code = status.HTTP_202_ACCEPTED
                        if response.request.context.get(BianContext.method) == 'DELETE':
                            response.code = status.HTTP_200_OK
                        logger.info('process_service_operation : '+response.request.method_id,
                                    extra=log_json(response.request.context,  {"return": "success"}))
                        return response
            else:
                response.code = status.HTTP_500_INTERNAL_SERVER_ERROR
                if response.errors: # invalid params
                    response.code = status.HTTP_400_BAD_REQUEST
                response.payload = response.errors
                return response
        raise ActionTermFailException(response)

    @classmethod
    def get_headers(cls, response):
        headers = {}
        if response:
            if response.request:
                if settings.METHOD_HEADERS and response.request.method_id in settings.METHOD_HEADERS:
                    method_headers = settings.METHOD_HEADERS[response.request.method_id]
                    for h in response.request.context.keys():
                        val = response.request.context.get(h)
                        if h in method_headers:
                            headers[h] = val
        return headers
