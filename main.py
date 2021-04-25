import os
import settings

from api import Auth, Classroom, Drive


def test_classroom(auth):
    gclass = Classroom(auth)
    course = gclass.get_course("Physics")
    latest_assignment = gclass.match_assignment(course, "Progress Check")

def test_g_drive(auth):
    gdrive = Drive(auth)
    folders = gdrive.search_files(settings.DRIVE_FOLDER_NAME, type="folder", files_only=True)
    if not folders:
        response = gdrive.create_folder(settings.DRIVE_FOLDER_NAME)
    gdrive.upload_file('test.pdf', 'test.pdf', [folders[0]['id']])


if __name__ == "__main__":
    auth = Auth()
    test_g_drive(auth)


