from __future__ import print_function
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

SCOPES = 'https://www.googleapis.com/auth/drive'

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
            if searchType == "folder":
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

    def download(self, folder_id, file_infos, dest, fileExt):
        ffiles = self.remove_duplicate_d(file_infos, dest, fileExt)
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
                print("Download %d%%." % int(status.progress() * 100), end='\r')
                sys.stdout.flush()
            print('')

if __name__ == "__main__":
    ss = GoogleDrive('token.pickle', 'credentials.json')
    ss.authenticate()
    folder_id = ss.search("mimeType = 'application/vnd.google-apps.folder' and name='test'", "folder")
    # ss.upload(folder_id, os.environ['HOME'] + "/math-solutions/1300/")
    file_infos = ss.search("mimeType='application/pdf' and parents in '{}'".format(folder_id), "file")
    ss.download(folder_id, file_infos, os.environ['HOME'] + "/downloads/")
