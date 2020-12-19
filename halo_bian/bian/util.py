
import logging

from halo_app.app.command import HaloQuery, HaloCommand
from halo_app.app.request import HaloRequest
from halo_app.classes import AbsBaseClass

from halo_bian.bian.bian import ActionTerms
from halo_bian.bian.command import BianQuery, BianCommand
from halo_bian.bian.context import BianContext, BianCtxFactory
from halo_bian.bian.exceptions import IllegalActionTermError
from halo_bian.bian.request import BianCommandRequest, BianQueryRequest

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
    def create_bian_request(cls,bian_context:BianContext, method_id:str, vars:dict,action: ActionTerms=ActionTerms.RETRIEVE) -> HaloRequest:
        logger.debug("in bian_validate_req " + str(action) + " vars=" + str(vars))
        action_term = action
        if action_term not in ActionTerms.ops:
            raise IllegalActionTermError(action)
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
            behavior_qualifier = cls.get_behavior_qualifier_from_path(action_term,bq_reference_id)
        if "sbq_reference_id" in vars:
            sub_qualifiers = cls.get_sub_qualifiers(behavior_qualifier, vars)
        if "collection_filter" in vars:
            collection_filter = vars["collection_filter"]
        if "body" in vars:
            body = vars["body"]

        if action == ActionTerms.RETRIEVE:
            bian_query = BianQuery(bian_context, method_id, vars)
            return BianQueryRequest(bian_query, action_term, sd_reference_id=sd_reference_id,
                                      cr_reference_id=cr_reference_id, bq_reference_id=bq_reference_id,
                                      behavior_qualifier=behavior_qualifier, collection_filter=collection_filter,
                                      body=body, sub_qualifiers=sub_qualifiers)
        bian_command = BianCommand(bian_context, method_id, vars)
        return BianCommandRequest(bian_command,action_term,sd_reference_id=sd_reference_id, cr_reference_id=cr_reference_id, bq_reference_id=bq_reference_id, behavior_qualifier=behavior_qualifier,collection_filter=collection_filter,body=body,sub_qualifiers=sub_qualifiers)

