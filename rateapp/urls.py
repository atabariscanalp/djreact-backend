"""rateapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from dj_rest_auth.views import (LoginView, LogoutView, PasswordChangeView,
                                PasswordResetConfirmView, PasswordResetView,
                                UserDetailsView)
from dj_rest_auth.registration.views import (RegisterView, VerifyEmailView)

from api.views import UserLoginAPIView, GetUserAPIView, UserRegisterAPIView

from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    # path('auth/', include('dj_rest_auth.urls')),
    path('auth/register/', include('dj_rest_auth.registration.urls')),
    path('accounts/', include('allauth.urls')),

    # URLs that do not require a session or valid token
    path('auth/password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('auth/password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),
    path('auth/login/', UserLoginAPIView.as_view(), name='rest_login'),
    path('auth/register/', UserRegisterAPIView.as_view(), name='rest_register'),
    
    path('', include('django.contrib.auth.urls')),
    # URLs that require a user to be logged in with a valid session / token.
    path('auth/register/verify-email/', VerifyEmailView.as_view(), name='rest_verify_email'),
    path('auth/logout/', LogoutView.as_view(), name='rest_logout'),
    path('auth/user/', UserDetailsView.as_view(), name='rest_user_details'),
    path('auth/password/change/', PasswordChangeView.as_view(), name='rest_password_change'),
    path('add/device/', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='add_fcm_device')
]

#if settings.DEBUG:
 #   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
