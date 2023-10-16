from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_customer_his_own_outlet_and_ended_date_not_expired,
    check_customer_with_number,
    check_that_current_customer_with_current_visit, check_that_customer_exist,
    check_that_order_not_have_visit, check_visit_exists,
    check_worker_in_order)
from app.core.database import get_async_session
from app.crud.visit import create_visit, delete_visit, update_visit
from app.models.models import Customer, Order, Visit
from app.schemas.visit import VisitCreate, VisitDB, VisitUpdate


router = APIRouter(
    prefix='/visit',
    tags=['Visit']
)


@router.post('/')
async def create_new_visit(
    visit_in: VisitCreate,
    session: AsyncSession = Depends(get_async_session)
):
    await check_that_order_not_have_visit(session, visit_in)
    customer = await check_that_customer_exist(
        customer_id=visit_in.customer_id, session=session
    )
    await check_customer_with_number(customer, visit_in.phone_number)
    await check_customer_his_own_outlet_and_ended_date_not_expired(
        session, customer, visit_in
    )
    if visit_in.outlet_id and visit_in.worker_id:
        await check_worker_in_order(
            visit_in.worker_id,
            visit_in.outlet_id,
            session
        )
    new_visit = await create_visit(visit_in, session)

    return new_visit


@router.get(
    '/',
    response_model=list[VisitDB],
    response_model_exclude_none=True,
)
async def get_all_visits(
    session: AsyncSession = Depends(get_async_session),
    created_start: Optional[datetime] = Query(
        None, description="Шаблон времени YYYY-MM-DDTHH:MM:SS"
    ),
    created_end: Optional[datetime] = Query(
        None, description="Шаблон времени YYYY-MM-DDTHH:MM:SS"
    ),
):
    query = select(Order)
    if created_start and created_end:
        query = query.where(and_(
            Order.created_date >= created_start,
            Order.created_date <= created_end
            )
        )
    db_objs = await session.execute(query)
    return db_objs.scalars().all()


@router.get(
    '/{visit_id}',
    response_model=VisitDB,
    response_model_exclude_none=True,
)
async def get_visit(
    visit_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    visit = await check_visit_exists(visit_id, session)
    return visit


@router.patch(
    '/{visit_id}',
    response_model=VisitDB
)
async def partially_update_(
    visit_id: int,
    visit_in: VisitUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    visit: Visit = await get_visit_by_id(visit_id, session)
    customer: Customer = await check_that_customer_exist(
        customer_id=visit_in.customer_id, session=session
    )
    await check_customer_with_number(customer, visit_in.phone_number)
    await check_that_current_customer_with_current_visit(
        visit_id, customer, session
    )
    await check_customer_his_own_outlet_and_ended_date_not_expired(
        visit_in, customer, session
    )
    if visit_in.order_id and visit_in.worker_id:
        await check_worker_in_order(
            visit_in.worker_id, visit_in.order_id, session
        )
    elif visit_in.order_id:
        await check_worker_in_order(
            visit.worker_id, visit_in.order_id, session
        )
    elif visit_in.worker_id:
        await check_worker_in_order(
            visit_in.worker_id, visit.order_id, session
        )
    new_order = await update_visit(visit, visit_in, session)
    return new_order


@router.delete(
    '/{visit_id}',
    response_model=VisitDB,
    response_model_exclude_none=True

)
async def delete_visit_by_id(
    visit_id: int,
    customer_id: int,
    phone_number: str,
    session: AsyncSession = Depends(get_async_session)
):
    db_visit: Visit = await get_visit_by_id(
        visit_id, session
    )
    customer = await check_that_customer_exist(
        customer_id=customer_id, session=session
    )
    await check_customer_with_number(customer, phone_number)
    await check_that_current_customer_with_current_visit(
       visit_id, customer, session
    )

    visit = await delete_visit(
        db_visit, session
    )
    return visit


async def get_visit_by_id(
        visit_id: int,
        session: AsyncSession,
) -> Optional[Visit]:
    db_visit = await session.get(Visit, visit_id)
    if db_visit is None:
        raise HTTPException(
            status_code=404,
            detail='Посещение не найдено.'
        )
    return db_visit
