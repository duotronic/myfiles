import time
class AppUtil():
    """description of class"""
    @staticmethod
    def timeStamp():
        return(str(time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime())))

class classes(object):
    """description of class"""

class OopsException(Exception):
    pass

#from sqlalchemy import MetaData, Table, Column, Integer, \
#                        Numeric, String, ForeignKey, DateTime
#metadata = MetaData()
#filesmeta = Table('filesmeta', metadata,
#    Column('fileid', Integer(), primary_key=True),
#    Column('set', String(50)),
#    Column('extension', String(255)),
#    Column('name', String(255)),
#    Column('size', Integer()),
#    Column('modtime', String(50)),
#    Column('flex1', String(255)),
#    Column('hash', String(255), index=True),
#    Column('path', String(255))
#)

class FInfo:
    def __init__(self, fileid=0, set = '', extension = '', 
                name = '',  size=0, modtime = '', 
                flex1 = '', hash = '', path = ''):
        self.fileid = fileid
        self.set = set
        self.extension = extension
        self.name = name
        self.size = size
        self.modtime = modtime
        self.flex1 = flex1
        self.hash = hash
        self.path = path
    def __eq__(self, finfo2):
        return self.hash.lower() == finfo2.hash.lower()
    def __ne__(self, finfo2):
        return self.hash.lower() != finfo2.hash.lower()
    def __lt__(self, finfo2):
        return self.hash.lower() < finfo2.hash.lower()
    def __gt__(self, finfo2):
        return self.hash.lower() > finfo2.hash.lower()
    def __le__(self, finfo2):
        return self.hash.lower() <= finfo2.hash.lower()
    def __ge__(self, finfo2):
        return self.hash.lower() >= finfo2.hash.lower()
    def __str__(self):
        return ('fileid=%d, set=%s, extension=%s, name=%s, size=%d, modtime=%s, flex1=%s, hash=%s, path=%s' %
            (self.fileid,
             self.set,
             self.extension,
             self.name,
             self.size,
             self.modtime,
             self.flex1,
             self.hash,
             self.path))

