#!/usr/bin/env python
import logging
from abc import ABCMeta
import uuid
import os
import json
from datetime import datetime
from halo_app.classes import AbsBaseClass,ServiceInfo
from halo_app.app.request import HaloRequest, HaloCommandRequest, HaloQueryRequest
from halo_app.app.response import HaloResponse
from halo_app.app.filterx import RequestFilter
from halo_app.settingsx import settingsx
from halo_bian.bian.exceptions import LifeCycleInitStateException,LifeCycleNewStateException,NoServiceConfigurationMappingException

settings = settingsx()

logger = logging.getLogger(__name__)


class BianCommandRequest(HaloCommandRequest):
    action_term = None
    sd_reference_id = None
    cr_reference_id = None
    bq_reference_id = None
    behavior_qualifier = None
    collection_filter = None
    body = None
    sub_qualifiers = None
    timeout = None


    def __init__(self,bian_command,action_term, sd_reference_id=None,cr_reference_id=None, bq_reference_id=None, behavior_qualifier=None,collection_filter=None,body=None,sub_qualifiers=None,timeout=1000):
        super(BianCommandRequest,self).__init__(bian_command)
        self.action_term = action_term
        self.sd_reference_id = sd_reference_id
        self.cr_reference_id = cr_reference_id
        self.behavior_qualifier = behavior_qualifier
        self.bq_reference_id = bq_reference_id
        self.collection_filter = collection_filter
        self.body = body
        self.sub_qualifiers = sub_qualifiers
        self.timeout = timeout

    def get_bq_func_name(self,behavior_qualifier,sub_qualifiers):
        if behavior_qualifier:
            name = behavior_qualifier.lower()
            if sub_qualifiers:
                for item in sub_qualifiers.keys():
                    name = name + "_" + item.lower()
            return name
        return None


class BianQueryRequest(HaloQueryRequest):
    action_term = None
    sd_reference_id = None
    cr_reference_id = None
    bq_reference_id = None
    behavior_qualifier = None
    collection_filter = None
    body = None
    sub_qualifiers = None
    timeout = None


    def __init__(self,bian_command,action_term, sd_reference_id=None,cr_reference_id=None, bq_reference_id=None, behavior_qualifier=None,collection_filter=None,body=None,sub_qualifiers=None,timeout=1000):
        super(BianQueryRequest,self).__init__(bian_command)
        self.action_term = action_term
        self.sd_reference_id = sd_reference_id
        self.cr_reference_id = cr_reference_id
        self.behavior_qualifier = behavior_qualifier
        self.bq_reference_id = bq_reference_id
        self.collection_filter = collection_filter
        self.body = body
        self.sub_qualifiers = sub_qualifiers
        self.timeout = timeout

    def get_bq_func_name(self,behavior_qualifier,sub_qualifiers):
        if behavior_qualifier:
            name = behavior_qualifier.lower()
            if sub_qualifiers:
                for item in sub_qualifiers.keys():
                    name = name + "_" + item.lower()
            return name
        return None
