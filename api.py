import os

from fuzzywuzzy import fuzz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import settings
import utils


class Auth:
    scopes = [] # If modifying these scopes, delete the file token.json.

    def __init__(self):
        self.register_scopes()
        self.creds = None
        self.authenticate()

    def authenticate(self):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.scopes)
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

    ]
    def __init__(self, auth):
        super().__init__(auth)
        self.service = build('drive', 'v3', credentials=self.auth.creds)

    def create_folder(self, name, path):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = self.service.files().create(body=file_metadata).execute()
        return file

    def uploade_file(self, filepath):
        pass
        

class Classroom(Service):
    scopes = [
        'https://www.googleapis.com/auth/classroom.coursework.me',
        'https://www.googleapis.com/auth/classroom.courses.readonly'
    ]

    def __init__(self, auth):
        super().__init__(auth)
        self.service = build('classroom', 'v1', credentials=self.auth.creds)

    def get_course(self, course_abbrv):
        courses = self.service.courses().list(courseStates='ACTIVE').execute().get('courses', [])
        course = utils.filter_get('name', settings.CLASSES[course_abbrv], courses)
        if not courses:
            print('No courses found.')
        else:
            return course
    
    def match_assignment(self, course, name):
        assignments = self.service.courses().courseWork().list(courseId=course['id'], pageSize=3).execute().get('courseWork')

        index_max = 0
        scores = []
        for index, a in enumerate(assignments):
            result = fuzz.partial_token_set_ratio(name, a['title'])
            scores.append(result)

            if result > scores[index_max]:
                index_max = index

        if scores[index_max] >= settings.TITLE_MATCH_THRESH:
            return assignments[index_max]
