_author_ = 'mark ketter 2016/11/28'
_project_ = 'file actions'
import os, csv, datetime, time, pathlib, hashlib
from unidecode import unidecode
import send2trash
import db_utility
import ntpath
from sqlalchemy import *
import zipfile
from classes import FInfo
from classes import AppUtil

def FixUnicode(text):
    return str(text.encode("utf-8", "replace"))

    #"".join([x if ord(x) < 128 else '?' for x in text])
    #return text.decode('utf-8','ignore').encode("utf-8")
    #return ''.join([i if ord(i) < 128 else ' ' for i in text])
    #return unidecode(unicode(text, encoding = "utf-8"))

def listdirs(folder):
# http://stackoverflow.com/questions/141291
# /how-to-list-only-top-level-directories-in-python
    return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]

def path_leaf(path):
# http://stackoverflow.com/questions/8384737/extract-file-name-
#    from-path-no-matter-what-the-os-path-format
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def version(): 
    return('filedata, 2016-11-26T17:40:00')

def dirsZip(srcDir, outputDir, errFileObj):
# do not use - use windows utils; this def() doesn't handle errors
# Backup the entire contents of "folder" into a ZIP file.
# the backup_ zip file is stored inside the directory being backed up
    aU = AppUtil()
    errStr = 'dirsZip: {}'.format(aU.timeStamp())
    errFileObj.write(errStr)

    srcDir = os.path.abspath(srcDir) # make sure folder is absolute

    dirList = listdirs(srcDir)
    for dir in dirList:
        zipFileName = path_leaf(dir) +'.zip'
        zipPath=os.path.join(outputDir, zipFileName)
        if os.path.exists(zipPath):
            errMsgStr = '!skipped (exists): {}'.format(zipPath)
            errFileObj.write(errMsgStr + '\n')
            print(errMsgStr)
            continue
        else:
            print('Creating {} \nin: {}...'.format(zipFileName, srcDir))

        # create zip files for each folder
        backupZip = zipfile.ZipFile(zipPath, 'w')
        for foldername, subfolders, filenames in os.walk(srcDir):
            # Add the current folder to the ZIP file.
            print('zipping folder{} :'.format(foldername))
            backupZip.write(foldername)

            # Add all the files in this folder to the ZIP file.
            for filename in filenames:
                print('zipping file{} : '.format(filename))
                backupZip.write(os.path.join(foldername, filename))
        backupZip.close()

def EmptyDirectories(filesSource):
    print('{:17} - {}'.format('EmptyDirectories:', \
            str(time.strftime('%Y-%m-%dT%H:%M:%S'))))
    for root, directories, filenames in os.walk(filesSource):
        for directory in directories:
            path = os.path.join(root, directory)
            try:
                fileList = os.listdir(path)
            except Exception as other:
                print('problem: {}\nDirectory: {}'.format(other,directory))
                continue
            if len(fileList) == 0:
                try:
                    os.rmdir(path)
                except Exception as other:
                    print('problem: ', other)
                    #print('{} - {}'.format(len(fileList),path))
                    pass
    return
  
def FileCullAttr(filesSource, flex1):
    print('{:17} - {}'.format('FileCullAttr:', \
            str(time.strftime('%Y-%m-%dT%H:%M:%S'))))

    filesScannedCnt = 0
    filesFilteredCnt = 0

    for root, directories, filenames in os.walk(filesSource):
        for filename in filenames:
            continue
            fileNamePath = os.path.join(root, filename)

            if not os.path.exists(fileNamePath):
                continue
            
            filesScannedCnt += 1
            fileInfo = FInfo()

            fileInfo.set = 'x'
            fileInfo.flex1 = flex1
            fileInfo.hash = 'h1'
            nameActionFlg = False 
            extensionActionFlg = False
            pathActionFlg = False
            sizeActionFlg = False
            datetimeActionFlg = False

            # file extension
            fileNameExtension = pathlib.Path(fileNamePath).suffix
            fileExtension = fileNameExtension.lower()
            fileInfo.extension = fileExtension
            proc_list = ['.txt','.ini','.pls','.wpc','.xpsf','.db']
            if fileNameExtension in proc_list:
                extensionActionFlg = True

            # file name
            fileName = os.path.basename(fileNamePath)
            filename = fileName[0:fileName.rfind(fileNameExtension)]
            fileInfo.name = filename
            # nameActionFlg = false

            # file path
            fileInfo.path = os.path.dirname(fileNamePath)
            #pathActionFlg = False

            # file size
            fileInfo.size = os.path.getsize(fileNamePath)
            if fileInfo.size == 0:
                sizeActionFlg = True

            fileModTime = os.path.getmtime(fileNamePath)
            fileModTime = datetime.datetime.fromtimestamp(fileModTime)
            # date formated for string sort
            fileInfo.modtime = fileModTime.strftime('%Y-%m-%dT%H:%M:%S')
            # date formatted for excel
            #fileInfo.modtime = fileDateTime.strftime('%m/%d/%y %H:%M')

            # date & time
            #beginDateTime = datetime.datetime(2016, 7, 14, 0, 0, 0)
            #endDateTime = datetime.datetime(2017, 7, 31, 23, 59, 59)
            #if not ((fileModTime >= beginDateTime) and (fileModTime <= endDateTime)):
                #datetimeActionFlg = True

            fullFileName = fileInfo.path + '\\' + fileInfo.name + fileInfo.extension
        
            if nameActionFlg or extensionActionFlg \
                or nameActionFlg or sizeActionFlg \
                or datetimeActionFlg:
                filesFilteredCnt += 1

                send2trash.send2trash(fullFileName)
                #os.unlink(fullFileName)

    outputStr = "files scanned: {0:n}, files processed: {1:n}\n"\
                    .format(filesScannedCnt, filesFilteredCnt)
    print(outputStr)
    return

def csv_dups_delete(csvDupsName, conn, errFileName):
    print('{:17} - {}'.format('Action_CsvFile:', \
            str(time.strftime('%Y-%m-%dT%H:%M:%S'))))

    csvFileObj = open(csvDupsName, 'r')
    errFileObj = open(errFileName, 'w')
    lineCount = 0
    delCount = 0
    read_eof = False
    while not read_eof:
        try:
            csvLine = csvFileObj.readline().strip()
            if len(csvLine) > 0:
                lineCount += 1
                pass    
            else:
                read_eof = True
        except:
            pass
            read_eof = True
        
        if not read_eof:
            csvFields = csv.reader([csvLine])
            c = list(csvFields)        
            x = {'fileid': c[0][0],
                    'set': c[0][1],     'extension': c[0][2], 
                    'name':  c[0][3],   'size': c[0][4], 
                    'modtime': c[0][5], 'flex1': c[0][6], 
                    'hash': c[0][7],    'path': c[0][8]}
            xFInfo = FInfo(**x)
            if xFInfo.flex1 == 'del':
                try:
                    delCount += 1
                    db_utility.del_filesmeta(conn, xFInfo)

                    fullFileName = xFInfo.path + '\\' + xFInfo.name + xFInfo.extension
                    print('{}\n'.format(fullFileName))
                    send2trash.send2trash(fullFileName)
                    #os.unlink(fullFileName)
                except Exception as other:
                    print('broke: ', other)
                    fullFileName = xFInfo.path + '\\' + xFInfo.name + xFInfo.extension
                    fullFileName = fullFileName.encode("utf-8", "replace")
                    errFileObj.write(str(fullFileName))

    print('{}: Records, {}: Deleted'.format(lineCount, delCount))
    return


