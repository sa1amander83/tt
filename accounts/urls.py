from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from accounts.views import *

app_name = "accounts"
urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("signin/", SignInView.as_view(), name="signin"),
    path("logout/", logout_view, name="logout"),
    path("restore/", restore_view, name="restore"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update", ProfileUpdateView.as_view(), name="profile-update"),
    path('upload-photo/', upload_profile_photo, name='upload-profile-photo'),
    path('update-slot-view-mode/', update_slot_view_mode, name='update_slot_view_mode')
]
