from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from accounts.models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def user_created_signal(sender, instance, created, **kwargs):
    print(f"Profile will created for user: {instance.username}")
    if created:
        Profile.objects.create(user=instance)
