#!/usr/bin/env python

from halo_flask.exceptions import HaloException
from abc import ABCMeta

class BianException(HaloException):
    pass


class IllegalActionTermException(BianException):
    pass

#class MissingBianContextException(BianException):
#    pass

class ActionTermFailException(BianException):
    pass

class IllegalBQException(BianException):
    pass

class IllegalBQIdException(BianException):
    pass

class SystemBQIdException(BianException):
    pass


class ServiceDomainNameException(BianException):
    pass

class AssetTypeNameException(BianException):
    pass

class FunctionalPatternNameException(BianException):
    pass

class GenericArtifactNameException(BianException):
    pass

class BehaviorQualifierNameException(BianException):
    pass

class ControlRecordNameException(BianException):
    pass


class BianApiException(BianException):
    pass