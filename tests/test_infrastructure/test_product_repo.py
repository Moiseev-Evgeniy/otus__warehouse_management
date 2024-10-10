import pytest
from sqlalchemy import delete

from domain.models import Product
from infrastructure.database import SessionFactory as SyncSession
from infrastructure.orm import ProductORM
from infrastructure.repositories import SqlAlchemyProductRepository

session = SyncSession()
product_repo = SqlAlchemyProductRepository(session)


@pytest.mark.parametrize(
    "name, quantity, price",
    [
        ("test_add_products_name_1", 11, 111.11),
        ("test_add_products_name_2", 22, 222.22)
    ]
)
def test_add(name, quantity, price):
    product_orm = product_repo.add(Product(id=None, name=name, quantity=quantity, price=price))
    session.commit()
    product_orm_from_db = session.query(ProductORM).filter_by(id=product_orm.id).scalar()

    assert product_orm.id == product_orm_from_db.id
    assert product_orm.name == product_orm_from_db.name == name
    assert product_orm.quantity == product_orm_from_db.quantity == quantity
    assert product_orm.price == product_orm_from_db.price == price

    session.execute(delete(ProductORM).filter_by(id=product_orm.id))
    session.commit()


@pytest.mark.parametrize(
    "name, quantity, price",
    [
        ("test_get_products_name_1", 33, 333.33),
        ("test_get_products_name_2", 44, 444.44)
    ]
)
def test_get(name, quantity, price):
    prepared_product_orm = ProductORM(name=name, quantity=quantity, price=price)
    session.add(prepared_product_orm)
    session.commit()

    product_orm = product_repo.get(prepared_product_orm.id)

    assert product_orm.id == prepared_product_orm.id
    assert product_orm.name == prepared_product_orm.name == name
    assert product_orm.quantity == prepared_product_orm.quantity == quantity
    assert product_orm.price == prepared_product_orm.price == price

    session.execute(delete(ProductORM).filter_by(id=prepared_product_orm.id))
    session.commit()


@pytest.mark.parametrize(
    "products_count, name, quantity, price",
    [
        (2, "test_list_products_name_1", 55, 555.55),
        (5, "test_list_products_name_2", 66, 666.66)
    ]
)
def test_list(products_count, name, quantity, price):
    prepared_products_orm = []
    for i in range(products_count):
        product_orm = ProductORM(name=name + f"_{i}", quantity=quantity, price=price)
        session.add(product_orm)
        prepared_products_orm.append(product_orm)
    session.commit()

    products_orm = product_repo.list()

    assert len(prepared_products_orm) <= len(products_orm)
    assert {p.id for p in prepared_products_orm} <= {p.id for p in products_orm}
    assert {name + f"_{i}" for i in range(products_count)} <= {p.name for p in products_orm}

    session.execute(delete(ProductORM).where(ProductORM.id.in_([p.id for p in prepared_products_orm])))
    session.commit()
