#!/usr/bin/env python
import logging
from abc import ABCMeta

from halo_flask.classes import AbsBaseClass
from halo_flask.request import HaloRequest
from halo_flask.response import HaloResponse
from halo_flask.settingsx import settingsx

settings = settingsx()

logger = logging.getLogger(__name__)


#extension,anlytics,cloud

class BianRequest(HaloRequest):
    action_term = None
    cr_reference_id = None
    bq_reference_id = None
    behavior_qualifier = None
    collection_filter = None

    def __init__(self, action_term, request, cr_reference_id=None, bq_reference_id=None, behavior_qualifier=None,collection_filter=None):
        self.action_term = action_term
        self.request = request
        self.cr_reference_id = cr_reference_id
        self.behavior_qualifier = behavior_qualifier
        self.bq_reference_id = bq_reference_id
        self.collection_filter = collection_filter


class BianResponse(HaloResponse):
    request = None

    def __init__(self, bian_request, payload=None, headers=None):
        self.request = bian_request
        self.payload = payload
        self.headers = headers


class ServiceProperties(AbsBaseClass):
    status = "online"
    props = []

    def get_status(self):
        return self.status

    def get_props(self):
        return self.props


class AssetType(AbsBaseClass):
    __metaclass__ = ABCMeta
    ASSET_TYPE = None

    def get_asset_type(self):
        return self.ASSET_TYPE


class GenericArtifact(AbsBaseClass):
    __metaclass__ = ABCMeta
    GENERIC_ARTIFACT_TYPE = None

    def get_generic_artifact_type(self):
        return self.GENERIC_ARTIFACT_TYPE


class BehaviorQualifier(AbsBaseClass):
    __metaclass__ = ABCMeta
    BEHAVIOR_QUALIFIER_TYPE = None
    dict = {}

    def __init__(self, dict):
        self.dict = dict

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

class LifeCycleState(AbsBaseClass):
    __metaclass__ = ABCMeta
    #Unassigned Assigned-strategy-pending Strategy-in-force Strategy-under-review Strategy-suspended Strategy-concluded
    Unassigned = "Unassigned"
    Assigned_strategy_pending = "Assigned-strategy-pending"
    Strategy_in_force = "Strategy-in-force"
    Strateg_under_review = "Strategy-under-review"
    Strategy_suspended = "Strategy-suspended"
    Strategy_concluded = "Strategy-concluded"


class ControlRecord(AssetType, GenericArtifact, BehaviorQualifier):
    __metaclass__ = ABCMeta
    asset_type = None
    generic_artifact = None
    behavior_qualifier = None
    life_cycle_state = None

    def __init__1(self, asset_type, generic_artifact, behavior_qualifier,life_cycle_state):
        self.asset_type = asset_type
        self.generic_artifact = generic_artifact
        self.behavior_qualifier = behavior_qualifier
        self.life_cycle_state = life_cycle_state

    def get_asset_type(self):
        return self.asset_type.get_asset_type()

    def get_generic_artifact_type(self):
        return self.generic_artifact.get_generic_artifact_type()

    def get_behavior_qualifier_type(self):
        self.behavior_qualifier.get_behavior_qualifier_type()

    def get_asset_type_obj(self):
        return self.asset_type

    def get_generic_artifact(self):
        return self.generic_artifact

    def get_behavior_qualifier(self):
        self.behavior_qualifier

    def get_life_cycle_state(self):
        self.life_cycle_state


class BianServiceInfo(AbsBaseClass):
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


# Service Operations - action terms
class ActionTerms(AbsBaseClass):
    INITIATE = 'INITIATE'
    CREATE = 'CREATE'
    ACTIVATE = 'ACTIVATE'
    CONFIGURE = 'CONFIGURE'
    UPDATE = 'UPDATE'
    REGISTER = 'REGISTER'
    RECORD = 'RECORD'
    EXECUTE = 'EXECUTE'
    EVALUATE = 'EVALUATE'
    PROVIDE = 'PROVIDE'
    AUTHORIZE = 'AUTHORIZE'
    REQUEST = 'REQUEST'
    TERMINATE = 'TERMINATE'
    NOTIFY = 'NOTIFY'
    RETRIEVE = 'RETRIEVE'
    ops = [
        INITIATE,
        CREATE,
        ACTIVATE,
        CONFIGURE,
        UPDATE,
        REGISTER,
        RECORD,
        EXECUTE,
        EVALUATE,
        PROVIDE,
        AUTHORIZE,
        REQUEST,
        TERMINATE,
        NOTIFY,
        RETRIEVE]
    categories = {
        INITIATE: BianCategory.ORIGINATION,
        CREATE: BianCategory.ORIGINATION,
        ACTIVATE: BianCategory.ORIGINATION,
        CONFIGURE: BianCategory.ORIGINATION,

        UPDATE: BianCategory.INVOCATION,
        REGISTER: BianCategory.INVOCATION,
        RECORD: BianCategory.INVOCATION,
        EXECUTE: BianCategory.INVOCATION,
        EVALUATE: BianCategory.INVOCATION,
        PROVIDE: BianCategory.INVOCATION,
        AUTHORIZE: BianCategory.INVOCATION,
        REQUEST: BianCategory.INVOCATION,
        TERMINATE: BianCategory.INVOCATION,

        NOTIFY: BianCategory.REPORTING,
        RETRIEVE: BianCategory.REPORTING}


