import uuid

from halo_app.app.command import AbsHaloCommand,DictHaloCommand
from halo_app.domain.event import AbsHaloEvent
from halo_bian.bian.app.context import BianContext
from halo_bian.bian.bian import ActionTerms

class AbsBianCommand(AbsHaloCommand):
    action_term = None

    def __init__(self, name:str,action_term:ActionTerms):
        super(AbsBianCommand,self).__init__(name)
        self.action_term = action_term

class DictBianCommand(AbsBianCommand):
    action_term = None

    def __init__(self, name:str,vars:dict,action_term:ActionTerms):
        super(DictBianCommand,self).__init__(name,action_term)
        self.vars = vars




