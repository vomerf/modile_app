from pydantic import BaseModel


class OutletDB(BaseModel):
    id: int
    name: str

    class Config:
        json_schema_extra = {
           'example': {
                'id': 1,
                'name': 'Продуктовый магазин'
           }
        }
        from_attributes = True
