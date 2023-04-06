from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from typing import Union
from .models import Lecturer, Student


@receiver(post_delete, sender=Lecturer)
@receiver(post_delete, sender=Student)
def delete_user(sender, instance, **kwargs):
    """
    If Lecturer or Student profile is deleted somehow,
    delete the associated <User> instance to particular profile
    """
    if isinstance(instance, Lecturer) or \
            isinstance(instance, Student):
        try:
            instance.user.delete()
            print(f"Deleted <User> instance for {instance}")
        except Exception as e:
            print(f"Error when deleting Lecturer's <User> instance: {e}")


