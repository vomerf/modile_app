from fastapi import APIRouter

from app.api.endpoints.order import router as order_router
from app.api.endpoints.outlet import router as outlet_router
from app.api.endpoints.visit import router as visit_router

main_router = APIRouter()
main_router.include_router(order_router)
main_router.include_router(visit_router) 
main_router.include_router(outlet_router) 