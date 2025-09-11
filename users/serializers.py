# users/serializers.py
from rest_framework import serializers
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

# Profile serializer (for viewing)
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "nickname", "profile_picture"]


# Profile update serializer (for editing nickname, profile picture, etc.)
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["nickname", "profile_picture"]


# Change password serializer
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_new_password(self, value):
        validate_password(value)  # uses Django’s built-in password validators
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        old_password = self.validated_data["old_password"]
        new_password = self.validated_data["new_password"]

        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Wrong password"})

        user.set_password(new_password)
        user.save()
        return user
