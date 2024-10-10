from typing import Type

from sqlalchemy.orm import Session
from domain.models import Order, Product
from domain.repositories import ProductRepository, OrderRepository
from infrastructure.orm import ProductORM, OrderORM


class SqlAlchemyProductRepository(ProductRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, product: Product) -> ProductORM:
        product_orm = ProductORM(name=product.name, quantity=product.quantity, price=product.price)
        self.session.add(product_orm)
        return product_orm

    def get(self, product_id: int) -> ProductORM:
        return self.session.query(ProductORM).filter_by(id=product_id).scalar()

    def list(self) -> list[Type[ProductORM]]:
        return self.session.query(ProductORM).all()


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, order: Order) -> OrderORM:
        order_orm = OrderORM()
        order_orm.products = [self.session.query(ProductORM).filter_by(id=p.id).one() for p in order.products]
        self.session.add(order_orm)
        return order_orm

    def get(self, order_id: int) -> OrderORM:
        return self.session.query(OrderORM).filter_by(id=order_id).scalar()

    def list(self) -> list[Type[OrderORM]]:
        return self.session.query(OrderORM).all()
