#!/usr/bin/env python
import logging
from abc import ABCMeta
import uuid
import os
import json
from datetime import datetime
from halo_flask.classes import AbsBaseClass,ServiceInfo
from halo_flask.request import HaloRequest
from halo_flask.response import HaloResponse
from halo_flask.flask.filter import RequestFilter
from halo_flask.settingsx import settingsx
from halo_bian.bian.exceptions import LifeCycleInitStateException,LifeCycleNewStateException,NoServiceConfigurationMappingException

settings = settingsx()

logger = logging.getLogger(__name__)

#@todo add json config file option replacing hard coded bian config
#@todo add full life cycle managment + state machine
#@todo life cycle for each type
#@todo extension,anlytics,cloud
#@todo add microservice support
#@todo create saas implementation - json config files
#@todo finish fargate deploy
#@todo control,monitor,analytics
#@todo ssm event processor,bian server cache

class BianRequest(HaloRequest):
    action_term = None
    sd_reference_id = None
    cr_reference_id = None
    bq_reference_id = None
    behavior_qualifier = None
    collection_filter = None
    query_params = None
    sub_qualifiers = None


    def __init__(self, action_term, request, sd_reference_id=None,cr_reference_id=None, bq_reference_id=None, behavior_qualifier=None,collection_filter=None,query_params=None,sub_qualifiers=None):
        super(BianRequest,self).__init__(request,self.get_bq_func_name(behavior_qualifier,sub_qualifiers))
        self.action_term = action_term
        self.sd_reference_id = sd_reference_id
        self.cr_reference_id = cr_reference_id
        self.behavior_qualifier = behavior_qualifier
        self.bq_reference_id = bq_reference_id
        self.collection_filter = collection_filter
        self.query_params = query_params
        self.sub_qualifiers = sub_qualifiers

    def get_bq_func_name(self,behavior_qualifier,sub_qualifiers):
        if behavior_qualifier:
            name = behavior_qualifier.lower()
            if sub_qualifiers:
                for item in sub_qualifiers.keys():
                    name = name + "_" + item.lower()
            return name
        return None

class BianResponse(HaloResponse):
    request = None

    def __init__(self, bian_request, payload=None, headers=None):
        self.request = bian_request
        self.payload = payload
        self.headers = headers

class BianRequestFilter(RequestFilter):
    # bian data
    service_domain = "service_domain"
    asset_type = "asset_type"
    functional_pattern = "functional_pattern"
    generic_artifact = "generic_artifact"
    behavior_qualifier_type = "behavior_qualifier_type"
    service_operation = "service_operation"
    action_term = "action_term"
    # request parameters
    sd_reference_id = "sd_reference_id"
    cr_reference_id = "cr_reference_id"
    bq_reference_id = "bq_reference_id"
    behavior_qualifier = "behavior_qualifier"

    def set(self, ref):
        self.ref = ref

    def augment_event_with_headers_and_data(self,event, halo_request,halo_response):
        event = super(BianRequestFilter, self).augment_event_with_headers_and_data(event, halo_request,halo_response)
        event.put(self.functional_pattern,self.ref.functional_pattern)
        event.put(self.action_term,self.ref.bian_action)
        event.put(self.service_domain, self.ref.service_domain)
        event.put(self.asset_type, self.ref.asset_type)
        event.put(self.generic_artifact, self.ref.generic_artifact)
        event.put(self.behavior_qualifier_type, self.ref.behavior_qualifier_type)
        event.put(self.service_operation, self.ref.service_operation)
        event.put(self.sd_reference_id, halo_request.sd_reference_id)
        event.put(self.cr_reference_id, halo_request.cr_reference_id)
        event.put(self.bq_reference_id, halo_request.bq_reference_id)
        event.put(self.behavior_qualifier, halo_request.behavior_qualifier)
        event = self.augment_event_with_data(event, halo_request, halo_response)
        return event

    def augment_event_with_data(self,event, halo_request, halo_response):
        return event

class AssetType(AbsBaseClass):
    __metaclass__ = ABCMeta
    ASSET_TYPE = None

    def get_asset_type(self):
        return self.ASSET_TYPE

