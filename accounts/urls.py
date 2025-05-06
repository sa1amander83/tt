from django.urls import path
from accounts import views

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("signin/", views.SignInView.as_view(), name="signin"),
    path("logout/", views.logout_view, name="logout"),
    path("restore/", views.restore_view, name="restore"),

]
