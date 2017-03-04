from collections import namedtuple
from datetime import time
from sqlalchemy import *

def createTables(engine):
    metadata = MetaData()

    filesmeta = Table('filesmeta', metadata,
        Column('fileid', Integer(), primary_key=True),
        Column('set', String(50)),
        Column('extension', String(255)),
        Column('name', String(255)),
        Column('size', Integer()),
        Column('modtime', String(50)),
        Column('flex1', String(255)),
        Column('hash', String(255), index=True),
        Column('path', String(255))
    )
    
    metadata.create_all(engine)
    pass

def ConnectExistingTables(conn):
    metadata = MetaData(conn)
    dbFilesMeta = Table('filesmeta', metadata, autoload = True)
    return(dbFilesMeta)

def del_filesmeta(conn, finfo):
    metadata = MetaData()

    filesmeta = Table('filesmeta', metadata,
        Column('fileid', Integer(), primary_key=True),
        Column('set', String(50)),
        Column('extension', String(255)),
        Column('name', String(255)),
        Column('size', Integer()),
        Column('modtime', String(50)),
        Column('flex1', String(255)),
        Column('hash', String(255), index=True),
        Column('path', String(255))
    )

    u = delete(filesmeta).where(
        filesmeta.c.fileid == finfo.fileid)
    result = conn.execute(u)
    x = result.rowcount
    pass
    


