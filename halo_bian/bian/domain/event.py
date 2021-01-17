import uuid

from halo_app.app.command import  HaloCommand
from halo_app.domain.event import  AbsHaloEvent
from halo_bian.bian.app.context import BianContext
from halo_bian.bian.bian import ActionTerms


class AbsBianEvent(AbsHaloEvent):
    action_term = None

    def __init__(self, context:BianContext,name:str,action_term:ActionTerms):
        super(AbsBianEvent,self).__init__(context,name)
        self.action_term = action_term


