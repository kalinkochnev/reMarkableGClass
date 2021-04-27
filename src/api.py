import mimetypes
import os
from typing import List

from fuzzywuzzy import fuzz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import settings
import utils


class Auth:
    scopes = []  # If modifying these scopes, delete the file token.json.

    def __init__(self):
        self.register_scopes()
        self.creds = None
        self.authenticate()

    def authenticate(self):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file(
                'token.json', self.scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scopes)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

    def register_scopes(self):
        for child in Service.__subclasses__():
            self.scopes.extend(child.scopes)


class Service:
    scopes = []

    def __init__(self, auth):
        self.auth: Auth = auth


class Drive(Service):
    scopes = [
        "https://www.googleapis.com/auth/drive.file"
    ]
    mime_types = {
        'folder': 'application/vnd.google-apps.folder',
        'upload': 'application/vnd.google-apps.file',
    }

    def __init__(self, auth):
        super().__init__(auth)
        self.service = build('drive', 'v3', credentials=self.auth.creds)

    def create_folder(self, name):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        response = self.service.files().create(body=file_metadata).execute()
        return response

    def delete_file(self):
        pass

    def get_file(self, id):
        return self.service.file(id).execute().get('file')

    def search_files(self, name=None, type=None, files_only=True):
        query = "trashed = false "
        if name is not None:
            query += f"and name='{name}' "
        if type is not None:
            query += f"and mimeType='{self.mime_types[type]}'"
        response = self.service.files().list(q=query, spaces='drive').execute()

        if files_only:
            return response.get('files')
        return response

    def upload_file(self, local_path, name, parent_folders: List[str]):
        """Uploads a file.
        parent_folders: list of folder ids"""
        file_metadata = {
            'name': name,
            'parents': parent_folders
        }

        
        media = MediaFileUpload(local_path,
                                mimetype=mimetypes.guess_type(local_path)[0],
                                resumable=True)
        file = self.service.files().create(body=file_metadata,
                                           media_body=media,
                                           fields='id').execute()
        return file


class Classroom(Service):
    scopes = [
        'https://www.googleapis.com/auth/classroom.coursework.me',
        'https://www.googleapis.com/auth/classroom.courses.readonly'
    ]

    def __init__(self, auth):
        super().__init__(auth)
        self.service = build('classroom', 'v1', credentials=self.auth.creds)

    def get_course(self, course_abbrv):
        courses = self.service.courses().list(
            courseStates='ACTIVE').execute().get('courses', [])
        course = utils.filter_get(
            'name', settings.CLASSES[course_abbrv], courses)
        if not courses:
            print('No courses found.')
        else:
            return course

    def match_assignment(self, course, name):
        assignments = self.service.courses().courseWork().list(
            courseId=course['id'], pageSize=3).execute().get('courseWork')

        index_max = 0
        scores = []
        for index, a in enumerate(assignments):
            result = fuzz.partial_token_set_ratio(name, a['title'])
            scores.append(result)

            if result > scores[index_max]:
                index_max = index

        if scores[index_max] >= settings.TITLE_MATCH_THRESH:
            return assignments[index_max]