class GenericArtifact(AbsBaseClass):
    __metaclass__ = ABCMeta
    GENERIC_ARTIFACT_TYPE = None
    behavior_qualifier_type = None

    def __init__(self, behavior_qualifier_type=None):
        self.behavior_qualifier_type = behavior_qualifier_type

    def get_generic_artifact_type(self):
        return self.GENERIC_ARTIFACT_TYPE

class BehaviorQualifier(AbsBaseClass):
    #behavior_qualifier = None
    sub_qualifiers = None
    qualifiers_depth = 1

    def __init__(self, name,sub_qualifiers=None):
        self.name = name
        if sub_qualifiers:
            self.sub_qualifiers = sub_qualifiers
            self.qualifiers_depth = self.get_qualifiers_depth(sub_qualifiers,self.qualifiers_depth)
            logger.debug("in BehaviorQualifier " + str(name) + " qualifiers_depth=" + str(self.qualifiers_depth))

    def get_qualifiers_depth(self,sub_qualifiers,the_depth):
        depth = the_depth + 1
        if sub_qualifiers:
            for key in sub_qualifiers:
                map = sub_qualifiers[key]
                subs = map["subs"]
                if subs:
                    d = self.get_qualifiers_depth(subs,depth)
                    if d > depth:
                        depth = d
        return depth

class BehaviorQualifierType(AbsBaseClass):
    __metaclass__ = ABCMeta
    BEHAVIOR_QUALIFIER_TYPE = None
    dict = {}

    def __init__(self, dict, sub_qualifiers=None):
        for key in dict:
            map = None
            if sub_qualifiers:
                if key in sub_qualifiers:
                    map = sub_qualifiers[key]
            self.dict[key] = BehaviorQualifier(dict[key].strip().replace("-", "_").replace(" ", "_"),map)

    def get_behavior_qualifier_type(self):
        return self.BEHAVIOR_QUALIFIER_TYPE

    def get(self, key):
        return self.dict[key]

    def put(self, key, value):
        self.dict[key] = value

    def keys(self):
        return self.dict.keys()

#Define Business Events for the Service Domains – four established BIAN categories are used to classify the business events:
#a. Origination – results in a new control record instance
#b. Invocation – acts on an active control record instance
#c. Reporting – provides information about one or more active instances
#d. Delegation – results in service calls to other Service Domains

class BianCategory(AbsBaseClass):
    ORIGINATION = "Origination"
    INVOCATION = "Invocation"
    REPORTING = "Reporting"
    DELEGATION = "Delegation"
    SETUP = "Setup"

class LifeCycleState(AbsBaseClass):
    state_name = None
    actions = []
    states = None
    life_cycle = None

    def __init__(self, state_name,life_cycle,actions=[]):
        self.state_name = state_name
        self.actions = actions
        self.life_cycle = life_cycle

    def allows(self,action_term):
        if action_term in self.actions:
            return True
        return False

    def set_next_states(self,states):
        self.states = states

    def check_next_states(self,state):
        if not self.states:
            self.states = self.life_cycle.states
        if state in self.states:
            return True
        return False

class LifeCycleStates(AbsBaseClass):
    __metaclass__ = ABCMeta

    current_state = None
    states = []
    version = ""

    def __init__(self,init_state, states):
        if init_state is None or init_state not in states:
            raise LifeCycleInitStateException(init_state)
        self.current_state = init_state
        self.states = states

    def get_current_state(self):
        return self.current_state

    def get_version(self):
        return self.version

    def set_new_state(self,state):
        if state in self.states:
            if self.current_state.check_next_states(state):
                self.current_state = state
                self.version = uuid.uuid4().__str__()[0:4]
                return
        raise LifeCycleNewStateException(state.state_name)


class DirectLifeCycleStates(LifeCycleStates):
    #Unassigned Assigned-strategy-pending Strategy-in-force Strategy-under-review Strategy-suspended Strategy-concluded

    def __init__(self, state_name):
        self.Unassigned = LifeCycleState("Unassigned", self)
        self.Assigned_strategy_pending = LifeCycleState("Assigned-strategy-pending",self)
        self.Strategy_in_force = LifeCycleState("Strategy-in-force",self)
        self.Strategy_under_review = LifeCycleState("Strategy-under-review",self)
        self.Strategy_suspended = LifeCycleState("Strategy-suspended",self)
        self.Strategy_concluded = LifeCycleState("Strategy-concluded",self)
        super(DirectLifeCycleStates,self).__init__(self.Unassigned,[self.Unassigned,self.Assigned_strategy_pending,self.Strategy_in_force,self.Strategy_under_review,self.Strategy_suspended,self.Strategy_concluded])

