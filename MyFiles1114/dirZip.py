#! python3
# backupToZip.py - Copies an entire folder and its contents into
# a ZIP file whose filename_ increments.

import zipfile, os, shutil ##1
import ntpath

 
def path_leaf(path):
# http://stackoverflow.com/questions/8384737/extract-file-name-
#    from-path-no-matter-what-the-os-path-format
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def dirToZip(folder, errFileObj):
# Backup the entire contents of "folder" into a ZIP file.
# the backup_ zip file is stored inside the directory being backed up

    folder = os.path.abspath(folder) # make sure folder is absolute

    zipFileName = path_leaf(folder) +'.zip'
    #zipFilePath = os.path.join(folder, zipFileName)
    #if os.path.isfile(zipFilePath):
    #    print('conflict: zip file exists at: {}').format(zipFilePath)
    #    return

    # testing seam - zip file location
    zipFileDir = r'J:\temp'

    print('Creating {} \nin: {}...'.format(zipFileName, folder))

    zipPath=os.path.join(zipFileDir, zipFileName)
    backupZip = zipfile.ZipFile(zipPath, 'w')

    # Walk the entire folder tree and compress the files in each folder.
    for foldername, subfolders, filenames in os.walk(folder):
        # Add the current folder to the ZIP file.
        backupZip.write(foldername)

        # Add all the files in this folder to the ZIP file.
        for filename in filenames:
            backupZip.write(os.path.join(foldername, filename))

    backupZip.close()

    if os.path.exists(folder):
        try:
            shutil.rmtree(folder)
        except Exception as other:
            print('\nbroke: {}\n'.format(str(other)))
            errFileObj.write(str(other) + '\n\n')
            #x = input('fix me!')
            return 1
        os.makedirs(folder)

        #move zip from j:\temp to folder
        shutil.move(zipPath,folder)

    return 0
