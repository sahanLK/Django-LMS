import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Submission


@receiver(post_delete, sender=Submission)
def submission_deleted(sender, instance, **kwargs):
    """
    Delete the file from the filesystem when particular submission object gets deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            try:
                os.remove(instance.file.path)
            except Exception as e:
                print(f"Error when deleting submission file: {e}")
