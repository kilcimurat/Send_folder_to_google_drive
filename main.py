from __future__ import print_function
import httplib2
import os, io
import zipfile
import argparse

from googleapiclient import discovery
from oauth2client import client
from oauth2client.file import Storage
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

class Auth:
    def __init__(self, SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME):
        self.SCOPES = SCOPES
        self.CLIENT_SECRET_FILE = CLIENT_SECRET_FILE
        self.APPLICATION_NAME = APPLICATION_NAME

    def getCredentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        cwd_dir = os.getcwd()
        credential_dir = os.path.join(cwd_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'google-drive-credentials.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            credentials = tools.run_flow(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

def zipFolder(folder_path, zip_name):
    zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))
    zipf.close()

def uploadZipFile(drive_service, zip_filename, folder_id):
    media = MediaFileUpload(zip_filename, mimetype='application/zip')
    file_metadata = {
        'name': os.path.basename(zip_filename),
        'parents': [folder_id]
    }
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print('File ID: %s' % file.get('id'))

def createFolderAndUpload(drive_service, folder_name, folder_path):
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
    folder_id = folder.get('id')
    print('Folder ID: %s' % folder_id)
    
    zip_filename = f'{folder_name}.zip'
    zipFolder(folder_path, zip_filename)
    uploadZipFile(drive_service, zip_filename, folder_id)
    
    # Optional: Delete the local zip file after uploading
    os.remove(zip_filename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Drive Folder Upload Script')
    parser.add_argument('folder_name', help='Name of the folder to create in Google Drive')
    parser.add_argument('folder_path', help='Local path of the folder to upload')

    args = parser.parse_args()

    SCOPES = 'https://www.googleapis.com/auth/drive'
    CLIENT_SECRET_FILE = 'client_secret.json'
    APPLICATION_NAME = 'Drive API Python Quickstart'
    
    authInst = Auth(SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME)
    credentials = authInst.getCredentials()
    
    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http)

    createFolderAndUpload(drive_service, args.folder_name, args.folder_path)
