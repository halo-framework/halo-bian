from halo_app.app.boundary import BoundaryService
from halo_app.app.event import AbsHaloEvent
from halo_app.classes import AbsBaseClass
from halo_app.domain.repository import AbsRepository
from halo_app.app.uow import AbsUnitOfWork
from halo_app.entrypoints import client_util
from halo_app.entrypoints.client_type import ClientType
from halo_app.entrypoints.event_consumer import AbsConsumer
from halo_app.infra.event_publisher import AbsPublisher


class FakeRepository(AbsRepository):

    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)

    def _get_by_batchref(self, batchref):
        return next((
            p for p in self._products for b in p.batches
            if b.reference == batchref
        ), None)


class FakeUnitOfWork(AbsUnitOfWork):

    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


class FakePublisher(AbsPublisher):
    def __init__(self):
        super(FakePublisher, self).__init__()
        class Publisher():
            def publish(self,channel, json):
                pass
        self.publisher = Publisher()


class FakeConsumer(AbsConsumer):
    def __init__(self):
        super(FakeConsumer, self).__init__()


class FakeBoundary(BoundaryService):
    def fake_process(self,event):
        super(FakeBoundary,self)._process_event(event)