#@todo check control record good - behavior_qualifier_type
class ControlRecord(GenericArtifact):
    __metaclass__ = ABCMeta
    asset_type = None
    life_cycle_state = None

    def __init__1(self, asset_type, generic_artifact, behavior_qualifier_type,life_cycle_state):
        self.asset_type = asset_type
        #self.generic_artifact = generic_artifact
        self.behavior_qualifier_type = behavior_qualifier_type
        self.life_cycle_state = life_cycle_state

    def get_asset_type(self):
        return self.asset_type.get_asset_type()

    def get_generic_artifact_type(self):
        return self.generic_artifact.get_generic_artifact_type()

    def get_behavior_qualifier_type(self):
        self.behavior_qualifier_type.get_behavior_qualifier_type()

    def get_asset_type_obj(self):
        return self.asset_type

    def get_generic_artifact(self):
        return self.generic_artifact

    def get_behavior_qualifier(self):
        self.behavior_qualifier_type

    def get_life_cycle_state(self):
        self.life_cycle_state

    def validate_action(self,action_term):
        if self.life_cycle_state.allows(action_term):
            return True
        return False

# Service Operations - action terms v2
class ActionTerms(AbsBaseClass):
    # sd ops
    ACTIVATE = 'ACTIVATE'
    CONFIGURE = 'CONFIGURE'
    FEEDBACK = 'FEEDBACK'
    # instantiation
    CREATE = 'CREATE'
    INITIATE = 'INITIATE'
    REGISTER = 'REGISTER'
    EVALUATE = 'EVALUATE'
    PROVIDE = 'PROVIDE'
    #invocation
    UPDATE = 'UPDATE'
    CONTROL = 'CONTROL',
    EXCHANGE = 'EXCHANGE',
    CAPTURE = 'CAPTURE',
    EXECUTE = 'EXECUTE'
    REQUEST = 'REQUEST'
    GRANT = 'GRANT',
    #reporting
    RETRIEVE = 'RETRIEVE',
    NOTIFY = 'NOTIFY'

    # old
    # RECORD = 'RECORD'
    # AUTHORIZE = 'AUTHORIZE'
    # TERMINATE = 'TERMINATE'


    ops = [
        ACTIVATE,
        CONFIGURE,
        FEEDBACK,
        CREATE,
        INITIATE,
        REGISTER,
        EVALUATE,
        PROVIDE,
        UPDATE,
        CONTROL,
        EXCHANGE,
        CAPTURE,
        EXECUTE,
        REQUEST,
        GRANT,
        RETRIEVE,
        NOTIFY
    ]
    categories = {
        ACTIVATE: BianCategory.SETUP,
        CONFIGURE: BianCategory.SETUP,
        FEEDBACK: BianCategory.SETUP,

        CREATE: BianCategory.ORIGINATION,
        INITIATE: BianCategory.ORIGINATION,
        REGISTER: BianCategory.ORIGINATION,
        EVALUATE: BianCategory.ORIGINATION,
        PROVIDE: BianCategory.ORIGINATION,

        UPDATE: BianCategory.INVOCATION,
        CONTROL: BianCategory.INVOCATION,
        EXCHANGE: BianCategory.INVOCATION,
        CAPTURE: BianCategory.INVOCATION,
        EXECUTE: BianCategory.INVOCATION,
        REQUEST: BianCategory.INVOCATION,
        GRANT: BianCategory.INVOCATION,

        RETRIEVE: BianCategory.REPORTING,
        NOTIFY: BianCategory.REPORTING,
    }

