from __future__ import annotations

import enum

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.option import created_at, end_at, intpk
from app.models.worker_outlet import worker_outlet


class Status(str, enum.Enum):
    started = 'started'
    ended = 'ended'
    in_process = 'in_process'
    awaiting = 'awaiting'
    canceled = 'canceled'


class Outlet(Base):
    __tablename__ = 'outlet'

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column()
    workers: Mapped[list['Worker']] = relationship(
        secondary=worker_outlet, back_populates="outlets"
    )
    customers: Mapped[list['Customer']] = relationship(
        back_populates="outlet", cascade='all, delete-orphan'
    )
    orders: Mapped[list['Order']] = relationship(
        back_populates="outlet", cascade='all, delete-orphan'
    )
    visits: Mapped[list['Visit']] = relationship(
        back_populates='outlet', cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f"Outlet(id={self.id!r}, name={self.name!r}"


class Worker(Base):
    __tablename__ = 'worker'

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(255), unique=True)
    outlets: Mapped[list['Outlet']] = relationship(
        secondary=worker_outlet, back_populates="workers"
    )
    orders: Mapped[list['Order']] = relationship(
        back_populates='worker', cascade='all, delete-orphan'
    )
    visits: Mapped[list['Visit']] = relationship(
        back_populates='worker', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return (f'Worker(id={self.id!r},'
                f'name={self.name!r}, phone_number={self.phone_number!r})')


class Customer(Base):
    __tablename__ = 'customer'

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(255), unique=True)
    outlet_id: Mapped[int] = mapped_column(ForeignKey('outlet.id'))
    outlet: Mapped['Outlet'] = relationship(
        back_populates="customers"
    )
    orders: Mapped[list['Order']] = relationship(
        back_populates='customer', cascade='all, delete-orphan'
    )
    visits: Mapped[list['Visit']] = relationship(
        back_populates='customer', cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f"Customer(id={self.id!r}, name={self.name!r}"


class Order(Base):
    __tablename__ = 'order'

    id: Mapped[intpk]
    created_date: Mapped[created_at]
    ended_date: Mapped[end_at]
    outlet_id: Mapped[int] = mapped_column(
        ForeignKey('outlet.id'), nullable=True
    )
    outlet: Mapped['Outlet'] = relationship(
        back_populates="orders"
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey('customer.id'), nullable=True
    )
    customer: Mapped['Customer'] = relationship(
        back_populates='orders'
    )
    status: Mapped[Status]
    worker_id: Mapped[int] = mapped_column(
        ForeignKey('worker.id'), nullable=True
    )
    worker: Mapped['Worker'] = relationship(
        back_populates="orders"
    )
    visit: Mapped['Visit'] = relationship(
        back_populates='order', cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return (
            f'Order(id={self.id!r},'
            f'created_date={self.created_date!r}, end_date{self.ended_date}'
        )


class Visit(Base):
    __tablename__ = 'visit'

    id: Mapped[intpk]
    created_date: Mapped[created_at]
    worker_id: Mapped[int] = mapped_column(
        ForeignKey('worker.id'), nullable=True
    )
    worker: Mapped['Worker'] = relationship(
        back_populates='visits'
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey('customer.id'), nullable=True
    )
    customer: Mapped['Customer'] = relationship(
        back_populates='visits'
    )
    outlet_id: Mapped[int] = mapped_column(
        ForeignKey('outlet.id'), nullable=True
    )
    outlet: Mapped['Outlet'] = relationship(
        back_populates='visits'
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey('order.id'), nullable=True
    )
    order: Mapped['Order'] = relationship(
        back_populates='visit'
    )

    def __repr__(self) -> str:
        return f"Visit(id={self.id!r}, created_date={self.created_date!r}"
