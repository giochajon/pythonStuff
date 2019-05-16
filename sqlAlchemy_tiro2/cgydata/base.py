from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql://giovas:belial@localhost:5432/cgyinfo')
metadata = MetaData(engine)

Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
