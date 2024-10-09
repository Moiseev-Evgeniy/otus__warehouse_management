import pytest
from sqlalchemy import delete

from domain.models import Product
from domain.services import WarehouseService
from infrastructure.orm import ProductORM, order_product_associations, OrderORM
from infrastructure.repositories import SqlAlchemyProductRepository, SqlAlchemyOrderRepository
from infrastructure.database import SessionFactory as SyncSession

session = SyncSession()
product_repo = SqlAlchemyProductRepository(session)
order_repo = SqlAlchemyOrderRepository(session)
warehouse_service = WarehouseService(product_repo, order_repo)


@pytest.mark.parametrize(
    "name, quantity, price",
    [
        ("test_create_product_name_1", 88, 888.88),
        ("test_create_product_name_2", 99, 999.99)
    ]
)
def test_create_product(name, quantity, price):
    product_orm = warehouse_service.create_product(name=name, quantity=quantity, price=price)
    session.commit()
    product_orm_from_db = session.query(ProductORM).filter_by(id=product_orm.id).scalar()

    assert product_orm.id == product_orm_from_db.id
    assert product_orm.name == product_orm_from_db.name == name
    assert product_orm.quantity == product_orm_from_db.quantity == quantity
    assert product_orm.price == product_orm_from_db.price == price

    session.execute(delete(ProductORM).filter_by(id=product_orm.id))
    session.commit()


@pytest.mark.parametrize(
    "products_count, name, quantity, price",
    [
        (2, "test_create_order_name_1", 66, 666.66),
        (5, "test_create_order_name_2", 77, 777.77)
    ]
)
def test_create_order(products_count, name, quantity, price):
    products_orm = []
    for i in range(products_count):
        products_orm.append(warehouse_service.create_product(name=name + f"_{i}", quantity=quantity, price=price))
    session.commit()
    products = [Product(id=p.id, name=p.name, quantity=p.quantity, price=p.price) for p in products_orm]

    order_orm = warehouse_service.create_order(products)
    session.commit()

    assert order_orm.id
    assert sorted(order_orm.products, key=lambda x: x.id) == sorted(products_orm, key=lambda x: x.id)

    session.execute(delete(order_product_associations).where(order_product_associations.c.order_id == order_orm.id))
    session.execute(delete(ProductORM).where(ProductORM.id.in_([product_orm.id for product_orm in products_orm])))
    session.execute(delete(OrderORM).where(OrderORM.id == order_orm.id))
    session.commit()
