_author_ = 'mark ketter 2016/08/07'
_project_ = 'list filenames w/set, path, name, extension, size, modification date&time, and md5 hash'
import os, csv, datetime, time, pathlib, hashlib
from unidecode import unidecode
from classes import FInfo
from classes import AppUtil

def checksum_md5(filename):
#http://stackoverflow.com/questions/1131220/
#get-md5-hash-of-big-files-in-python?noredirect=1&lq=1
    md5 = hashlib.md5()
    with open(filename,'rb') as f: 
        for chunk in iter(lambda: f.read(8192), b''): 
            md5.update(chunk)
    #return md5.digest() #returns binary string
    return md5.hexdigest()

def remove_non_ascii(text):
    return str(text.encode("utf-8", "replace"),'utf-8')

def version(): 
    return('filedata, 2016-11-26T17:40:00')

def FileMeta2Csv(filesSource, filesetname, flex1, csvFileName, errFileObj):
    print('{:17} - {}'.format('FileMeta2Csv:', \
            str(time.strftime('%Y-%m-%dT%H:%M:%S'))))
    aU = AppUtil()
    errStr = 'FileMeta2Csv: {}'.format(aU.timeStamp())
    errFileObj.write(errStr)
    csvFileObj = open(csvFileName, 'w', newline='')

    #csvFileHeaderStr = "fileid,set,extension,name,size,modTime,flex1,hash,path\n"
    #csvFileObj.write(csvFileHeaderStr)

    csvWriter = csv.writer(csvFileObj)

    filesScannedCnt = 0
    filesFilteredCnt = 0

    for root, directories, filenames in os.walk(filesSource):
        #for directory in directories:
            #print (os.path.join(root, directory))
        for filename in filenames:
            fileNamePath = os.path.join(root, filename)

            if not os.path.exists(fileNamePath):
                continue

            filesScannedCnt += 1
            print('.', end="", flush=True)
            if (filesScannedCnt %500 == 0):
                print('\n{:05d} - {}'.format(filesScannedCnt, \
                        str(time.strftime('%Y-%m-%dT%H:%M:%S'))))

            fileInfo = FInfo()
            fileNameExtension = pathlib.Path(fileNamePath).suffix

            # filter - file extension
            extensions = ['.gif','.jpg','.jpeg','.png','.txt']
            #extensions = ['.mp3','.jpg','.jpeg','.png']
            #extensions = ['.mp3','.wma']
            #if not (fileNameExtension.lower() in extensions):
            #    continue

            fileModTime = os.path.getmtime(fileNamePath)
            fileModTime = datetime.datetime.fromtimestamp(fileModTime)
            # date formated for string sort
            fileInfo.modtime = fileModTime.strftime('%Y-%m-%dT%H:%M:%S')
            # date formatted for excel
            #fileDateTimeStr = fileDateTime.strftime('%m/%d/%y %H:%M')

            # filter - date & time
            beginDateTime = datetime.datetime(2016, 1, 1, 0, 0, 0)
            endDateTime = datetime.datetime(2016, 12, 31, 23, 59, 59)
            #if not ((fileModTime >= beginDateTime) and (fileModTime <= endDateTime)):
            #    continue

            filesFilteredCnt += 1
            fileInfo.set = filesetname
            fileName = os.path.basename(fileNamePath)
            filename = fileName[0:fileName.rfind(fileNameExtension)]
            fileInfo.name = remove_non_ascii(filename)
            fileInfo.extension = fileNameExtension.lower()
            fileInfo.path = os.path.dirname(fileNamePath)
            fileInfo.size = os.path.getsize(fileNamePath)
            fileInfo.flex1 = flex1

            fileInfo.hash = checksum_md5(fileNamePath)

            #print(fileInfo)
            try:
                csvWriter.writerow([fileInfo.fileid, fileInfo.set, fileInfo.extension, 
                            fileInfo.name, str(fileInfo.size), fileInfo.modtime, 
                            fileInfo.flex1, fileInfo.hash, fileInfo.path])
            except Exception as other:
                print('problem: ', other)
                print('count: {0}'.format(filesFilteredCnt))
                #fullFileName = fileInfo.path + '\\' + fileInfo.name + fileInfo.extension
                #fullFileName = remove_non_ascii(fullFileName)
                #errFileObj.write(fullFileName)

    csvFileObj.close()

    outputStr = "\noutput file: {0:s}\nfiles scanned: {1:n}, files processed: {2:n}\n"\
        .format(csvFileObj.name, filesScannedCnt, filesFilteredCnt)
    print(outputStr)