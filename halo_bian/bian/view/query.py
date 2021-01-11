import uuid

from halo_app.domain.command import  HaloCommand
from halo_app.domain.event import  AbsHaloEvent
from halo_app.view.query import HaloQuery

from halo_bian.bian.app.context import BianContext
from halo_bian.bian.bian import ActionTerms


class BianQuery(HaloQuery):
    action_term = None

    def __init__(self, context:BianContext,name:str,vars:dict,action_term:ActionTerms):
        super(BianQuery,self).__init__(context,name,vars)
        self.action_term = action_term


