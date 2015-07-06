from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import mapper
from sqlalchemy import create_engine, MetaData

engine = create_engine('sqlite:///gigaset.db', convert_unicode=True)
metadata = MetaData(bind=engine)

if __name__ == '__main__':
    cronologia = Table('cronologia', metadata, autoload=True)
    lista = cronologia.select(cronologia.c.mac=='7c2f8097cb6d').execute()
    for oggetto in lista:
        print oggetto['mac'], oggetto['state']
    con = engine.connect()
    con.execute(cronologia.insert(), mac='7c2f8097cb6d', timestamp='0', state='out')