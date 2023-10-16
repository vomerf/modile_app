from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_customer_his_own_outlet,
    check_customer_with_number, check_order_exists,
    check_that_customer_exist,
    check_worker_in_outlet,
    check_that_current_customer_with_current_order
    )
from app.core.database import get_async_session
from app.crud.order import create_order, delete_order, update_order
from app.models.models import Order, Status
from app.schemas.order import (
    OrderCreate, OrderDB, OrderUpdate, OrderUpdateStatus
)

# Создаём объект роутера.
router = APIRouter(
    prefix='/order',
    tags=['Order']
    )


@router.post(
    '/'
)
async def create_new_order(
    order_in: OrderCreate,
    session: AsyncSession = Depends(get_async_session)
):
    '''Для создания заказа обязательно
    нужно передать customer_id и phone_number
    по которым происходит проверка пользователя
    '''
    customer = await check_that_customer_exist(
        customer_id=order_in.customer_id, session=session
    )
    await check_customer_with_number(customer, order_in.phone_number)
    await check_customer_his_own_outlet(customer, order_in)
    if order_in.outlet_id and order_in.worker_id:
        await check_worker_in_outlet(
            order_in.worker_id,
            order_in.outlet_id,
            session
        )
    new_order = await create_order(order_in, session)

    return new_order


@router.get(
    '/',
    response_model=list[OrderDB],
    response_model_exclude_none=True
)
async def get_all_orders(
    session: AsyncSession = Depends(get_async_session),
    status: Optional[Status] = None,
    created_start: Optional[datetime] = Query(
        None, description="Шаблон времени YYYY-MM-DDTHH:MM:SS"
    ),
    created_end: Optional[datetime] = Query(
        None, description="Шаблон времени YYYY-MM-DDTHH:MM:SS"
    ),
    ended_start: Optional[datetime] = Query(
        None, description="Шаблон времени YYYY-MM-DDTHH:MM:SS"
    ),
    ended_end: Optional[datetime] = Query(
        None, description="Шаблон времени YYYY-MM-DDTHH:MM:SS"
    ),
):
    '''Для получения списка заказов не обязательно
    нужно передать customer_id и phone_number
    по которым происходит проверка пользователя.
    Реализована фильтрация статусу и по дате создания и завершения заказа.
    Формат времени должен соответствевать данному шаблону YYYY-MM-DDTHH:MM:SS.
    '''
    query = select(Order)
    if status:
        query = query.where(Order.status == status)
    if created_start and created_end:
        query = query.where(and_(
            Order.created_date >= created_start,
            Order.created_date <= created_end
            )
        )

    if ended_start and ended_end:
        query = query.where(and_(
            Order.ended_date >= ended_start,
            Order.ended_date <= ended_end
            )
        )
    db_objs = await session.execute(query)
    return db_objs.scalars().all()


@router.get(
    '/{order_id}',
    response_model=OrderDB,
    response_model_exclude_none=True,
)
async def get_order(
    order_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    '''Для получения списка заказов
    не обязательно нужно передать customer_id и phone_number
    по которым происходит проверка пользователя
    '''
    order = await check_order_exists(order_id, session)
    return order


@router.patch(
    '/{order_id}',
    response_model=OrderDB
)
async def partially_update_order(
    order_id: int,
    order_in: OrderUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    '''Для редактирования заказа обязательно
    нужно передать customer_id и phone_number
    по которым происходит проверка пользователя'''

    order = await get_order_by_id(order_id, session)
    customer = await check_that_customer_exist(
        customer_id=order_in.customer_id, session=session
    )
    await check_customer_with_number(customer, order_in.phone_number)
    await check_that_current_customer_with_current_order(
        order_id, customer, session
    )
    await check_customer_his_own_outlet(customer, order_in)
    if order_in.outlet_id and order_in.worker_id:
        await check_worker_in_outlet(
            order_in.worker_id, order_in.outlet_id, session
        )
    elif order_in.outlet_id:
        await check_worker_in_outlet(
            order.worker_id, order_in.outlet_id, session
        )
    elif order_in.worker_id:
        await check_worker_in_outlet(
            order_in.worker_id, order.outlet_id, session
        )
    new_order = await update_order(order, order_in, session)
    return new_order


@router.put(
    '/change-status/{order_id}',
    response_model=OrderDB,
    tags=['Change status']
)
async def update_order_status(
    order_id: int,
    order_status: OrderUpdateStatus,
    session: AsyncSession = Depends(get_async_session),
):
    '''Для редактирования статуса в заказе обязательно
    нужно передать customer_id и phone_number
    по которым происходит проверка пользователя'''

    order: Order = await get_order_by_id(order_id, session)
    customer = await check_that_customer_exist(
        customer_id=order_status.customer_id, session=session
    )
    await check_that_current_customer_with_current_order(
        order.id, customer, session
    )
    await check_customer_with_number(customer, order_status.phone_number)
    new_order = await update_order(order, order_status, session)
    return new_order


@router.delete(
    '/{order_id}',
    response_model=OrderDB,
    response_model_exclude_none=True

)
async def delete_order_by_id(
    order_id: int,
    customer_id: int,
    phone_number: str,
    session: AsyncSession = Depends(get_async_session)
):
    '''Для удаления заказе обязательно
    нужно передать customer_id и phone_number
    по которым происходит проверка пользователя'''

    db_order: Order = await get_order_by_id(
        order_id, session
    )
    customer = await check_that_customer_exist(
        customer_id=customer_id, session=session
    )
    await check_customer_with_number(customer, phone_number)
    await check_that_current_customer_with_current_order(
       order_id, customer, session
    )

    order = await delete_order(
        db_order, session
    )
    return order


async def get_order_by_id(
        order_id: int,
        session: AsyncSession,
) -> Optional[Order]:
    db_order = await session.get(Order, order_id)
    if db_order is None:
        raise HTTPException(
            status_code=404,
            detail='Заказ не найден.'
        )
    return db_order
