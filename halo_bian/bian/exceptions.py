#!/usr/bin/env python

from halolib.exceptions import HaloException


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