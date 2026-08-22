from app.models.academic_profile import AcademicProfile
from app.models.application import Application
from app.models.base import Base
from app.models.document import Document
from app.models.notification import Notification
from app.models.profile import Profile
from app.models.saved_scholarship import SavedScholarship
from app.models.scholarship import Scholarship
from app.models.user_settings import UserSettings

__all__ = [
    "AcademicProfile", "Application", "Base", "Document", "Notification",
    "Profile", "SavedScholarship", "Scholarship", "UserSettings",
]
