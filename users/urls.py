# users/urls.py
from . import views
from django.urls import path
from django.urls import path

from django.urls import path
from .views import RequestOTPView, VerifyOTPView, ResetPasswordView

from .views import signup_page, login_page, forgot_password_page

from django.urls import path
from .views import (
    ProfileView,
    ProfileUpdateView,
    ChangePasswordView,
)

from django.urls import path
from .views import PublicProfileView
from .views import update_password_page   
from django.urls import path
from .views import complete_otp_page, update_password_page

from .views import logout_api
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    # JWT
    MyTokenObtainPairView,

    # OTP signup flow (APIs)
    api_send_otp, api_verify_otp, api_set_password,

    # Optional classic signup (no OTP)
    signup_api,

    # Login API
    login_view,

    # Helper
    get_my_token,

    # Profile API
    profile_api,

    # Simple HTML pages (optional)
    signup_page, login_page, feed_page,
)

urlpatterns = [
    # ============================================================================
    # HTML PAGES (Frontend Routes)
    # ============================================================================
    path('signup/', signup_page, name='signup_page'),
    path('login/', login_page, name='login_page'),              # ← Fixed: matches template usage
    path('feed/', feed_page, name='feed_page'),
    path('forgot-password/', forgot_password_page, name='forgot_password'),
    path('complete-otp/', complete_otp_page, name='complete_otp_page'),
    path('update-password/', update_password_page, name='update_password_page'),
    
    # ============================================================================
    # API ENDPOINTS - Authentication & JWT
    # ============================================================================
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # OTP Signup Flow
    path('api/send-otp/', api_send_otp, name='api_send_otp'),
    path('api/verify-otp/', api_verify_otp, name='api_verify_otp'),
    path('api/set-password/', api_set_password, name='api_set_password'),
    
    # Authentication
    path('api/signup/', signup_api, name='api_signup'),          # Classic signup (no OTP)
    path('api/login/', login_view, name='api_login'),
    path('api/logout/', logout_api, name='api_logout'),
    path('api/get-my-token/', get_my_token, name='get_my_token'),
    
    # ============================================================================
    # API ENDPOINTS - Profile Management
    # ============================================================================
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('api/profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('api/profile/<int:id>/', PublicProfileView.as_view(), name='public_profile'),
    
    # ============================================================================
    # API ENDPOINTS - Password Reset
    # ============================================================================
    path('api/password/request-otp/', RequestOTPView.as_view(), name='request_password_otp'),
    path('api/password/verify-otp/', VerifyOTPView.as_view(), name='verify_password_otp'),
    path('api/password/reset/', ResetPasswordView.as_view(), name='reset_password'),
]
