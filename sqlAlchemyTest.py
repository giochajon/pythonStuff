# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://giovas:belial@localhost:5432/wordcount_dev')
Session = sessionmaker(bind=engine)

Base = declarative_base()
