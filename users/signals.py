from django.db.models.signals import post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


@receiver(post_delete, sender=Profile)
def profile_deleted(sender, instance, **kwargs):
    instance.user.delete()
