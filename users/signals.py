# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        from .models import Profile   # 👈 import inside function to avoid circular import
        Profile.objects.get_or_create(user=instance)
