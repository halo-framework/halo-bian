#!/usr/bin/env python

from halo_flask.exceptions import HaloException
from abc import ABCMeta

class BianException(HaloException):
    pass


class IllegalServiceOperationException(BianException):
    pass


class ServiceOperationFailException(BianException):
    pass


class IllegalBQException(BianException):
    pass


class BianMethodNotImplementedException(BianException):
    pass

class ServiceDomainNameException(BianException):
    pass

class FunctionalPatternNameException(BianException):
    pass