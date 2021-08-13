
import logging
import json
from flask_filter.schemas import FilterSchema
from halo_app.app.cmd_assembler import CmdAssemblerFactory
from halo_app.const import OPType
from halo_app.app.command import DictHaloCommand
from halo_app.app.request import AbsHaloRequest
from halo_app.classes import AbsBaseClass
from halo_app.logs import log_json
from halo_app.reflect import Reflect
from halo_bian.bian.bian import ActionTerms, FunctionalPatterns, BehaviorQualifierType
from halo_bian.bian.app.command import DictBianCommand
from halo_bian.bian.domain.event import AbsBianEvent
from halo_bian.bian.app.context import BianContext, BianCtxFactory
from halo_bian.bian.exceptions import IllegalActionTermException, IllegalBQException, BehaviorQualifierNameException, \
    FunctionalPatternNameException, BianRequestActionException, ActionTermFailException
from halo_bian.bian.app.request import BianCommandRequest, BianEventRequest, BianQueryRequest
from halo_app.settingsx import settingsx
from halo_bian.bian.app.query import BianQuery
from halo_app.app.query_filters import Filter

settings = settingsx()

logger = logging.getLogger(__name__)

class BianUtil(AbsBaseClass):

    @classmethod
    def create_bian_request(cls,bian_context:BianContext, usecase_id:str, vars:dict,action: ActionTerms=None,op_type:OPType=OPType.COMMAND) -> AbsHaloRequest:
        logger.debug("in bian_validate_req " + str(action) + " vars=" + str(vars))
        if action:
            action_term = action
        else:
            action_term = cls.set_action(usecase_id)
        if action_term not in ActionTerms.ops:
            raise IllegalActionTermException(action_term)
        if action_term == ActionTerms.RETRIEVE:
            op_type = OPType.QUERY
        if settings.COMMANDS_ONLY:
            op_type = OPType.COMMAND
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

        if op_type == OPType.COMMAND:
            #bian_command = DictBianCommand(method_id, vars,action_term)
            cmd_assembler = CmdAssemblerFactory.get_assembler_by_method_id(usecase_id)
            bian_command = cmd_assembler.write_cmd_for_method(usecase_id, vars,action_term)
            bian_command.action_term = action_term
            request = BianCommandRequest(bian_context,bian_command,action_term,sd_reference_id=sd_reference_id, cr_reference_id=cr_reference_id, bq_reference_id=bq_reference_id, behavior_qualifier=behavior_qualifier,body=body,sub_qualifiers=sub_qualifiers)
        else:
            bian_query = BianQuery(usecase_id, vars,action_term)
            request = BianQueryRequest(bian_context,bian_query,action_term,sd_reference_id=sd_reference_id, cr_reference_id=cr_reference_id, bq_reference_id=bq_reference_id, behavior_qualifier=behavior_qualifier,collection_filter=collection_filter,sub_qualifiers=sub_qualifiers)
        return request

    @classmethod
    def get_behavior_qualifier(cls, op, bq_name):
        bqt_obj = cls.get_behavior_qualifier_type()
        for bq_id in bqt_obj.keys():
            bq_obj = bqt_obj.get(bq_id)
            if bq_obj.name == bq_name.strip().replace("-","_").replace(" ","_"):
                return bq_name
        raise IllegalBQException(bq_name)

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
        raise IllegalActionTermException(method_id)

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

    @classmethod
    def get_flask_filters(cls,collection_filter):
        filter_schema = FilterSchema()
        try:
            collection_filter_json = json.loads(collection_filter)
            if "field" in collection_filter_json:
                many = False
            else:
                many = True
            filters = filter_schema.load(collection_filter_json, many=many)
            if not many:
                filters = [filters]
            return cls.get_app_filters(filters)
        except Exception as e:  # {'_schema': ['Invalid input type.']}
            logger.error("Encountered a request error in filter: " + str(e))
            raise e

    @classmethod
    def get_app_filters(cls,collection_filters):
        arr = []
        for f in collection_filters:
            filter = Filter(f.field, f.OP, f.value)
            arr.append(filter)
        return arr

    @classmethod
    def get_bian_vars(cls,vars):
        varsx = {}
        if 'collection_filter' in vars or 'queryparams' in vars:
            try:
                if 'collection_filter' in vars:
                    item = vars['collection_filter']
                    if item:
                        collection_filter = cls.get_flask_filters(vars['collection_filter'])
                        varsx['collection_filter'] = collection_filter
                if 'queryparams' in vars:
                    item = vars['queryparams']
                    if item:
                        queryparams = cls.get_flask_filters(vars['queryparams'])
                        varsx['queryparams'] = queryparams
            except Exception as e:
                raise e

        if 'sd_reference_id' in vars:
            varsx['sd_reference_id'] = vars['sd_reference_id']
        if 'cr_reference_id' in vars:
            varsx['cr_reference_id'] = vars['cr_reference_id']
        if 'bq_reference_id' in vars:
            varsx['bq_reference_id'] = vars['bq_reference_id']
        if 'behavior_qualifier' in vars:
            varsx['behavior_qualifier'] = vars['behavior_qualifier']
        if 'body' in vars:
            varsx['body'] = vars['body']
        return varsx