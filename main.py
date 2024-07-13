from __future__ import print_function
import os
import io
import zipfile
import argparse

from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

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
        creds = None
        cwd_dir = os.getcwd()
        credential_dir = os.path.join(cwd_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'google-drive-credentials.json')

        if os.path.exists(credential_path):
            creds = Credentials.from_authorized_user_file(credential_path, self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRET_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open(credential_path, 'w') as token:
                token.write(creds.to_json())

        return creds

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

    SCOPES = ['https://www.googleapis.com/auth/drive']
    CLIENT_SECRET_FILE = 'client_secret.json'
    APPLICATION_NAME = 'Drive API Python Quickstart'
    
    authInst = Auth(SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME)
    credentials = authInst.getCredentials()
    
    drive_service = discovery.build('drive', 'v3', credentials=credentials)

    createFolderAndUpload(drive_service, args.folder_name, args.folder_path)
