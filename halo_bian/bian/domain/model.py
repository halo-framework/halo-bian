from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set

from halo_app.app.context import HaloContext
from halo_app.domain.entity import AbsHaloAggregateRoot, AbsHaloEntity
from halo_app.domain.event import AbsHaloDomainEvent

logger = logging.getLogger(__name__)

class CurrentAccount(AbsHaloAggregateRoot):

    def __init__(self, id: str,  data: str):
        super(CurrentAccount, self).__init__(id)
        self.data = data
        self.details = []
        self.events = []

    def add(self, name: str,qty:int) -> str:
        try:
            detail = ItemDetail(None,self.id,name,qty)
            self.details.append(detail)
            self.events.append(self.add_domain_event(name,qty))
            return detail.id
        except Exception as e:
            self.events.append(self.add_error_domain_event(e))
            return None

    def add_domain_event(self, context, something: str):
        class HaloDomainEvent(AbsHaloDomainEvent):
            def __init__(self, context: HaloContext, name: str,agg_root_id:str,something:str):
                super(HaloDomainEvent, self).__init__(context, name,agg_root_id)
                self.something = something

        return HaloDomainEvent(context, "good",self.agg_root_id,something)

    def add_error_domain_event(self, context, something: str):
        class HaloDomainEvent(AbsHaloDomainEvent):
            def __init__(self, context: HaloContext, name: str,agg_root_id:str,something:str):
                super(HaloDomainEvent, self).__init__(context, name,agg_root_id)
                self.something = something

        return HaloDomainEvent(context, "bad",self.agg_root_id,something)



class ItemDetail(AbsHaloEntity):

    def __init__(self, id: str, item_id: str,name:str, qty:int):
        super(ItemDetail, self).__init__(id)
        self.item_id = item_id
        self.name = name
        self.qty = qty
        self.events = []


    def add(self, qty:int) -> int:
        try:
            self.qty += qty
            return self.qty
        except Exception as e:
            logger.error("error",e)
            return None



