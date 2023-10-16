from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from app.models.models import Customer, Order, Outlet, Visit, Worker
from app.models.worker_outlet import worker_outlet


async def check_that_customer_exist(
    customer_id: int,
    session: AsyncSession
):

    stmt = select(Customer).where(Customer.id == customer_id)
    stmt = (
        stmt.
        join(Outlet, isouter=False).
        options(contains_eager(Customer.outlet))
    )

    result = await session.execute(stmt)
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(
            status_code=404,
            detail='Такого заказчика не существует'
        )
    return customer


async def check_customer_with_number(customer: Customer, phone: str):
    if not customer.phone_number == phone:
        raise HTTPException(
            status_code=403,
            detail=(
                'Аунтентифткация по номеру телефона не прошла. '
                'Передайте корректный номер(phonr_number) '
                'или id заказчика(customer_id).'
            )
        )


async def check_customer_his_own_outlet(customer, request_data):
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
):
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
    worker = result.scalars().first()

    outlets = worker.outlets
    outlets_id_list = set()
    for outlet in outlets:
        outlets_id_list.add(outlet.id)
    if outlet_id not in outlets_id_list:
        raise HTTPException(
            status_code=404,
            detail='Данный работник не относится к данной тороговой точке.'
        )


async def check_order_exists(order_id, session: AsyncSession):
    stmt = select(Order).where(Order.id == order_id)
    order = await session.execute(stmt)
    order = order.scalars().first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail='Заказ который вы хотите получить не существует.'
        )
    return order


async def check_visit_exists(visit_id, session: AsyncSession):
    stmt = select(Visit).where(Visit.id == visit_id)
    visit = await session.execute(stmt)
    order = visit.scalars().first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail='Посещение которое вы хотите получить не существует.'
        )
    return order


async def check_worker_in_order(worker_id, order_id, session: AsyncSession):
    stmt = (
        select(Worker)
        .join(Order)
        .where(Worker.id == worker_id)
        .options(contains_eager(Worker.orders))
    )

    result = await session.execute(stmt)
    worker = result.scalars().first()
    orders = worker.orders
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
):
    order = await session.execute(
        select(Order).
        join(Order.visit).
        where(Order.id == request_data.order_id)
    )
    order = order.scalars().one_or_none()
    if order:
        raise HTTPException(
            status_code=404,
            detail='У данного заказа уже есть посещение.'
        )


async def check_that_current_customer_with_current_order(
    order_id, customer, session: AsyncSession
):
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
):
    result = await session.execute(
        select(Visit).filter_by(id=visit_id, customer_id=customer.id)
    )
    order = result.scalar()
    if order is None:
        raise HTTPException(
            status_code=404,
            detail='Данный заказчик не привязан к посещению.'
        )
