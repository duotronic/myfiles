_author_ = 'mark ketter 2016/11/17'
_project_ = ''
import os, csv, datetime, time, pathlib, hashlib

from sqlalchemy import *
import ntpath
import send2trash
import zipfile
from dirZip import dirToZip
from classes import FInfo
from classes import AppUtil

def rna(text):
    #return text.encode("utf-8", "replace")
    return(text)

def csvWriteRow(csvWriter, fileInfo):
    csvWriter.writerow([fileInfo.fileid, fileInfo.set, fileInfo.extension, 
                fileInfo.name, str(fileInfo.size), fileInfo.modtime, 
                fileInfo.flex1, fileInfo.hash, fileInfo.path])

def zipSln(connection, errFileName, timeStamp):
    filesmeta = Table('filesmeta', MetaData(),
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

    errFileObj = open(errFileName, 'w')
    errStr = 'zipSln{}'.format(timeStamp + '\n')
    errFileObj.write(errStr)
    errCount = 0
    s = select([filesmeta]).where(filesmeta.c.extension == '.sln')
    rp = connection.execute(s)

    #    #shutil.rmtree(fileMeta.path)

    slnCount = 0
    for fileMeta in rp:
        slnCount =+ 1
        errCnt = dirToZip(fileMeta.path, errFileObj)
        errCount = errCount + errCnt
        #print('name: {}, ext: {}, path: {}'.\
        #    format(rna(fileMeta.name), fileMeta.extension, rna(fileMeta.path)))

    errFileObj.close()
    print('files: {} errors: {}'.format(slnCount,errCount))
    return

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            #ziph.write(os.path.join(root, file))
            ziph.write(
                os.path.relpath(
                    os.path.join(root, file), os.path.join(path, '..')))

def dbFileAction(connection):
    filesmeta = Table('filesmeta', MetaData(),
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
    s = select([filesmeta]).where(filesmeta.c.extension == '.jpg')
    rp = connection.execute(s)
    count = 1
    for fileMeta in rp:
        print(rna(fileMeta.path))
        #print('name: {}, ext: {}, path: {}'.\
        #    format(rna(fileMeta.name), fileMeta.extension, rna(fileMeta.path)))
        count += 1

    print(count)
    return
    
def FileMetaCsv2Db(csvFileName,conn,db,errFileObj):
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

    aU = AppUtil()
    errStr = 'FileMetaCsv2Db: {}'.format(aU.timeStamp())
    errFileObj.write(errStr)

    print('{:17} - {}'.format('csv into db:', \
            str(time.strftime('%Y-%m-%dT%H:%M:%S'))))

    csvFileObj = open(csvFileName, 'r')
    read_eof = False
    while not read_eof:
        try:
            csvLine = csvFileObj.readline().strip()
            if len(csvLine) > 0:
                # lineCount += 1
                pass    
            else:
                read_eof = True
        except:
            pass
            read_eof = True
        
        if not read_eof:
            csvFields = csv.reader([csvLine])
            c = list(csvFields)        
            nFInfo = {  'set':   c[0][1], 'extension': c[0][2], 
                        'name':  c[0][3], 'size':   c[0][4], 'modtime': c[0][5],  
                        'flex1': c[0][6], 'hash':   c[0][7], 'path':    c[0][8]
                    }
            #print(nFInfo)
            
            ins = filesmeta.insert().values(**nFInfo)

            #print(str(ins)) # view SqlAlchemy meta
            #print(ins.compile().params)
            result = conn.execute(ins)
            x = result.inserted_primary_key
            #fileMeta = FInfo(**nFInfo)
            #print(fileMeta)

    return

def Db_Dups_Delete(connection, errFileName):
    filesmeta = Table('filesmeta', MetaData(),

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

    print('{:17} - {}'.format('Db_Dups_Delete:', \
            str(time.strftime('%Y-%m-%dT%H:%M:%S'))))
    fileCount = 0

    s = select([filesmeta])
    s = s.order_by(desc(filesmeta.c.hash),asc(filesmeta.c.modtime))
    rp = connection.execute(s)

    prevHash = 'a'
    prevMeta = FInfo()
    for fileMeta in rp:
        if (fileCount %1000 == 0):
            print('{:05d} - {}'.format(fileCount, \
                    str(time.strftime('%Y-%m-%dT%H:%M:%S'))))
        fileCount += 1
        filehash = fileMeta.hash
        if prevHash == filehash:
            try:
                fullFileName = fileMeta.path + '\\' + fileMeta.name + fileMeta.extension
                send2trash.send2trash(fullFileName)
                #os.unlink(fullFileName)
                s = delete(filesmeta).where(filesmeta.c.fileid == fileMeta.fileid)
                result = connection.execute(s)
                continue
            except Exception as other:
                print('broke: ', other)
                print('fileid: {}, file count: {}'.\
                    format(fileMeta.fileid, fileCount))
        else:
            prevHash = filehash
            prevMeta = fileMeta

    print('{}: Deleted'.format(fileCount))
    return

def DbDups2Csv(connection,csvDupsName):
    filesmeta = Table('filesmeta', MetaData(),
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

    print('{:17} - {}'.format('Db_Dups_2_Csv:', \
            str(time.strftime('%Y-%m-%dT%H:%M:%S'))))
    
    csvFileObj = open(csvDupsName, 'w', newline='')
    csvWriter = csv.writer(csvFileObj)
    #csvFileHeaderStr = "fileid,set,extension,name,size,modTime,flex1,hash,path\n"
    #csvFileObj.write(csvFileHeaderStr)

    s = select([filesmeta])
    s = s.order_by(desc(filesmeta.c.hash),asc(filesmeta.c.modtime))
    rp = connection.execute(s)

    prevHash = 'a'
    prevMeta = FInfo()
    prevMetaWriteCount = 0
    for fileMeta in rp:
        filehash = fileMeta.hash
        if prevHash == filehash:
            if (prevMetaWriteCount == 0):
                csvWriteRow(csvWriter, prevMeta)
                prevMetaWriteCount = 1
            csvWriteRow(csvWriter, fileMeta)
            continue
        else:
            prevHash = filehash
            prevMeta = fileMeta
            prevMetaWriteCount = 0

    #prevHash = 'a'
    #prevMeta = FInfo()
    #for fileMeta in rp:
    #    filehash = fileMeta.hash
    #    if prevHash == filehash:
    #        csvWriteRow(csvWriter, fileMeta)
    #        continue
    #    else:
    #        #csvWriteRow(csvWriter, prevMeta)
    #        prevHash = filehash
    #        prevMeta = fileMeta

    csvFileObj.close()

    return






    #s = select([filesmeta]).where(filesmeta.c.name.contains('e'))
    #s = s.distinct(filesmeta.c.hash)
    #s = select([filesmeta.c.fileid, \
    #            filesmeta.c.set, \
    #            filesmeta.c.extension, \
    #            filesmeta.c.name, \
    #            filesmeta.c.size, \
    #            filesmeta.c.modtime, \
    #            filesmeta.c.flex1, \
    #            filesmeta.c.hash, \
    #            filesmeta.c.path])