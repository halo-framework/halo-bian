# pylint: disable=redefined-outer-name
from datetime import date
from sqlalchemy.orm import clear_mappers
from unittest import mock
import pytest
from halo_app import bootstrap, view
from halo_app.app.context import HaloContext
from halo_app.domain import command
from halo_app.app import uow as unit_of_work
from halo_app.domain.command import HaloCommand
from halo_app.infra import sql_uow
from tests.conftest import get_halo_context

today = date.today()


@pytest.fixture
def sqlite_boundary(sqlite_session_factory):
    boundray = bootstrap.bootstrap(
        start_orm=True,
        uow=sql_uow.SqlAlchemyUnitOfWork(sqlite_session_factory),
        publish=lambda *args: None,
    )
    yield boundray
    clear_mappers()

def test_allocations_view(sqlite_boundary):
    halo_context = HaloContext()
    sqlite_boundary.execute(HaloCommand(halo_context,'x0', {}))
    sqlite_boundary.handle(command.CreateBatch('sku2batch', 'sku2', 50, today))
    sqlite_boundary.handle(command.Allocate('order1', 'sku1', 20))
    sqlite_boundary.handle(command.Allocate('order1', 'sku2', 20))
    # add a spurious batch and order to make sure we're getting the right ones
    sqlite_boundary.handle(command.CreateBatch('sku1batch-later', 'sku1', 50, today))
    sqlite_boundary.handle(command.Allocate('otherorder', 'sku1', 30))
    sqlite_boundary.handle(command.Allocate('otherorder', 'sku2', 10))

    assert view.allocations('order1', sqlite_boundary.uow) == [
        {'sku': 'sku1', 'batchref': 'sku1batch'},
        {'sku': 'sku2', 'batchref': 'sku2batch'},
    ]


def test_deallocation(sqlite_boundary):
    sqlite_boundary.handle(command.CreateBatch('b1', 'sku1', 50, None))
    sqlite_boundary.handle(command.CreateBatch('b2', 'sku1', 50, today))
    sqlite_boundary.handle(command.Allocate('o1', 'sku1', 40))
    sqlite_boundary.handle(command.ChangeBatchQuantity('b1', 10))

    assert view.allocations('o1', sqlite_boundary.uow) == [
        {'sku': 'sku1', 'batchref': 'b2'},
    ]
