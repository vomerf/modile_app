from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

date_example = datetime.now()


class VisitCreate(BaseModel):
    outlet_id: int = Field(None, gt=0)
    customer_id: int = Field(..., gt=0)
    worker_id: int = Field(None, gt=0)
    order_id: int = Field(None, gt=0)
    phone_number: str

    class Config:
        json_schema_extra = {
           'example': {
               'outlet_id': 1,
               'customer_id': 1,
               'worker_id': 1,
               'order_id': 1,
               'phone_number': '89138927125'
           }
        }


class VisitUpdate(BaseModel):
    outlet_id: Optional[int] = Field(None, gt=0)
    customer_id: int = Field(..., gt=0)
    worker_id: Optional[int] = Field(None, gt=0)
    order_id: Optional[int] = Field(None, gt=0)
    created_date: Optional[datetime] = Field(None)
    phone_number: str

    class Config:
        json_schema_extra = {
           'example': {
                'outlet_id': 1,
                'customer_id': 1,
                'worker_id': 1,
                'order_id': 1,
                'phone_number': '89138927125',
                'created_date': date_example
           }
        }


class VisitDB(BaseModel):
    id: int
    created_date: datetime

    class Config:
        from_attributes = True
