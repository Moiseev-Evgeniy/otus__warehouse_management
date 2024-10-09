from domain.models import Product, Order
from domain.repositories import ProductRepository, OrderRepository
from infrastructure.orm import ProductORM, OrderORM


class WarehouseService:
    def __init__(self, product_repo: ProductRepository, order_repo: OrderRepository):
        self.product_repo = product_repo
        self.order_repo = order_repo

    def create_product(self, name: str, quantity: int, price: float) -> ProductORM:
        product = Product(id=None, name=name, quantity=quantity, price=price)
        product_orm = self.product_repo.add(product)
        return product_orm

    def create_order(self, products: list[Product]) -> OrderORM:
        order = Order(id=None, products=products)
        order_orm = self.order_repo.add(order)
        return order_orm
