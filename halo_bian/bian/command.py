import uuid

from halo_app.app.command import HaloQuery, HaloCommand

from halo_bian.bian.context import BianContext


class BianCommand(HaloCommand):

    def __init__(self, context:BianContext,name:str,vars:dict,id:str=None):
        if not id:
            self.id = uuid.uuid4().__str__()
        super(HaloCommand,self).__init__(id)
        self.context = context
        self.name = name
        self.vars = vars


class BianQuery(HaloQuery):

    def __init__(self, context:BianContext,name:str,vars:dict,id:str=None):
        if not id:
            self.id = uuid.uuid4().__str__()
        super(BianQuery,self).__init__(id)
        self.context = context
        self.name = name
        self.vars = vars

