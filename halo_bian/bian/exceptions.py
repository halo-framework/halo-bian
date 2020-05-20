#!/usr/bin/env python

from halo_flask.exceptions import HaloException, HaloError,BadRequestError
from abc import ABCMeta

class BianException(HaloException):
    pass

class BianError(HaloError):
    pass

class BadBianRequestError(BadRequestError):
    pass

class IllegalActionTermError(BianError):
    pass

#class MissingBianContextException(BianException):
#    pass

class ActionTermFailException(BianException):
    pass

class IllegalBQError(BianError):
    pass

class IllegalBQIdError(BianError):
    pass

class SystemBQIdError(BianError):
    pass

class ServiceDomainNameException(BianException):
    pass

class AssetTypeNameException(BianException):
    pass

class FunctionalPatternNameException(BianException):
    pass

class GenericArtifactNameException(BianException):
    pass

class ServiceStateException(BianException):
    pass

class ServiceNotOpenException(BianException):
    pass

class LifeCycleInitStateException(BianException):
    pass

class LifeCycleNewStateException(BianException):
    pass

class BehaviorQualifierNameException(BianException):
    pass

class ControlRecordNameException(BianException):
    pass

class NoServiceConfigurationMappingException(BianException):
    pass

class BianApiException(BianException):
    pass