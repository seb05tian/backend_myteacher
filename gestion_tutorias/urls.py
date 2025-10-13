from django.urls import path
from dj_rest_auth.views import LoginView, RegisterView, MeView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('/login',LoginView.as_view(), name='login'),
    path('/register', RegisterView.as_view(), name='register'),
    path('/me', MeView.as_view(), name='me'),
]