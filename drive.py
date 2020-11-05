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
mimes = {"pdf" : 'application/pdf', "aiff" : 'audio/x-aiff', "aif" : 'audio/aiff', "jpg" : 'image/jpeg', "drive-folder" : 'application/vnd.google-apps.folder', "wav" : 'audio/wav'}

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
    
    def search(self, queryType, searchType):
        response = self.service.files().list(
                            q=queryType,
                            fields='nextPageToken, files(id, name)',
                            ).execute()
        results = []
        for item in response.get('files', []):
            print(u'{0} ({1})'.format(item['name'], item['id']))
            if searchType == "single":
                return item['id']
            else:
                results.append((item['id'], item['name']))
        return results
    
    def remove_duplicate_u(self, files, folder_id):
        sf = self.search("parents in '{}'".format(folder_id), "file")
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
            file_metadata = {
                'name' : file_name,
                'parents' : [folder_id]
            }
            media = MediaFileUpload(dir_path+file_name, resumable=True)
            f = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute() 
            print("file id: %s" % f.get('id'))

    def download(self, folder_id, dest, fileExt):
        file_infos = self.search("mimeType='{}' and parents in '{}'".format(mimes[fileExt], folder_id), "multiple")
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
        print("finding subfolders...")
        sub_folders = self.search("mimeType='{}' and parents in '{}'".format(mimes["drive-folder"], folder_id), "multiple")
        for subf in sub_folders:
            self.downloadRec(subf[0], dest+subf[1]+"/", fileExt)
