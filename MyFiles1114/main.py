import os, csv, datetime, time, pathlib, hashlib
from collections import namedtuple
from sqlalchemy import *

import file_data
import file_action
import db_app
import db_utility

if __name__ == '__main__':
    ######################################################
    # create a files data .csv file
    timeStamp = time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime())

    filesSource = r'M:\2017Media'
    MetaSet = '2017Media'
    outputDir = r'j:\\temp'

    #filesSource = r'J:\eBooks-Topics'
    #MetaSet = 'eBkPub'

    flex1 = 'F1'
    userDocsPath = os.getenv('USERPROFILE') + r'\Documents'
    csvOutputDir = userDocsPath

    csvDataName = os.path.join(csvOutputDir, MetaSet + r'-data.csv')
    csvDupsName = os.path.join(csvOutputDir, MetaSet + r'-dups.csv')
    errFileName = os.path.join(csvOutputDir, MetaSet + r'-errs.txt')
    errFileObj = open(errFileName, 'w')

    print('{:17} - {}'.format('MetaSet:',MetaSet))
    print('{:17} - {}'.format('start:', \
            str(time.strftime('%Y-%m-%dT%H:%M:%S'))))

    ######################################################
    # delete extraneous files
    # .txt, .gif, .jpeg, zero-length
    #file_action.FileCullAttr(filesSource, flex1)
    #file_action.EmptyDirectories(filesSource)

    ######################################################
    # create files meta data csv file
    file_data.FileMeta2Csv(filesSource, MetaSet, flex1, csvDataName, errFileObj) 

    ######################################################
    # db overhead
    dbConnectStr = r'postgresql+psycopg2:' \
                + r'//postgres:postgrespassword@localhost' \
                + r':5432/MYFILES'
    engine = create_engine(dbConnectStr)
    #engine.echo = True                 # db debugging switch
    conn = engine.connect()
    db_utility.createTables(engine)
    dbFilesMeta = db_utility.ConnectExistingTables(conn)

    #######################################################
    # put the files metadata csv into the database
    db_app.FileMetaCsv2Db(csvDataName,conn,dbFilesMeta,errFileObj)

    #######################################################
    # file action select from csv
    # do not use! - file_action.csv_dups_delete(csvDupsName,conn,errFileName)
    # do not use! - file_action.dirsZip(filesSource,outputDir,errFileObj)

    #######################################################
    # file action select from db
    # do not use! - db_app.zipSln(conn, errFileName, timeStamp)
    #db_app.Db_Dups_Delete(conn,errFileName)
    db_app.DbDups2Csv(conn,csvDupsName)

    ######################################################
    # clean up
    #file_action.EmptyDirectories(filesSource)
    errFileObj.close()
    print('{:17} - {}'.format('finished!', \
            str(time.strftime('%Y-%m-%dT%H:%M:%S'))))