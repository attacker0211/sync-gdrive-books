import sys
import drive
import os 

def uploadRec():
    if len(sys.argv) != 4:
        print("wrong arguments")
        sys.exit()
    else:
        ss = drive.GoogleDrive('token.pickle', 'credentials.json')
        ss.authenticate()
        folder_id = ss.check_folder(sys.argv[1], None) 
        ss.uploadRec(folder_id, os.environ['HOME'] + sys.argv[2], sys.argv[3]) 
        
if "__name__ == __main__":
    uploadRec()
