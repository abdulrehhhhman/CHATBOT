from .user import User
from .chat import Chat
from .course import Course, CourseEnrollment, CourseMaterial

# This makes imports easier in other files
__all__ = [
    "User", 
    "Chat", 
    "Course", 
    "CourseEnrollment", 
    "CourseMaterial"
]