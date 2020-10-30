import sys
import drive
import os 

def download():
    if len(sys.argv) != 3:
        print("wrong arguments")
        sys.exit()
    else:
        ss = drive.GoogleDrive('token.pickle', 'credentials.json')
        ss.authenticate()
        folder_id = ss.search("mimeType = 'application/vnd.google-apps.folder' and name='%s'" % sys.argv[1], "folder")
        file_infos = ss.search("mimeType='application/pdf' and parents in '{}'".format(folder_id), "file")
        ss.download(folder_id, file_infos, os.environ['HOME'] + sys.argv[2], ".pdf")
        
if "__name__ == __main__":
    download()
