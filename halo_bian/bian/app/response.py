#!/usr/bin/env python
import logging
from abc import ABCMeta
import uuid
import os
import json
from datetime import datetime
from halo_app.classes import AbsBaseClass,ServiceInfo
from halo_app.app.request import HaloRequest, HaloCommandRequest
from halo_app.app.response import HaloResponse
from halo_app.app.filterx import RequestFilter
from halo_app.settingsx import settingsx
from halo_bian.bian.exceptions import LifeCycleInitStateException,LifeCycleNewStateException,NoServiceConfigurationMappingException

settings = settingsx()

logger = logging.getLogger(__name__)


class BianResponse(HaloResponse):
    request = None

    def __init__(self, bian_request, payload=None, headers=None):
        self.request = bian_request
        self.payload = payload
        self.headers = headers
