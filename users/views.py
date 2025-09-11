# users/views.py
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth import authenticate, get_user_model

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import OTP, Profile

import random

User = get_user_model()

# ───────────────────────────────────────────────────────────────────────────────
# JWT: add extra claims if you want
# ───────────────────────────────────────────────────────────────────────────────
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# ───────────────────────────────────────────────────────────────────────────────
# OTP SIGNUP FLOW (pure API)
# 1) /users/api/send-otp/     -> POST { email }
# 2) /users/api/verify-otp/   -> POST { otp }
# 3) /users/api/set-password/ -> POST { password } -> returns JWT
# 4) /users/api/password/forgot/ -> POST { PASSWORD REST VIA OTP }
# 5) /users/api/password/verify-otp/ -> POST {User verifies OTP}
# 6) /users/api/password/reset/ -> POST  {User sets a new password}
# ───────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def api_send_otp(request):
    """
    Body: { "email": "user@example.com" }
    Stores the email in the session for the next steps.
    """
    email = (request.data.get('email') or '').strip().lower()
    if not email:
        return Response({"error": "Email is required"}, status=400)

    # generate & save OTP
    otp_code = str(random.randint(100000, 999999))
    OTP.objects.create(email=email, otp=otp_code)

    # keep state in session for next steps
    request.session['otp_email'] = email
    request.session.pop('otp_verified', None)

    # DEV: print to console; PROD: configure SMTP
    if getattr(settings, 'EMAIL_BACKEND', '') == 'django.core.mail.backends.console.EmailBackend':
        print(f"[DEV OTP] {email} -> {otp_code}")

    # send email (will print to console if console backend)
    send_mail(
        subject='Your NOVA OTP Code',
        message=f'Your OTP is: {otp_code}',
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
        recipient_list=[email],
        fail_silently=True,
    )

    return Response({"message": "OTP sent to email"}, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_verify_otp(request):
    """
    Body: { "otp": "123456" }
    Uses session['otp_email'] from previous step.
    """
    email = request.session.get('otp_email')
    if not email:
        return Response({"error": "Session expired. Please restart signup."}, status=403)

    input_otp = (request.data.get('otp') or '').strip()
    if not input_otp:
        return Response({"error": "OTP is required"}, status=400)

    try:
        otp_obj = OTP.objects.filter(email=email).latest('created_at')
    except OTP.DoesNotExist:
        return Response({"error": "OTP not found. Please request a new one."}, status=404)

    # expiry: 10 minutes
    if timezone.now() > otp_obj.created_at + timezone.timedelta(minutes=10):
        return Response({"error": "OTP expired. Please request a new one."}, status=400)

    if otp_obj.otp != input_otp:
        return Response({"error": "Invalid OTP"}, status=400)

    request.session['otp_verified'] = True
    return Response({"message": "OTP verified. You can set your password now."}, status=200)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_set_password(request):
    """
    Body: { "password": "strongpass" }
    Requires session['otp_verified'] and session['otp_email'].
    Returns: access_token, refresh_token
    """
    if not request.session.get('otp_verified'):
        return Response({"error": "Access denied. Verify OTP first."}, status=403)

    email = request.session.get('otp_email')
    if not email:
        return Response({"error": "Session expired. Please restart signup."}, status=403)

    password = request.data.get('password')
    if not password:
        return Response({"error": "Password is required"}, status=400)

    # ✅ Create user and profile together
    user, created = User.objects.get_or_create(email=email, defaults={"username": email})
    user.set_password(password)
    user.save()

    # ✅ **FIX: Create Profile if it doesn't exist**
    from .models import Profile  # Make sure to import Profile
    Profile.objects.get_or_create(user=user, defaults={
        'nickname': user.username or user.email.split('@')[0],
        # Add other default fields if needed
    })

    # Clear session state and old OTPs for that email
    request.session.pop('otp_verified', None)
    request.session.pop('otp_email', None)
    OTP.objects.filter(email=email).delete()

    refresh = RefreshToken.for_user(user)
    return Response({
        "message": "Signup complete",
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh)
    }, status=200)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import PasswordResetSession
import random

User = get_user_model()

# Dummy OTP storage (replace with Redis/DB in production)
OTP_STORE = {}

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_to_email(email, otp):
    # 🔥 Replace with real email service
    print(f"[DEBUG] Sending OTP {otp} to {email}")

class RequestOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        otp = generate_otp()
        OTP_STORE[email] = otp
        send_otp_to_email(email, otp)

        # Create/reset session
        session, _ = PasswordResetSession.objects.get_or_create(user=user)
        session.is_verified = False
        session.save()

        return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if OTP_STORE.get(email) != otp:
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        session, _ = PasswordResetSession.objects.get_or_create(user=user)
        session.is_verified = True
        session.save()

        return Response({
            "message": "OTP verified successfully",
            "session_token": str(session.session_token)
        }, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")
        session_token = request.data.get("session_token")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            session = PasswordResetSession.objects.get(user=user, session_token=session_token)
        except PasswordResetSession.DoesNotExist:
            return Response({"error": "Invalid session"}, status=status.HTTP_400_BAD_REQUEST)

        if not session.is_verified:
            return Response({"error": "OTP not verified"}, status=status.HTTP_403_FORBIDDEN)

        # ✅ Reset password
        user.set_password(new_password)
        user.save()

        # Destroy session after successful reset
        session.delete()
        if email in OTP_STORE:
            del OTP_STORE[email]

        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)


# ───────────────────────────────────────────────────────────────────────────────
# OPTIONAL: plain signup (no OTP) — keep only if you still call it
# ───────────────────────────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def signup_api(request):
    """
    Classic signup (email+password) WITHOUT OTP.
    """
    email = (request.data.get('email') or '').strip().lower()
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email and password required'}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'User with this email already exists'}, status=400)

    user = User.objects.create_user(username=email, email=email)
    user.set_password(password)
    user.save()

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }, status=201)


# ───────────────────────────────────────────────────────────────────────────────
# LOGIN (JWT)
# ───────────────────────────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Body: { "email": "...", "password": "..." }
    """
    email = (request.data.get("email") or "").strip().lower()
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email and password are required"}, status=400)

    # With custom user (USERNAME_FIELD=email), pass username=email to authenticate
    user = authenticate(request, username=email, password=password)
    if user is None:
        return Response({"error": "Invalid email or password"}, status=401)

    refresh = RefreshToken.for_user(user)
    return Response({
        "message": "Login successful",
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh)
    }, status=200)

# ───────────────────────────────────────────────────────────────────────────────
# LOGOUT API KILL JWT SESSION
# ───────────────────────────────────────────────────────────────────────────────
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    # Optional: blacklist the refresh token if using SimpleJWT blacklist
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            from rest_framework_simplejwt.tokens import RefreshToken
            token = RefreshToken(refresh_token)
            token.blacklist()
    except Exception:
        pass

    return JsonResponse({"message": "Logged out successfully"}, status=200)


# ───────────────────────────────────────────────────────────────────────────────
# PROFILE API (JWT-protected example)
# ───────────────────────────────────────────────────────────────────────────────
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def profile_api(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'GET':
        from .serializers import ProfileSerializer
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    if request.method == 'PUT':
        from .serializers import ProfileSerializer
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


# ───────────────────────────────────────────────────────────────────────────────
# Helper: mint a new token for current user (needs session or JWT auth)
# ───────────────────────────────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_token(request):
    refresh = RefreshToken.for_user(request.user)
    return Response({
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh)
    })


# ───────────────────────────────────────────────────────────────────────────────
# (Optional) Simple template pages that POST to the APIs via JavaScript.
# You can remove these if you go full API + SPA/mobile only.
# ───────────────────────────────────────────────────────────────────────────────
def signup_page(request):        return render(request, 'users/signup.html')
def login_page(request):         return render(request, 'users/login.html')
def feed_page(request):          return render(request, 'users/feed.html')
def forgot_password_page(request):
    return render(request, "users/forgot_password.html")




# from django.shortcuts import render

def complete_otp_page(request):
    return render(request, 'users/complete_otp.html')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model

User = get_user_model()

from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model

User = get_user_model()
from products.models import Profile

def update_password_page(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password and password == confirm_password:
            user = request.user
            user.set_password(password)
            user.save()

            # Ensure profile exists (safety net)
            Profile.objects.get_or_create(user=user)

            update_session_auth_hash(request, user)
            return redirect('login_page')

        return render(request, 'users/update_password.html', {
            'error': 'Passwords do not match!'
        })

    return render(request, 'users/update_password.html')

    
    # GET request - show the form
    return render(request, 'users/update_password.html')






## profile managment api endpoints

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Profile
from .serializers import (
    ProfileSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer,
)


class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

    def put(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # check if any valid field is present
        if not serializer.validated_data:
            return Response(
                {"error": "No valid fields provided"},
                status=400
            )

        serializer.save()
        return Response({"message": "Profile updated"})



class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password updated"})
    
    # retrive other user info by id number 
from rest_framework import generics, permissions
from .models import Profile
from .serializers import ProfileSerializer


class PublicProfileView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]  # only logged in users can view
    lookup_field = "id"  # this makes /api/profile/<id>/ work