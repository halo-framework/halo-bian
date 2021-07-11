import logging
from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, ForeignKey,
    event,
)
from sqlalchemy.orm import mapper, relationship, clear_mappers

from halo_bian.bian.domain import model

logger = logging.getLogger(__name__)

metadata = MetaData()


items = Table(
    'items', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('data', String(255)),
)

item_dtls = Table(
    'item_dtls', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('desc', String(255)),
    Column('qty', Integer, nullable=False),
    Column('item_id', ForeignKey('items.id')),
)


items_view = Table(
    'items_view', metadata,
    Column('item_dtl_id', Integer),
    Column('data', String(255)),
    Column('desc', String(255)),
    Column('qty', Integer, nullable=False),
)


def start_mappers():
    logger.info("Starting mappers")
    dtls_mapper = mapper(model.ItemDetail, item_dtls)
    items_mapper = mapper(model.CurrentAccount, items)



@event.listens_for(model.CurrentAccount, 'load')
def receive_load(item, _):
    item.events = []