# BehaviorQualifiers
class Aspect(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Aspect"


class Algorithm(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Algorithm"


class Assignment(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Assignment"


class Clause(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Clause"


class Deliverable(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Deliverable"


class Duty(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Duty"


class Event(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Event"


class Feature(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Feature"


class Function(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Function"


class Goal(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Goal"


class Property(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Property"


class Routine(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Routine"


class Signal(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Signal"


class Step(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Step"


class Task(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Task"


class Term(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Term"


class Test(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Test"


class Workstep(BehaviorQualifier):
    BEHAVIOR_QUALIFIER_TYPE = "Workstep"


# Generic Artifacts
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


# Functional Patterns
class FunctionalPatterns(AbsBaseClass):
    ADMINISTER = 'Administer'
    AGREETERMS = 'Agree Terms'
    ALLOCATE = 'Allocate'
    ANALYZE = 'Analyze'
    ASSESS = 'Assess'
    DESIGN = 'Design'
    DEVELOP = 'Develop'
    DIRECT = 'Direct'
    MAINTAIN = 'Maintain'
    MANAGE = 'Manage'
    REGISTER = 'Register'
    TRACK = 'Track'
    MONITOR = 'Monitor'
    OPERATE = 'Operate'
    FULFILL = 'Fulfill'
    TRANSACT = 'Transact'
    ENROLL = 'Enroll'
    PROCESS = 'Process'

    # Functional Pattern ==> Generic Artifact Type ==> Behavior Qualifier
    # pattern : [Generic Artifact,Behavior Qualifier Type]
    patterns = {
        ADMINISTER: ['AdministrativePlan', 'Routine'],
        AGREETERMS: ['Agreement', 'Term'],
        ALLOCATE: ['Allocation', 'Assignment'],
        ANALYZE: ['Analysis', 'Algorithm'],
        ASSESS: ['Assessment', 'Test'],
        DESIGN: ['Specification', 'Aspect'],
        DEVELOP: ['DevelopmentProject', 'Deliverable'],
        DIRECT: ['Strategy', 'Goal'],
        MAINTAIN: ['MaintenanceAgreement', 'Task'],
        MANAGE: ['ManagementPlan', 'Duty'],
        REGISTER: ['Directory_Entry', 'Property'],
        TRACK: ['Log', 'Event'],
        MONITOR: ['Measurement', 'Signal'],
        OPERATE: ['OperatingSession', 'Function'],
        FULFILL: ['FulfillmentArrangement', 'Feature'],
        TRANSACT: ['Transaction', 'Step'],
        ENROLL: ['Membership', 'Clause'],
        PROCESS: ['Procedure', 'Workstep']
    }

    # action terms allowed for functional pattern
    # pattern : [action terms]
    operations = {
        ADMINISTER: [ActionTerms.ACTIVATE, ActionTerms.CONFIGURE, ActionTerms.UPDATE,
                     ActionTerms.RECORD, ActionTerms.REQUEST, ActionTerms.TERMINATE,
                     ActionTerms.NOTIFY, ActionTerms.RETRIEVE],
        AGREETERMS: [ActionTerms.INITIATE, ActionTerms.EVALUATE, ActionTerms.UPDATE,
                     ActionTerms.REQUEST, ActionTerms.TERMINATE,
                     ActionTerms.NOTIFY, ActionTerms.RETRIEVE],
        ALLOCATE: [ActionTerms.ACTIVATE, ActionTerms.CONFIGURE, ActionTerms.UPDATE,
                   ActionTerms.RECORD, ActionTerms.PROVIDE,
                   ActionTerms.NOTIFY, ActionTerms.RETRIEVE],
        ANALYZE: [ActionTerms.ACTIVATE, ActionTerms.CONFIGURE,
                  ActionTerms.RECORD, ActionTerms.REQUEST,
                  ActionTerms.NOTIFY, ActionTerms.RETRIEVE],
        ASSESS: [ActionTerms.ACTIVATE, ActionTerms.CONFIGURE, ActionTerms.EVALUATE,
                 ActionTerms.RECORD, ActionTerms.REQUEST, ActionTerms.AUTHORIZE,
                 ActionTerms.RETRIEVE],
        DESIGN: [ActionTerms.CREATE, ActionTerms.UPDATE,
                 ActionTerms.RECORD, ActionTerms.REQUEST,
                 ActionTerms.RETRIEVE],
        DEVELOP: [ActionTerms.CREATE,
                  ActionTerms.RECORD, ActionTerms.REQUEST,
                  ActionTerms.RETRIEVE],
        DIRECT: [ActionTerms.ACTIVATE, ActionTerms.CONFIGURE, ActionTerms.RECORD,
                 ActionTerms.AUTHORIZE, ActionTerms.REQUEST,
                 ActionTerms.NOTIFY, ActionTerms.RETRIEVE],
        MAINTAIN: [ActionTerms.ACTIVATE, ActionTerms.CONFIGURE,
                   ActionTerms.RECORD, ActionTerms.REQUEST,
                   ActionTerms.RETRIEVE],
        MANAGE: [ActionTerms.ACTIVATE, ActionTerms.CONFIGURE, ActionTerms.RECORD,
                 ActionTerms.REQUEST, ActionTerms.TERMINATE,
                 ActionTerms.NOTIFY, ActionTerms.RETRIEVE],
        REGISTER: [ActionTerms.ACTIVATE, ActionTerms.CONFIGURE, ActionTerms.UPDATE,
                   ActionTerms.REGISTER,
                   ActionTerms.RECORD, ActionTerms.REQUEST,
                   ActionTerms.NOTIFY, ActionTerms.RETRIEVE],
        TRACK: [ActionTerms.ACTIVATE, ActionTerms.CONFIGURE, ActionTerms.UPDATE,
                ActionTerms.RECORD, ActionTerms.TERMINATE,
                ActionTerms.NOTIFY, ActionTerms.RETRIEVE],
        MONITOR: [ActionTerms.ACTIVATE, ActionTerms.CONFIGURE,
                  ActionTerms.RECORD, ActionTerms.REQUEST, ActionTerms.TERMINATE,
                  ActionTerms.NOTIFY, ActionTerms.RETRIEVE],
        OPERATE: [ActionTerms.ACTIVATE, ActionTerms.CONFIGURE,
                  ActionTerms.RECORD, ActionTerms.EXECUTE, ActionTerms.REQUEST,
                  ActionTerms.TERMINATE,
                  ActionTerms.NOTIFY, ActionTerms.RETRIEVE],
        FULFILL: [ActionTerms.INITIATE, ActionTerms.EXECUTE, ActionTerms.UPDATE,
                  ActionTerms.RECORD, ActionTerms.REQUEST, ActionTerms.TERMINATE,
                  ActionTerms.NOTIFY, ActionTerms.RETRIEVE],
        TRANSACT: [ActionTerms.INITIATE, ActionTerms.UPDATE,
                   ActionTerms.EXECUTE, ActionTerms.REQUEST,
                   ActionTerms.NOTIFY, ActionTerms.RETRIEVE],
        ENROLL: [ActionTerms.ACTIVATE, ActionTerms.CONFIGURE, ActionTerms.UPDATE,
                 ActionTerms.REQUEST,
                 ActionTerms.RETRIEVE],
        PROCESS: [ActionTerms.ACTIVATE, ActionTerms.CONFIGURE, ActionTerms.UPDATE,
                  ActionTerms.RECORD, ActionTerms.REQUEST, ActionTerms.EXECUTE,
                  ActionTerms.NOTIFY, ActionTerms.RETRIEVE],
    }

    # Functional Pattern main Service Domain states
    # pattern : [life cycle states]
    states = {
        ADMINISTER: [],
        AGREETERMS: [],
        ALLOCATE: [],
        ANALYZE: [],
        ASSESS: [],
        DESIGN: [],
        DEVELOP: [],
        DIRECT: [LifeCycleState.Unassigned, LifeCycleState.Assigned_strategy_pending,LifeCycleState.Strateg_under_review,LifeCycleState.Strategy_concluded,LifeCycleState.Strategy_in_force,LifeCycleState.Strategy_suspended],
        MAINTAIN: [],
        MANAGE: [],
        REGISTER: [],
        TRACK: [],
        MONITOR: [],
        OPERATE: [],
        FULFILL: [],
        TRANSACT: [],
        ENROLL: [],
        PROCESS: [],
    }



#Capture service operation connections – The service operation connections for each business event