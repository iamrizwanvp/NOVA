from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', required=False)

    class Meta:
        model = Profile
        fields = ['email', 'username', 'profile_picture', 'address', 'state', 'country', 'pincode']

    def update(self, instance, validated_data):
        # Update related User fields
        user_data = validated_data.pop('user', {})
        if 'username' in user_data:
            instance.user.username = user_data['username']
            instance.user.save()

        # Update Profile fields
        return super().update(instance, validated_data)


# users/serializers.py

from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ["nickname", "email", "profile_pic"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["nickname", "profile_pic"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not check_password(value, user.password):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return user
