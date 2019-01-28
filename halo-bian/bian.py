#!/usr/bin/env python

from halolib.response import HaloResponse
from halolib.settingsx import settingsx

from exceptions import *

# flask

settings = settingsx()

logger = logging.getLogger(__name__)

from abc import ABCMeta



class BianRequest():
    service_operation = None
    behavior_qualifier = None
    reference_id = None
    request = None

    def __init__(self, service_operation, behavior_qualifier, reference_id, request):
        self.service_operation = service_operation
        self.behavior_qualifier = behavior_qualifier
        self.reference_id = reference_id
        self.request = request


class BianResponse(HaloResponse):
    bian_request = None

    def __init__(self, bian_request, payload=None, headers=None):
        self.bian_request = bian_request
        self.payload = payload
        self.headers = headers


class ServiceProperties:
    status = "online"
    props = []

    def get_status(self):
        return self.status

    def get_props(self):
        return self.props


class AssetType:
    __metaclass__ = ABCMeta
    ASSET_TYPE = None

    def get_asset_type(self):
        return self.ASSET_TYPE


class GenericArtifact:
    __metaclass__ = ABCMeta
    GENERIC_ARTIFACT_TYPE = None

    def get_generic_artifact_type(self):
        return self.GENERIC_ARTIFACT_TYPE


class BehaviorQualifier:
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

class ControlRecord(AssetType, GenericArtifact, BehaviorQualifier):
    asset_type = None
    generic_artifact = None
    behavior_qualifier = None

    def __init__(self, asset_type, generic_artifact, behavior_qualifier):
        self.asset_type = asset_type
        self.generic_artifact = generic_artifact
        self.behavior_qualifier = behavior_qualifier

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


class BianServiceInfo:
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

    def __init__(self, service_domain, functional_pattern, control_record_obj):
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


