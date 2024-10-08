# todo
from sqlalchemy.orm import Session


class SqlAlchemyUnitOfWork:
    def __init__(self, session: Session):
        self.session = session
