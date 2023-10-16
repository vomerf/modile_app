from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models.models import Customer, Outlet, Worker
from app.models.worker_outlet import worker_outlet
from app.schemas.outlet import OutletDB

router = APIRouter(
    prefix='/outlet',
    tags=['Outlet'],
)


@router.get(
    '/',
    response_model=list[OutletDB])
async def get_outlets(
    phone_number: str,
    session: AsyncSession = Depends(get_async_session)
):
    stmt = (
            select(Outlet).
            join(Outlet.customers).
            join(worker_outlet).
            join(Worker).where(
                        Worker.phone_number == phone_number or
                        Customer.phone_number == phone_number
                    )
            )

    result = await session.execute(stmt)
    outlets = result.scalars().unique().all()
    return outlets
