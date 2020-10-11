from abc import abstractmethod

from halo_flask.settingsx import settingsx
from halo_flask.classes import AbsBaseClass
from .exceptions import OrchException

settings = settingsx()

class Seq(AbsBaseClass):
    def __init__(self, name,steps=[]):
        self.name = name
        self.steps = steps

    def add_step(self,step):
        self.steps.append(step)

class SeqStep(AbsBaseClass):
    def __init__(self, no, name, op,conn):
        self.no = no
        self.name = name
        self.op = op
        self.conn = conn

class AbsBianFoiEngine(AbsBaseClass):

    def create_seq(self,name):
        seq = Seq(name)
        return seq

    def get_orch_for_step(self,step):
        return step

    def get_foi_orch(self,orch_steps):
        """
        "senderServiceDomainName": "Contact Handler",
        "receiverServiceDomainName": "Contact Dialogue",
        "actionTerm": "Execute",
        "purposeOfCallText": "Initiate Servicing Session",
        "messageTransmissionKind": "RequestAndHold"
        """

        return orch_steps

    def get_orch_steps(self,scenario_name):
        for scenario in settings.BIAN_FOI_SCENARIOS:
            if 'scenarioName' in scenario and scenario_name == scenario['scenarioName']:
                primary_service_domainName = scenario['primaryServiceDomainName']
                scenario_type = scenario["type"]
                if scenario_type == "Invocation":
                    seq = self.create_seq(scenario_name)
                    if "scenarioSteps" in scenario:
                        scenario_steps = scenario["scenarioSteps"]
                        orch_steps = []
                        for step in scenario_steps:
                            if step["senderServiceDomainName"] == primary_service_domainName:
                                orch_step = self.get_orch_for_step(step)
                                orch_steps.append(orch_step)
                        return self.get_foi_orch(orch_steps)
        raise OrchException(scenario_name)