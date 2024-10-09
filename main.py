from domain.models import Product, Order
from domain.services import WarehouseService
from infrastructure.database import SessionFactory as SyncSession
from infrastructure.repositories import SqlAlchemyProductRepository, SqlAlchemyOrderRepository
from infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def main():

    with SqlAlchemyUnitOfWork(SyncSession()) as session:
        product_repo = SqlAlchemyProductRepository(session)
        order_repo = SqlAlchemyOrderRepository(session)
        warehouse_service = WarehouseService(product_repo, order_repo)

        try:
            p1 = warehouse_service.create_product(name="test1", quantity=1, price=100)
            p2 = warehouse_service.create_product(name="test2", quantity=2, price=200)
            p3 = warehouse_service.create_product(name="test3", quantity=3, price=300)

            session.commit()

            print(f"Created product: id {p1.id}")
            print(f"Created product: id {p2.id}")
            print(f"Created product: id {p3.id}")

            p1 = Product(id=p1.id, name=p1.name, quantity=p1.quantity, price=p1.price)
            p2 = Product(id=p2.id, name=p2.name, quantity=p2.quantity, price=p2.price)
            p3 = Product(id=p3.id, name=p3.name, quantity=p3.quantity, price=p3.price)

            new_order = warehouse_service.create_order([p1, p2, p3])
            session.commit()
            print(f"Created order: id {new_order.id}")
            new_order = Order(id=new_order.id)

        except Exception as e:
            session.rollback()
            raise e


if __name__ == "__main__":
    main()
