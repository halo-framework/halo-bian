from abc import abstractmethod

from halo_flask.models import AbsDbMixin


class AbsBianDbMixin(AbsDbMixin):

    @abstractmethod
    def save_servicing_session(self,servicing_session):
        pass

    @abstractmethod
    def get_servicing_session(self,servicing_session_id):
        pass

    @abstractmethod
    def save_feedback_event(self,feedback_event):
        pass

    @abstractmethod
    def get_feedback_events(self,ss_id,cr_id=None,bq_id=None):
        pass