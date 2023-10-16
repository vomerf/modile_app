from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Field

from app.models.models import Status

data_example_started = datetime.now() - timedelta(weeks=30)
data_example_ended = data_example_started + timedelta(weeks=1)


class OrderCreate(BaseModel):
    customer_id: int = Field(..., gt=0)
    outlet_id: int = Field(None, gt=0)
    status: Status = Field('started')
    worker_id: int = Field(None, gt=0)
    phone_number: str

    class Config:
        json_schema_extra = {
           'example': {
               'outlet_id': 1,
               'customer_id': 1,
               'status': 'in_process',
               'worker_id': 1,
               'phone_number': '89138927125'
           }
        }


class OrderUpdate(BaseModel):
    outlet_id: int = Field(None, gt=0)
    customer_id: int = Field(..., gt=0)
    worker_id: int = Field(None, gt=0)
    created_date: datetime = Field(None)
    ended_date: datetime = Field(None)
    phone_number: str

    class Config:
        json_schema_extra = {
           'example': {
                'outlet_id': 1,
                'customer_id': 1,
                'worker_id': 1,
                'phone_number': '89138927125',
                'created_date': data_example_started,
                'ended_date': data_example_ended
           }
        }
        extra = 'forbid'


class OrderUpdateStatus(BaseModel):
    status: Status
    customer_id: int = Field(..., gt=0)
    phone_number: str

    class Config:
        json_schema_extra = {
           'example': {
                'customer_id': 1,
                'status': 'in_process',
                'phone_number': '89138927125',
           }
        }
        extra = 'forbid'


class OrderDB(BaseModel):
    id: int
    created_date: datetime
    ended_date: datetime
    status: Status

    class Config:
        from_attributes = True
