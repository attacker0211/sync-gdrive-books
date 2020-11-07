import pickle
import os
import io
import glob
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pathlib import Path

SCOPES = "https://www.googleapis.com/auth/drive"
mimes = {"pdf" : 'application/pdf', "aiff" : 'audio/x-aiff', "aif" : 'audio/aiff', "JPG" : 'image/jpeg', "drive-folder" : 'application/vnd.google-apps.folder', "wav" : 'audio/wav'}

class GoogleDrive():
    def __init__(self, tokFile, credFile, scopeType=SCOPES):
        self.tokFile = tokFile
        self.credFile = credFile
        self.service = None
        self.scopeType = scopeType

    def authenticate(self):
        creds = None
        if os.path.exists(self.tokFile):
            with open(self.tokFile, 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credFile, self.scopeType)
                creds = flow.run_local_server(port=0)
            with open(self.tokFile, 'wb') as token:
                pickle.dump(creds, token)
        self.service = build('drive', 'v3', credentials=creds)

    def unlink(self):
        os.chdir(os.environ['HOME'] + "/drive")
        if os.path.exists(self.tokFile):
            os.remove(self.tokFile)
    
    def search(self, queryType):
        response = self.service.files().list(
                            q=queryType,
                            fields='nextPageToken, files(id, name)',
                            ).execute()
        results = []
        for item in response.get('files', []):
            print(u'{0} ({1})'.format(item['name'], item['id']))
            results.append((item['id'], item['name']))
        return results
    
    def create(self, name, fileType, parents, dir_path):
        file_metadata = {}
        file_metadata["name"] = name
        if parents != None:
            file_metadata["parents"] = [parents]
        if fileType == "folder":
            file_metadata["mimeType"] = mimes["drive-folder"]
            f = self.service.files().create(body=file_metadata,fields='id').execute()
            print("create folder id: %s" % f.get('id'))
            return f
        else:
            media = MediaFileUpload(dir_path+name, resumable=True)
            f = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute() 
            print("create file id: %s" % f.get('id'))
            return f
    
    def check_folder(self, name, parent):
        query = "mimeType='%s' and name='%s'" % (mimes["drive-folder"], name)
        if parent != None:
            query += " and parents in '%s'" % (parent)
        folder_info = self.search(query)
        folder_id = ""
        if len(folder_info) == 0:
            folder_id = self.create(name, "folder", parent, None)
        else:
            folder_id = folder_info[0][0]
        return folder_id
        
    def remove_duplicate_u(self, files, folder_id):
        sf = self.search("parents in '%s'" % (folder_id))
        efs = [f[1] for f in sf]
        ffiles = filter(lambda f: f not in efs, files)
        return ffiles
    
    def remove_duplicate_d(self, files, dest, fileExt):
        os.chdir(dest)
        efs = [f for f in glob.glob("*" + fileExt)]
        ffiles = filter(lambda f: f[1] not in efs, files)
        return ffiles

    def upload(self, folder_id, dir_path, fileExt):
        os.chdir(dir_path)
        files = [f for f in glob.glob("*" + fileExt)]
        ffiles = self.remove_duplicate_u(files, folder_id)
        for file_name in ffiles:
            self.create(file_name, "file", folder_id, dir_path)

    def uploadRec(self, folder_id, dir_path, fileExt):
        self.upload(folder_id, dir_path, fileExt)
        sub_folders = glob.glob("*/") 
        for subf in sub_folders:
            sub_id = self.check_folder(subf[:-1], folder_id) 
            self.uploadRec(sub_id, dir_path+subf, fileExt)

    def download(self, folder_id, dest, fileExt):
        query = ""
        if fileExt != "*":
            query += "mimeType='%s' and" % (mimes[fileExt])
        query += "parents in '%s'" % (folder_id)
        file_infos = self.search(query)
        if not os.path.exists(dest):
            os.makedirs(dest)
        ffiles = self.remove_duplicate_d(file_infos, dest, "." + fileExt)
        for file_info in ffiles:
            request = self.service.files().get_media(fileId=file_info[0])
            fh = io.FileIO(dest + file_info[1], 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                try:
                    status, done = downloader.next_chunk()
                except:
                    fh.close()
                    os.remove(dest + file_info[0])
                    sys.exit(1)
                print("Download %s %d%%." % (file_info[1], int(status.progress() * 100)), end='\r')
                sys.stdout.flush()
            print('')

    def downloadRec(self, folder_id, dest, fileExt):
        self.download(folder_id, dest, fileExt)
        sub_folders = self.search("mimeType='{}' and parents in '{}'".format(mimes["drive-folder"], folder_id))
        for subf in sub_folders:
            self.downloadRec(subf[0], dest+subf[1]+"/", fileExt)
