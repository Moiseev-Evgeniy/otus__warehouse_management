from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
engine = create_engine(
    "postgresql://POSTGRES:POSTGRES@localhost:5432/POSTGRES",connect_args={"options": f"-csearch_path=otus_wh"}
)
SessionFactory = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
