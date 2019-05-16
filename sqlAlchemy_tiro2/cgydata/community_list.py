from sqlalchemy import Column, String, Integer, Date, Table, ForeignKey,create_engine
from sqlalchemy.orm import mapper
from base import Base, MetaData,Session,metadata

#original table def 

    # comm_code character varying(255) COLLATE pg_catalog."default" NOT NULL,
    # name character varying(255) COLLATE pg_catalog."default",
    # sector character varying(255) COLLATE pg_catalog."default",
    # class character varying(255) COLLATE pg_catalog."default",
    # res_cnt character varying(255) COLLATE pg_catalog."default",
    # dwell_cnt character varying(255) COLLATE pg_catalog."default",
    # comm_structure character varying(255) COLLATE pg_catalog."default",
    # gcoord json,
    # gcenter json,




class Communities(object):
    comm_code = Column(String, primary_key=True)
    name = Column(String)
    sector = Column(String)
    cclass = Column(String)
    res_cnt = Column(String)
    dwell_cnt = Column(String)
    com_structure = Column(String)
    gcoord = Column(String)
    gcenter = Column(String)

def set_query_table():

    #census = Table('census2018', metadata, autoload=True)
    census = Table('cgy2018', metadata, 
    Column('comm_code', String, primary_key=True),
    Column('name', String),
    Column('sector', String),
    Column('cclass', String),
    Column('res_cnt', String),
    Column('dwell_cnt', String),
    Column('comm_structure', String),
    Column('gcoord', String),
    Column('gcenter', String) )

    mapper(Communities, census)
    session = Session()
    return session

def get_community_list():
    session = set_query_table()
    res = session.query(Communities) \
    .filter(Communities.cclass == 'Residential' ) \
    .all()
    result = []
    for item in res:
        result.append (item.name)
    return result

#get_community_list()
print (get_community_list())



