import sys
import drive
import os 

def upload():
    if len(sys.argv) != 4:
        print("wrong arguments")
        sys.exit()
    else:
        ss = drive.GoogleDrive('token.pickle', 'credentials.json')
        ss.authenticate()
        folder_id = ss.search("mimeType = 'application/vnd.google-apps.folder' and name='%s'" % sys.argv[1], "single")
        ss.upload(folder_id, os.environ['HOME'] + sys.argv[2], sys.argv[3]) 
        
if "__name__ == __main__":
    upload()
