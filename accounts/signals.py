from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from versatileimagefield.image_warmer import VersatileImageFieldWarmer

from accounts.models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def user_created_signal(sender, instance, created, **kwargs):
    print(f"Profile will created for user: {instance.username}")
    if created:
        Profile.objects.create(user=instance)


# @receiver(post_save, sender=Profile)
# def warm_Person_headshot_images(sender, instance, **kwargs):
#     if instance.avatar:
#         person_img_warmer = VersatileImageFieldWarmer(
#             instance_or_queryset=instance,
#             rendition_key_set="avatar",
#             image_attr="avatar",
#         )
#         num_created, failed_to_create = person_img_warmer.warm()
