"""
Google Drive Integration Module
Handles authentication, file listing, downloading, and uploading to Google Drive
"""

import os
import io
import pickle
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import tempfile

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDriveManager:
    """Manages Google Drive operations for OCR processing"""
    
    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Initialize Google Drive Manager
        
        Args:
            credentials_path: Path to credentials.json file
            token_path: Path to token.pickle file for storing authentication
        """
        self.credentials_path = credentials_path or 'credentials.json'
        self.token_path = token_path or 'token.pickle'
        self.service = None
        self.creds = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with Google Drive API
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Load existing credentials
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # If there are no (valid) credentials available, let the user log in
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        raise FileNotFoundError(
                            f"Credentials file not found: {self.credentials_path}\n"
                            "Please download credentials.json from Google Cloud Console"
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(self.token_path, 'wb') as token:
                    pickle.dump(self.creds, token)
            
            # Build the service
            self.service = build('drive', 'v3', credentials=self.creds)
            return True
            
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.service is not None
    
    def list_folders(self, parent_id: Optional[str] = None) -> List[Dict]:
        """
        List folders in Google Drive
        
        Args:
            parent_id: Parent folder ID (None for root)
            
        Returns:
            List of folder dictionaries with 'id' and 'name'
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated. Call authenticate() first.")
        
        try:
            query = "mimeType='application/vnd.google-apps.folder'"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            else:
                query += " and 'root' in parents"
            
            query += " and trashed=false"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, parents)',
                orderBy='name'
            ).execute()
            
            folders = results.get('files', [])
            return folders
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
    
    def list_files_in_folder(self, folder_id: str, file_extensions: Optional[List[str]] = None) -> List[Dict]:
        """
        List files in a specific folder
        
        Args:
            folder_id: Google Drive folder ID
            file_extensions: List of file extensions to filter (e.g., ['.pdf', '.jpg'])
            
        Returns:
            List of file dictionaries with 'id', 'name', and 'mimeType'
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated. Call authenticate() first.")
        
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            query += " and mimeType!='application/vnd.google-apps.folder'"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, size)',
                orderBy='name'
            ).execute()
            
            files = results.get('files', [])
            
            # Filter by extensions if provided
            if file_extensions:
                extensions_lower = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                                  for ext in file_extensions]
                files = [f for f in files if any(f['name'].lower().endswith(ext) 
                                                for ext in extensions_lower)]
            
            return files
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
    
    def download_file(self, file_id: str, destination_path: str) -> bool:
        """
        Download a file from Google Drive
        
        Args:
            file_id: Google Drive file ID
            destination_path: Local path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated. Call authenticate() first.")
        
        try:
            request = self.service.files().get_media(fileId=file_id)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            with io.FileIO(destination_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    
            return True
            
        except HttpError as error:
            print(f"An error occurred downloading file: {error}")
            return False
    
    def upload_file(self, file_path: str, folder_id: str, file_name: Optional[str] = None) -> Optional[str]:
        """
        Upload a file to Google Drive
        
        Args:
            file_path: Local file path to upload
            folder_id: Google Drive folder ID to upload to
            file_name: Name for the file in Drive (defaults to local filename)
            
        Returns:
            File ID if successful, None otherwise
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated. Call authenticate() first.")
        
        try:
            if not file_name:
                file_name = os.path.basename(file_path)
            
            # Determine MIME type based on extension
            mime_types = {
                '.txt': 'text/plain',
                '.json': 'application/json',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.doc': 'application/msword',
                '.pdf': 'application/pdf',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
            }
            
            ext = os.path.splitext(file_path)[1].lower()
            mime_type = mime_types.get(ext, 'application/octet-stream')
            
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
            
        except HttpError as error:
            print(f"An error occurred uploading file: {error}")
            return None
    
    def get_folder_path(self, folder_id: str) -> str:
        """
        Get the full path of a folder
        
        Args:
            folder_id: Google Drive folder ID
            
        Returns:
            Full path string
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated. Call authenticate() first.")
        
        try:
            path_parts = []
            current_id = folder_id
            
            while current_id:
                file = self.service.files().get(
                    fileId=current_id,
                    fields='id, name, parents'
                ).execute()
                
                path_parts.insert(0, file.get('name', 'Unknown'))
                
                parents = file.get('parents', [])
                current_id = parents[0] if parents else None
            
            return ' / '.join(path_parts)
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return "Unknown Path"
    
    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """
        Create a new folder in Google Drive
        
        Args:
            folder_name: Name of the folder to create
            parent_id: Parent folder ID (None for root)
            
        Returns:
            Folder ID if successful, None otherwise
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated. Call authenticate() first.")
        
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
            
        except HttpError as error:
            print(f"An error occurred creating folder: {error}")
            return None
    
    def delete_credentials(self):
        """Delete stored credentials (logout)"""
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
            self.service = None
            self.creds = None
            return True
        return False

