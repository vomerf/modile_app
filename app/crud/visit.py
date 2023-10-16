from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Visit
from app.schemas.visit import VisitCreate, VisitUpdate


async def create_visit(
        new_order: VisitCreate,
        session: AsyncSession
) -> Visit:
    new_order_data = new_order.model_dump(exclude={'phone_number'})
    db_order = Visit(**new_order_data)
    session.add(db_order)
    await session.commit()
    await session.refresh(db_order)
    return db_order


async def update_visit(
        db_visit: Visit,
        visit_in: VisitUpdate,
        session: AsyncSession,
) -> Visit:
    obj_data = jsonable_encoder(db_visit)
    update_data = visit_in.model_dump(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(db_visit, field, update_data[field])
    session.add(db_visit)
    await session.commit()
    await session.refresh(db_visit)
    return db_visit


async def delete_visit(
        db_visit: Visit,
        session: AsyncSession,
) -> Visit:
    await session.delete(db_visit)
    await session.commit()
    return db_visit
