import uuid

from halo_app.app.command import HaloQuery, HaloCommand

from halo_bian.bian.context import BianContext


class BianCommand(HaloCommand):

    def __init__(self, context:BianContext,name:str,vars:dict,id:str=None):
        super(BianCommand,self).__init__(context,name,vars,id)
        self.context = context
        self.name = name
        self.vars = vars


class BianQuery(HaloQuery):

    def __init__(self, context:BianContext,name:str,vars:dict,id:str=None):
        super(BianQuery,self).__init__(context,name,vars,id)
        self.context = context
        self.name = name
        self.vars = vars