# Service Operations
class ServiceOperations:
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
class FunctionalPatterns:
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
        ADMINISTER: ['Administrative Plan', 'Routine'],
        AGREETERMS: ['Agreement', 'Term'],
        ALLOCATE: ['Allocation', 'Assignment'],
        ANALYZE: ['Analysis', 'Algorithm'],
        ASSESS: ['Assessment', 'Test'],
        DESIGN: ['Specification', 'Aspect'],
        DEVELOP: ['Development Project', 'Deliverable'],
        DIRECT: ['Strategy', 'Goal'],
        MAINTAIN: ['Maintenance Agreement', 'Task'],
        MANAGE: ['Management Plan', 'Duty'],
        REGISTER: ['Directory Entry', 'Property'],
        TRACK: ['Log', 'Event'],
        MONITOR: ['Measurement', 'Signal'],
        OPERATE: ['Operating Session', 'Function'],
        FULFILL: ['Fulfillment Arrangement', 'Feature'],
        TRANSACT: ['Transaction', 'Step'],
        ENROLL: ['Membership', 'Clause'],
        PROCESS: ['Procedure', 'Workstep']
    }

    # service operations allowed for functional pattern
    # pattern : [service operations]
    operations = {
        ADMINISTER: [ServiceOperations.ACTIVATE, ServiceOperations.CONFIGURE, ServiceOperations.UPDATE,
                     ServiceOperations.RECORD, ServiceOperations.REQUEST, ServiceOperations.TERMINATE,
                     ServiceOperations.NOTIFY, ServiceOperations.RETRIEVE],
        AGREETERMS: [ServiceOperations.INITIATE, ServiceOperations.EVALUATE, ServiceOperations.UPDATE,
                     ServiceOperations.REQUEST, ServiceOperations.TERMINATE,
                     ServiceOperations.NOTIFY, ServiceOperations.RETRIEVE],
        ALLOCATE: [ServiceOperations.ACTIVATE, ServiceOperations.CONFIGURE, ServiceOperations.UPDATE,
                   ServiceOperations.RECORD, ServiceOperations.PROVIDE,
                   ServiceOperations.NOTIFY, ServiceOperations.RETRIEVE],
        ANALYZE: [ServiceOperations.ACTIVATE, ServiceOperations.CONFIGURE,
                  ServiceOperations.RECORD, ServiceOperations.REQUEST,
                  ServiceOperations.NOTIFY, ServiceOperations.RETRIEVE],
        ASSESS: [ServiceOperations.ACTIVATE, ServiceOperations.CONFIGURE, ServiceOperations.EVALUATE,
                 ServiceOperations.RECORD, ServiceOperations.REQUEST, ServiceOperations.AUTHORIZE,
                 ServiceOperations.RETRIEVE],
        DESIGN: [ServiceOperations.CREATE, ServiceOperations.UPDATE,
                 ServiceOperations.RECORD, ServiceOperations.REQUEST,
                 ServiceOperations.RETRIEVE],
        DEVELOP: [ServiceOperations.CREATE,
                  ServiceOperations.RECORD, ServiceOperations.REQUEST,
                  ServiceOperations.RETRIEVE],
        DIRECT: [ServiceOperations.ACTIVATE, ServiceOperations.CONFIGURE, ServiceOperations.RECORD,
                 ServiceOperations.AUTHORIZE, ServiceOperations.REQUEST,
                 ServiceOperations.NOTIFY, ServiceOperations.RETRIEVE],
        MAINTAIN: [ServiceOperations.ACTIVATE, ServiceOperations.CONFIGURE,
                   ServiceOperations.RECORD, ServiceOperations.REQUEST,
                   ServiceOperations.RETRIEVE],
        MANAGE: [ServiceOperations.ACTIVATE, ServiceOperations.CONFIGURE, ServiceOperations.RECORD,
                 ServiceOperations.REQUEST, ServiceOperations.TERMINATE,
                 ServiceOperations.NOTIFY, ServiceOperations.RETRIEVE],
        REGISTER: [ServiceOperations.ACTIVATE, ServiceOperations.CONFIGURE, ServiceOperations.UPDATE,
                   ServiceOperations.REGISTER,
                   ServiceOperations.RECORD, ServiceOperations.REQUEST,
                   ServiceOperations.NOTIFY, ServiceOperations.RETRIEVE],
        TRACK: [ServiceOperations.ACTIVATE, ServiceOperations.CONFIGURE, ServiceOperations.UPDATE,
                ServiceOperations.RECORD, ServiceOperations.TERMINATE,
                ServiceOperations.NOTIFY, ServiceOperations.RETRIEVE],
        MONITOR: [ServiceOperations.ACTIVATE, ServiceOperations.CONFIGURE,
                  ServiceOperations.RECORD, ServiceOperations.REQUEST, ServiceOperations.TERMINATE,
                  ServiceOperations.NOTIFY, ServiceOperations.RETRIEVE],
        OPERATE: [ServiceOperations.ACTIVATE, ServiceOperations.CONFIGURE,
                  ServiceOperations.RECORD, ServiceOperations.EXECUTE, ServiceOperations.REQUEST,
                  ServiceOperations.TERMINATE,
                  ServiceOperations.NOTIFY, ServiceOperations.RETRIEVE],
        FULFILL: [ServiceOperations.INITIATE, ServiceOperations.EXECUTE, ServiceOperations.UPDATE,
                  ServiceOperations.RECORD, ServiceOperations.REQUEST, ServiceOperations.TERMINATE,
                  ServiceOperations.NOTIFY, ServiceOperations.RETRIEVE],
        TRANSACT: [ServiceOperations.INITIATE, ServiceOperations.UPDATE,
                   ServiceOperations.EXECUTE, ServiceOperations.REQUEST,
                   ServiceOperations.NOTIFY, ServiceOperations.RETRIEVE],
        ENROLL: [ServiceOperations.ACTIVATE, ServiceOperations.CONFIGURE, ServiceOperations.UPDATE,
                 ServiceOperations.REQUEST,
                 ServiceOperations.RETRIEVE],
        PROCESS: [ServiceOperations.ACTIVATE, ServiceOperations.CONFIGURE, ServiceOperations.UPDATE,
                  ServiceOperations.RECORD, ServiceOperations.REQUEST, ServiceOperations.EXECUTE,
                  ServiceOperations.NOTIFY, ServiceOperations.RETRIEVE],
    }
