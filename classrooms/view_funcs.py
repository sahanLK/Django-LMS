"""
Common helpful functions for views.py
"""
from .models import Classroom, Assignment, Post
from users.models import Profile  # No error because similar to django Shell import
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from typing import Union
from .exceptions import ArgumentNotSpecifiedError


def get_user_profile(user: User) -> Profile:
    """
    Returns the user profile, using any user instance
    :param user:
    :return:
    """
    profile = Profile.objects.get(user=user)
    return profile


def get_class(class_pk) -> Classroom:
    cls = Classroom.objects.get(pk=class_pk)
    return cls


def get_stu_profiles(class_pk) -> QuerySet:
    owner_dept = get_class(class_pk).owner.profile.department
    students = Profile.objects.filter(department=owner_dept, role='Student')
    return students


def get_lec_profiles(class_pk: str) -> list:
    """
    Get the lecturer for a particular class
    :param class_pk: Primary key of the class
    :return:
    """
    cls_owner = get_class(class_pk).owner
    prof = Profile.objects.get(user=cls_owner)
    return [prof]


def get_assignments_all(user):
    my_prof = get_user_profile(user)
    pending = set()
    for assign in Assignment.objects.all():
        # Get assignment owner profile
        owner_prof = get_user_profile(assign.owner)
        if owner_prof.department == my_prof.department:
            pending.add(assign)
    return pending
