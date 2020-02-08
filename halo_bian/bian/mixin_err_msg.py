#!/usr/bin/env python
import logging
import urllib
import uuid
import datetime
import json
# aws
# common
from halo_flask.const import HTTPChoice
from halo_flask.exceptions import HaloException
from halo_flask.mixin_err_msg import ErrorMessages



logger = logging.getLogger(__name__)


class ErrorMessages(ErrorMessages):
    #bian messages
    ErrorMessages.hashx["IllegalServiceOperationException"] = { "code" : 100100, "message" : "Illegal Service Operation used" }
    ErrorMessages.hashx["ServiceOperationFailException"] = {"code": 100101,"message": "Service Operation Failed"}
    ErrorMessages.hashx["IllegalBQException"] = {"code": 100102, "message": "Illegal Behavior Qualifier used"}
    ErrorMessages.hashx["IllegalBQIdException"] = {"code": 100103, "message": "Illegal Behavior Qualifier id used"}
    ErrorMessages.hashx["BianMethodNotImplementedException"] = {"code": 100104, "message": "Bian Method Not Implemented in this Service Domain"}
    ErrorMessages.hashx["ServiceDomainNameException"] = {"code": 100105, "message": "Service Domain Name missing in settings"}
    ErrorMessages.hashx["FunctionalPatternNameException"] = {"code": 100106, "message": "Functional Pattern Name missing in settings"}
    ErrorMessages.hashx["BianApiException"] = {"code": 100107, "message": "Bian Api call Failed"}





