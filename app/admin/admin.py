from starlette_admin.contrib.sqla import Admin, ModelView
from app.core.database import async_engine
from app.models.models import Worker, Order, Outlet, Customer, Visit


class WorkerView(ModelView):
    model = Worker
    searchable_fields = ['name', 'phone_number']


class OrderView(ModelView):
    ...


class CustomerView(ModelView):
    ...


class OutletView(ModelView):
    model = Outlet
    searchable_fields = ['name']


class VisitView(ModelView):
    ...


admin = Admin(async_engine, title="База данных")
admin.add_view(WorkerView(Worker))
admin.add_view(OrderView(Order))
admin.add_view(OutletView(Outlet))
admin.add_view(CustomerView(Customer))
admin.add_view(VisitView(Visit))