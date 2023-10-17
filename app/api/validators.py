from datetime import datetime
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from app.models.models import Customer, Order, Outlet, Visit, Worker
from app.models.worker_outlet import worker_outlet


async def check_that_customer_exist(
    customer_id: int,
    session: AsyncSession
) -> Customer:
    stmt = select(Customer).where(Customer.id == customer_id)
    stmt = (
        stmt.
        join(Outlet, isouter=False).
        options(contains_eager(Customer.outlet))
    )

    result = await session.execute(stmt)
    customer: Customer | None = result.scalars().first()
    if not customer:
        raise HTTPException(
            status_code=404,
            detail='Такого заказчика не существует'
        )
    return customer


async def check_customer_with_number(customer: Customer, phone: str) -> None:
    if not customer.phone_number == phone:
        raise HTTPException(
            status_code=403,
            detail=(
                'Аунтентифткация по номеру телефона не прошла. '
                'Передайте корректный номер(phonr_number) '
                'или id заказчика(customer_id).'
            )
        )


async def check_customer_his_own_outlet(
    customer: Customer, request_data
) -> None:
    outlet = customer.outlet
    if request_data.outlet_id and outlet.id != request_data.outlet_id:
        raise HTTPException(
            status_code=400,
            detail="Заказчик не привязан к указанной торговой точке"
        )


async def check_that_order_not_expired(session: AsyncSession, request_data):
    order = await session.execute(
        select(Order.ended_date).where(Order.id == request_data.order_id)
    )
    order_ended_date = order.scalars().one()
    if order_ended_date > datetime.now():
        raise HTTPException(
            status_code=422,
            detail='Время окончания заказа прошло'
        )


async def check_customer_his_own_outlet_and_ended_date_not_expired(
    request_data, customer, session
) -> None:
    await check_customer_his_own_outlet(customer, request_data)
    await check_that_order_not_expired(session, request_data)


async def check_worker_in_outlet(worker_id, outlet_id, session: AsyncSession):
    stmt = (
        select(Worker)
        .join(worker_outlet)
        .join(Outlet)
        .where(Worker.id == worker_id)
        .options(contains_eager(Worker.outlets))
    )
    result = await session.execute(stmt)
    worker: Worker | None = result.scalars().first()
    if worker is None:
        return
    outlets: Sequence[Outlet] = worker.outlets
    outlets_id_list = set()
    for outlet in outlets:
        outlets_id_list.add(outlet.id)
    if outlet_id not in outlets_id_list:
        raise HTTPException(
            status_code=404,
            detail='Данный работник не относится к данной тороговой точке.'
        )


async def check_order_exists(order_id, session: AsyncSession) -> Order:
    stmt = select(Order).where(Order.id == order_id)
    order = await session.execute(stmt)
    order_obj: Order | None = order.scalars().first()
    if not order_obj:
        raise HTTPException(
            status_code=404,
            detail='Заказ который вы хотите получить не существует.'
        )
    return order_obj


async def check_visit_exists(visit_id, session: AsyncSession) -> Visit:
    stmt = select(Visit).where(Visit.id == visit_id)
    visit = await session.execute(stmt)
    visit_obj: Visit | None = visit.scalars().first()
    if not visit_obj:
        raise HTTPException(
            status_code=404,
            detail='Посещение которое вы хотите получить не существует.'
        )
    return visit_obj


async def check_worker_in_order(
    worker_id, order_id, session: AsyncSession
) -> None:
    stmt = (
        select(Worker)
        .join(Order)
        .where(Worker.id == worker_id)
        .options(contains_eager(Worker.orders))
    )

    result = await session.execute(stmt)
    worker: Worker | None = result.scalars().first()
    if worker is None:
        return
    orders: Sequence[Order] = worker.orders
    orders_id_list = set()
    for order in orders:
        orders_id_list.add(order.id)
    if order_id not in orders_id_list:
        raise HTTPException(
            status_code=404,
            detail='Данный работник не относится к данному заказу.'
        )


async def check_that_order_not_have_visit(
    session: AsyncSession, request_data
) -> None:
    order = await session.execute(
        select(Order).
        join(Order.visit).
        where(Order.id == request_data.order_id)
    )
    order_obj: Order | None = order.scalars().one_or_none()
    if order_obj:
        raise HTTPException(
            status_code=404,
            detail='У данного заказа уже есть посещение.'
        )


async def check_that_current_customer_with_current_order(
    order_id, customer, session: AsyncSession
) -> None:
    result = await session.execute(
        select(Order).filter_by(id=order_id, customer_id=customer.id)
    )
    order = result.scalar()
    if order is None:
        raise HTTPException(
            status_code=404,
            detail='Данный заказчик не привязан к заказу.'
        )


async def check_that_current_customer_with_current_visit(
    visit_id, customer, session: AsyncSession
) -> None:
    result = await session.execute(
        select(Visit).filter_by(id=visit_id, customer_id=customer.id)
    )
    order = result.scalar()
    if order is None:
        raise HTTPException(
            status_code=404,
            detail='Данный заказчик не привязан к посещению.'
        )
