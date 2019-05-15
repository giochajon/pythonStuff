from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker
 

#Session = sessionmaker(bind=engine)

#Base = declarative_base()

class Communities(object):
    pass

def loadSession():

    engine = create_engine('postgresql://giovas:belial@localhost:5432/cgyinfo')
    metadata = MetaData(engine)
    census = Table('census2018', metadata, autoload=True)
    mapper(Communities, census)
 
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
 
if __name__ == "__main__":
    session = loadSession()
    res = session.query(Communities).all()
    #print(res[0].name)
    for item in res:
        print (item.name, item.sector)