import os
import settings

from api import Auth, Classroom, Drive


if __name__ == "__main__":
    auth = Auth()
    gclass = Classroom(auth)
    course = gclass.get_course("Physics")
    latest_assignment = gclass.match_assignment(course, "Progress Check")
    print(latest_assignment)