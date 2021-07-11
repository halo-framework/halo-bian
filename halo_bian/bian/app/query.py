import uuid

from halo_app.domain.event import  AbsHaloEvent
from halo_app.app.query import HaloQuery

from halo_bian.bian.app.context import BianContext
from halo_bian.bian.bian import ActionTerms


class BianQuery(HaloQuery):
    action_term = None

    def __init__(self, name:str,vars:dict,action_term:ActionTerms):
        super(BianQuery,self).__init__(name,vars)
        self.action_term = action_term


