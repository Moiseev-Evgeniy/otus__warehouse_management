import pytest
from sqlalchemy import delete

from domain.models import Product, Order
from infrastructure.database import SessionFactory as SyncSession
from infrastructure.orm import ProductORM, order_product_associations, OrderORM
from infrastructure.repositories import SqlAlchemyOrderRepository

session = SyncSession()
order_repo = SqlAlchemyOrderRepository(session)


@pytest.mark.parametrize(
    "products_count, name, quantity, price",
    [
        (2, "test_add_order_name_1", 99, 999.99),
        (5, "test_add_order_name_2", 88, 888.88)
    ]
)
def test_add(products_count, name, quantity, price):
    products_orm = []
    for i in range(products_count):
        product_orm = ProductORM(name=name + f"_{i}", quantity=quantity, price=price)
        session.add(product_orm)
        products_orm.append(product_orm)
    session.commit()
    products = [Product(id=p.id, name=p.name, quantity=p.quantity, price=p.price) for p in products_orm]
    order = Order(id=None, products=products)

    order_orm = order_repo.add(order)
    session.commit()

    assert order_orm.id
    assert sorted(order_orm.products, key=lambda x: x.id) == sorted(products_orm, key=lambda x: x.id)

    session.execute(delete(order_product_associations).where(order_product_associations.c.order_id == order_orm.id))
    session.execute(delete(ProductORM).where(ProductORM.id.in_([product_orm.id for product_orm in products_orm])))
    session.execute(delete(OrderORM).where(OrderORM.id == order_orm.id))
    session.commit()


@pytest.mark.parametrize(
    "products_count, name, quantity, price",
    [
        (2, "test_get_order_name_1", 77, 777.77),
        (5, "test_get_order_name_2", 66, 666.66)
    ]
)
def test_get(products_count, name, quantity, price):
    prepared_order_orm = OrderORM()
    for i in range(products_count):
        product_orm = ProductORM(name=name + f"_{i}", quantity=quantity, price=price)
        session.add(product_orm)
        prepared_order_orm.products.append(product_orm)
    session.add(prepared_order_orm)
    session.commit()

    order_orm = order_repo.get(prepared_order_orm.id)

    assert order_orm.id == prepared_order_orm.id
    assert sorted(order_orm.products, key=lambda x: x.id) == sorted(prepared_order_orm.products, key=lambda x: x.id)

    session.execute(delete(order_product_associations).where(order_product_associations.c.order_id == order_orm.id))
    session.execute(
        delete(ProductORM).where(ProductORM.id.in_([product_orm.id for product_orm in prepared_order_orm.products]))
    )
    session.execute(delete(OrderORM).where(OrderORM.id == order_orm.id))
    session.commit()


@pytest.mark.parametrize(
    "orders_count, products_count, name, quantity, price",
    [
        (3, 2, "test_list_order_name_1", 55, 555.55),
        (7, 5, "test_list_order_name_2", 44, 444.44)
    ]
)
def test_list(orders_count, products_count, name, quantity, price):
    prepared_orders_orm = []
    for j in range(orders_count):
        prepared_order_orm = OrderORM()
        for i in range(products_count):
            product_orm = ProductORM(name=name + f"_{j}_{i}", quantity=quantity, price=price)
            session.add(product_orm)
            prepared_order_orm.products.append(product_orm)
        session.add(prepared_order_orm)
        prepared_orders_orm.append(prepared_order_orm)
    session.commit()
    orders_orm = order_repo.list()

    assert len(prepared_orders_orm) <= len(orders_orm)
    assert {o.id for o in prepared_orders_orm} <= {o.id for o in orders_orm}
    assert {products_count} == {len(o.products) for o in orders_orm if o.id in {o.id for o in prepared_orders_orm}}
    order_products_dict = {o.id: o.products for o in orders_orm if o.id in {o.id for o in prepared_orders_orm}}
    for o in prepared_orders_orm:
        assert {p.id for p in o.products} == {p.id for p in order_products_dict.get(o.id)}

    p_ids = []
    for o in prepared_orders_orm:
        for p in o.products:
            p_ids.append(p.id)
    session.execute(
        delete(order_product_associations)
        .where(order_product_associations.c.order_id.in_([o.id for o in prepared_orders_orm]))
    )
    session.execute(delete(ProductORM).where(ProductORM.id.in_(p_ids)))
    session.execute(delete(OrderORM).where(OrderORM.id.in_([o.id for o in prepared_orders_orm])))
    session.commit()
