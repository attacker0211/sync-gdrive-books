import sys
import drive
import os 


def downloadRec():
    if len(sys.argv) != 4:
        print("wrong arguments")
        sys.exit()
    else:
        ss = drive.GoogleDrive('token.pickle', 'credentials.json')
        ss.authenticate()
        folder_id = ss.search("mimeType='%s' and name='%s'" % (drive.mimes["drive-folder"], sys.argv[1]), "single")
        ss.downloadRec(folder_id, os.environ['HOME'] + sys.argv[2], sys.argv[3])
        
if "__name__ == __main__":
    downloadRec()
