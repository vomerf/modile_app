from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Order
from app.schemas.order import OrderCreate, OrderUpdate, OrderUpdateStatus


async def create_order(
        new_order: OrderCreate,
        session: AsyncSession
) -> Order:
    new_order_data = new_order.model_dump(exclude={'phone_number'})
    db_order = Order(**new_order_data)
    session.add(db_order)
    await session.commit()
    await session.refresh(db_order)
    return db_order


async def update_order(
        db_order: Order,
        order_in: OrderUpdate | OrderUpdateStatus,
        session: AsyncSession,
) -> Order:
    obj_data = jsonable_encoder(db_order)
    update_data = order_in.model_dump(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(db_order, field, update_data[field])
    session.add(db_order)
    await session.commit()
    await session.refresh(db_order)
    return db_order


async def delete_order(
        db_order: Order,
        session: AsyncSession,
) -> Order:
    await session.delete(db_order)
    await session.commit()
    return db_order
