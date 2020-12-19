from __future__ import print_function

# python
import datetime
import logging
import os
import traceback
from abc import ABCMeta,abstractmethod
import importlib
import jwt
# app
from halo_app.settingsx import settingsx

from halo_app.const import HTTPChoice

settings = settingsx()

############################################
from halo_app.app.mixinx import AbsApiMixinX
from halo_app.app.viewsx import AbsBaseLinkX
from halo_bian.bian.abs_bian_srv import AbsBianCommandHandler
from flask.views import MethodView
from flask import request,Response
import json
class TestMixinX(AbsBianCommandHandler, MethodView):
    def get(self):
        ret = self.do_process("abc",request.args,request.headers)
        print(str(ret.payload))
        if ret.code >= 300:
            return Response(ret.payload, status=ret.code, headers=ret.headers)
        return Response(json.dumps(ret.payload), status=ret.code, headers=ret.headers)

    def do_operation_11(self, halo_request):  # basic maturity - single request
        self.now = datetime.datetime.now()
        # 1. get api definition to access the BANK API  - url + vars dict
        back_json = {"msg": str(datetime.datetime.now())+' test page - timing for process: ' + str(datetime.datetime.now() - self.now) + " " + settings.VERSION}
        dict = {'1': back_json}
        # 8. return json response
        return dict

class TestLinkX(TestMixinX, AbsBaseLinkX):
    pass