import uuid

from halo_app.domain.command import  HaloCommand
from halo_app.domain.event import  AbsHaloEvent
from halo_bian.bian.context import BianContext




class AbsBianEvent(AbsHaloEvent):

    def __init__(self, context:BianContext,name:str,vars:dict,id:str=None):
        super(AbsBianEvent,self).__init__(context,name,vars,id)
        self.context = context
        self.name = name
        self.vars = vars

