from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    """
    Create or update UserProfile for User
    """
    if created:
        # Create UserProfile for new users
        UserProfile.objects.create(user=instance)
    else:
        # For existing users, get or create UserProfile
        UserProfile.objects.get_or_create(user=instance)