# BehaviorQualifiers v2
class Aspect(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Aspect"

class Algorithm(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Algorithm"

class Assignment(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Assignment"

class Clause(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Clause"

class Deliverable(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Deliverable"

class Duty(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Duty"

class Event(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Event"

class Feature(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Feature"

class Function(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Function"

class Goal(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Goal"

class Property(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Property"

class Routine(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Routine"

class Signal(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Signal"

class Step(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Step"

class Task(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Task"

class Term(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Term"

class Test(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Test"

class Workstep(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Workstep"

class Advise(BehaviorQualifierType):
    BEHAVIOR_QUALIFIER_TYPE = "Advise"

# Generic Artifacts v2
class AdministrativePlan(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "AdministrativePlan"

class Allocation(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Allocation"

class Agreement(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Agreement"

class Analysis(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Analysis"

class Assessment(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Assessment"

class DevelopmentProject(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "DevelopmentProject"

class Directory(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Directory"

class FulfillmentArrangement(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "FulfillmentArrangement"

class Log(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Log"

class MaintenanceAgreement(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "MaintenanceAgreement"

class ManagementPlan(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "ManagementPlan"

class Measurement(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Measurement"

class Membership(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Membership"

class OperatingSession(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "OperatingSession"

class Procedure(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Procedure"

class Specification(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Specification"

class Strategy(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Strategy"

class Transaction(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Transaction"

class Advice(GenericArtifact):
    GENERIC_ARTIFACT_TYPE = "Advice"

# Functional Patterns v2
class FunctionalPatterns(AbsBaseClass):
    #create
    DIRECT = 'Direct'
    MANAGE = 'Manage'
    ADMINISTER = 'Administer'
    DESIGN = 'Design'
    DEVELOP = 'Develop'
    #initiate
    PROCESS = 'Process'
    OPERATE = 'Operate'
    MAINTAIN = 'Maintain'
    FULFILL = 'Fulfill'
    TRANSACT = 'Transact'
    ADVISE = 'Advise'
    MONITOR = 'Monitor'
    TRACK = 'Track'
    #register
    CATALOG = 'Catalog'
    ENROLL = 'Enroll'
    #evaluate
    AGREETERMS = 'Agree Terms'
    ASSESS = 'Assess'
    ANALYZE = 'Analyze'
    #provide
    ALLOCATE = 'Allocate'

    # Functional Pattern ==> Generic Artifact Type ==> Behavior Qualifier
    # pattern : [Generic Artifact,Behavior Qualifier Type]
    patterns = {
        DIRECT: ['Strategy', 'Goal'],  #
        MANAGE: ['ManagementPlan', 'Duty'],  #
        ADMINISTER: ['AdministrativePlan', 'Routine'],#
        DESIGN: ['Specification', 'Aspect'],  #
        DEVELOP: ['DevelopmentProject', 'Deliverable'],  #
        PROCESS: ['Procedure', 'Workstep'],  #
        OPERATE: ['OperatingSession', 'Function'],  #
        MAINTAIN: ['MaintenanceAgreement', 'Task'],  #
        FULFILL: ['FulfillmentArrangement', 'Feature'],  #
        TRANSACT: ['Transaction', 'Step'],
        ADVISE: ['Advice', 'Topic'],  #
        MONITOR: ['State', 'Measure'],  #
        TRACK: ['Log', 'Event'],  #
        CATALOG: ['DirectoryEntry', 'Property'],  #
        ENROLL: ['Membership', 'Clause'],  #
        AGREETERMS: ['Agreement', 'Term'],#
        ASSESS: ['Assessment', 'Test'],  #
        ANALYZE: ['Analysis', 'Algorithm'],  #
        ALLOCATE: ['Allocation', 'Criteria'],#
    }

    # action terms allowed for functional pattern
    # pattern : [action terms]
    operations = {
        ADMINISTER: [ActionTerms.EXCHANGE, ActionTerms.CAPTURE, ActionTerms.CONTROL,ActionTerms.GRANT,
                 ActionTerms.CREATE, ActionTerms.NOTIFY,
                 ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST],#
        AGREETERMS: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.GRANT,ActionTerms.EVALUATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST],#
        ALLOCATE: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.CAPTURE,ActionTerms.PROVIDE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE],#
        ANALYZE: [ActionTerms.EVALUATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.EXECUTE,ActionTerms.REQUEST],#
        ASSESS: [ActionTerms.EXCHANGE, ActionTerms.GRANT,ActionTerms.EVALUATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.EXECUTE,ActionTerms.REQUEST],#
        DESIGN: [ActionTerms.EXCHANGE, ActionTerms.CAPTURE, ActionTerms.CONTROL,
                 ActionTerms.CREATE, ActionTerms.NOTIFY,
                 ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST],#
        DEVELOP: [ActionTerms.EXCHANGE, ActionTerms.CAPTURE, ActionTerms.CONTROL,
                 ActionTerms.CREATE, ActionTerms.NOTIFY,
                 ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST],#
        DIRECT: [ActionTerms.EXCHANGE, ActionTerms.CAPTURE, ActionTerms.GRANT,
                 ActionTerms.CREATE, ActionTerms.NOTIFY,
                 ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.REQUEST],#
        MAINTAIN: [ActionTerms.CONTROL, ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
        MANAGE: [ActionTerms.EXCHANGE, ActionTerms.CAPTURE, ActionTerms.CONTROL,ActionTerms.GRANT,
                 ActionTerms.CREATE, ActionTerms.NOTIFY,
                 ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST],#
        CATALOG: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.REGISTER,ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
        TRACK: [ActionTerms.CAPTURE,ActionTerms.CONTROL, ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE],#
        MONITOR: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.CAPTURE,ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
        OPERATE: [ActionTerms.EXCHANGE, ActionTerms.CONTROL, ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,
                 ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
        FULFILL: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
        TRANSACT: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
        ENROLL: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.GRANT,ActionTerms.REGISTER,ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST],#
        PROCESS: [ActionTerms.EXCHANGE, ActionTerms.CONTROL, ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,
                 ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
        ADVISE: [ActionTerms.EXCHANGE,ActionTerms.CONTROL, ActionTerms.INITIATE,
                 ActionTerms.NOTIFY,ActionTerms.RETRIEVE, ActionTerms.FEEDBACK,
                 ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.UPDATE,ActionTerms.REQUEST,ActionTerms.EXECUTE],#
    }

    # Functional Pattern main Service Domain states
    # pattern : [life cycle states]
    #@todo finish life cycle mapping and check if state should be checked in pre and post validate for each operation
    states = {
        ADMINISTER: [],
        AGREETERMS: [],
        ALLOCATE: [],
        ANALYZE: [],
        ASSESS: [],
        DESIGN: [],
        DEVELOP: [],
        DIRECT: DirectLifeCycleStates,
        MAINTAIN: [],
        MANAGE: [],
        CATALOG: [],
        TRACK: [],
        MONITOR: [],
        OPERATE: [],
        FULFILL: [],
        TRANSACT: [],
        ENROLL: [],
        PROCESS: [],
        ADVISE: []
    }

#Capture service operation connections – The service operation connections for each business event
# Finance Context - Multi 10
from halo_flask.request import HaloContext
class BianContext(HaloContext):
    COMPANY = "Company"
    OPERATIONAL_ENTITY = "Operational Entity"
    BRAND = "Brand"
    CHANNEL = "Channel"
    ENVIRONMENT = "Environment"
    COUNTRY = "Country"
    TIME_ZONE = "Time Zone"
    LANGUAGE = "Language"
    BRANCH = "Branch"
    APP_CLIENT = "App Client"
    CONSUMER = "Consumer"
    BIZ_SCENARIO = "Biz Scenario"

    HaloContext.items[COMPANY] = "x-bian-company"
    HaloContext.items[OPERATIONAL_ENTITY] = "x-bian-op-entity"
    HaloContext.items[BRAND] = "x-bian-brand"
    HaloContext.items[CHANNEL] = "x-bian-channel"
    HaloContext.items[ENVIRONMENT] = "x-bian-env"
    HaloContext.items[COUNTRY] = "x-bian-country"
    HaloContext.items[TIME_ZONE] = "x-bian-tz"
    HaloContext.items[LANGUAGE] = "x-bian-language"
    HaloContext.items[BRANCH] = "x-bian-branch"
    HaloContext.items[APP_CLIENT] = "x-bian-app-client"
    HaloContext.items[CONSUMER] = "x-bian-consumer"
    HaloContext.items[BIZ_SCENARIO] = "x-bian-biz-scenario"

#bian services

class BianServiceInfo(ServiceInfo):
    # A Service Domain is a combination of a Functional Pattern and an Asset Type

    # The BIAN service domain name
    service_domain = None
    # The BIAN asset type managed by the service
    asset_type = "undefined"
    # The BIAN functional pattern of the service
    functional_pattern = None
    # The BIAN generic artifiact type of the service domain control record
    generic_artifact = "undefined"
    # The BIAN behavior qualifier type for the service
    behavior_qualifier_type = "undefined"
    # The control record name used by the service to track state
    control_record = "undefined"

    def __init__(self, service_domain, asset_type, functional_pattern, generic_artifact, behavior_qualifier_type):
        super(BianServiceInfo, self).__init__(settings.FUNC_NAME)
        self.service_domain = service_domain
        self.asset_type = asset_type
        self.functional_pattern = functional_pattern
        self.generic_artifact = generic_artifact
        self.control_record = asset_type + generic_artifact
        self.behavior_qualifier_type = behavior_qualifier_type

    def __init__1(self, service_domain, functional_pattern, control_record_obj):
        self.service_domain = service_domain
        self.functional_pattern = functional_pattern
        if control_record_obj:
            self.asset_type = control_record_obj.get_asset_type()
            self.generic_artifact = control_record_obj.get_generic_artifact()
            self.control_record = self.asset_type + self.generic_artifact
            self.behavior_qualifier_type = control_record_obj.get_behavior_qualifier_type()

    def get_service_domain(self):
        return self.service_domain

    def get_asset_type(self):
        return self.asset_type

    def get_functional_pattern(self):
        return self.functional_pattern

    def get_generic_artifact(self):
        return self.generic_artifact

    def get_behavior_qualifier_type(self):
        return self.behavior_qualifier_type

    def get_control_record(self):
        return self.control_record

class TheBianServiceInfo(BianServiceInfo):

    def __init__(self):
        super(TheBianServiceInfo, self).__init__(settings.SERVICE_DOMAIN, settings.ASSET_TYPE, settings.FUNCTIONAL_PATTERN, settings.GENERIC_ARTIFACT, settings.BEHAVIOR_QUALIFIER_TYPE)

class BianServiceLifeCycleStates(LifeCycleStates):
    # active, suspended, idle

    def __init__(self, init_state_name):
        self.Idle = LifeCycleState("Idle", self,[ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.FEEDBACK])
        self.Active = LifeCycleState("Active",self,ActionTerms.ops)
        self.Suspended = LifeCycleState("Suspended",self,[ActionTerms.ACTIVATE,ActionTerms.CONFIGURE,ActionTerms.FEEDBACK])
        self.Terminated = LifeCycleState("Terminated",self,[])
        array = [self.Idle,self.Active,self.Suspended,self.Terminated]
        init_state = None
        for i in array:
            if i.state_name == init_state_name:
                init_state = i
        super(BianServiceLifeCycleStates,self).__init__(init_state,array)

class BianServiceConfigurationSetting(AbsBaseClass):
    configuration_setting_id = None
    configuration_setting_name = None
    configuration_setting_type = None
    configuration_setting_value = None

class BianServiceConfiguration(AbsBaseClass):
    configuration_settings = {}

    def __init__(self, config_url):
        if config_url:
            self.load_keys_for_prop(config_url)
        else:
            raise NoServiceConfigurationMappingException(config_url)

    def load_keys_for_prop(self,config_url):
        file_dir = os.path.dirname(__file__)
        file_path = os.path.join(config_url)
        with open(file_path, 'r') as fi:
            map = json.load(fi)
            for key in map:
                self.configuration_settings[key] = map[key]
            logger.info("loaded service configuration mapping!")

    def set_configuration_setting(self, configuration_setting_id,param_type,param_value):
        name = self.configuration_settings[configuration_setting_id]
        value = self.get_val_by_type(param_type,param_value)
        settings.__setattr__(name,value)
        logger.debug("set_configuration_setting "+name+" "+settings.__getattribute__(name))

    def get_configuration_setting(self,configuration_setting_id):
        if configuration_setting_id in self.configuration_settings:
            return self.configuration_settings[configuration_setting_id]
        return None

    def get_list(self):
        return self.configuration_settings.keys()

    def update_list(self,param_name,param_val):
        self.configuration_settings[param_name] = param_val

class BianServicingSession(AbsBaseClass):
    start = None
    end = None
    session_id = None
    bian_service = None
    center_id = None
    service_id = None
    service_configuration = None
    service_state = None

    def __init__(self, session_id,center_id=None,service_id=None,service_configuration=None,service_state=None):
        self.start = datetime.now()
        if session_id:
            self.session_id = session_id
        else:
            self.session_id = uuid.uuid4().__str__()[0:8]
        self.center_id = center_id
        self.service_id = service_id
        self.service_configuration = service_configuration
        self.service_state = service_state

    def get_session_id(self):
        return self.session_id
