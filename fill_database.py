import random
from datetime import datetime, timedelta
from app.models.models import Outlet, Worker, Customer, Order, Visit, Status
from app.core.database import sync_session, sync_engine, Base


Base.metadata.drop_all(sync_engine)
Base.metadata.create_all(sync_engine)


# Функция для генерации случайной даты
def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )


# Создайте случайные даты для заказов
start_date = datetime(2023, 1, 1)
ended_date = datetime(2023, 12, 31)

# Создайте соединение с базой данных
with sync_session() as session:
    # Создайте 10 дополнительных оутлетов
    outlets = []
    for i in range(1, 11):
        outlet = Outlet(name=f'Outlet {i}')
        session.add(outlet)
        outlets.append(outlet)

    # Создайте 200 заказчиков
    customers = []
    for i in range(1, 201):
        outlet = random.choice(outlets)
        customer = Customer(name=f'Customer {i}', phone_number=f'8913{random.randint(1000000, 9999999)}', outlet=outlet)
        session.add(customer)
        customers.append(customer)

    # Создайте 200 воркеров
    workers = []
    for i in range(1, 201):
        k = random.randint(1, 10)
        outlet = random.sample(outlets, k)
        
        worker = Worker(
            name=f'Worker {i}',
            phone_number=f'8913{random.randint(1000000, 9999999)}',
            outlets=outlet
        )
        session.add(worker)
        workers.append(worker)

    orders = []
    # Создайте 200 заказов
    for i in range(1, 201):
        customer = random.choice(customers)
        worker = random.choice(workers)
        created_date = random_date(start_date, ended_date)
        ended_date = created_date + timedelta(days=7)
        status = random.choice(list(Status))
        outlet = random.choice(outlets)
        order = Order(
            created_date=created_date,
            ended_date=ended_date,
            outlet=outlet,
            customer=customer,
            status=status,
            worker=worker
        )
        session.add(order)
        orders.append(order)
    # Создайте 100 посещений
    for i in range(1, 101):
        worker = random.choice(workers)
        customer = random.choice(customers)
        outlet = random.choice(outlets)
        order = random.choice(orders)
        created_date = random_date(start_date, ended_date)
        visit = Visit(
            created_date=created_date,
            worker=worker,
            customer=customer,
            outlet=outlet,
            order=order
        )
        session.add(visit)

    # Сохраните изменения в базе данных
    session.commit()
