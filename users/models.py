from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from main.models import Batch, Department
from main.funcs import d_t


class CustomizedUser(AbstractUser):
    email = models.EmailField(unique=True, null=False)
    gender = models.CharField(max_length=6)

    def __str__(self):
        username = "Administrator" if self.is_superuser else self.username
        return f"{username} [ {self.email} ]"

    @property
    def role(self):
        if self.is_superuser:
            return 'superuser'
        elif Student.objects.filter(user=self).count() != 0:
            return 'student'
        elif Lecturer.objects.filter(user=self).count() != 0:
            return 'lecturer'

    @property
    def is_lecturer(self):
        if self.role == 'lecturer':
            return True
        return False

    @property
    def is_student(self):
        if self.role == 'student':
            return True
        return False

    @property
    def profile(self):
        """
        Return the related profile for the user.
        Profile can only be <Student> or <Lecturer> instance.
        :return:
        """
        profile = None
        if self.role == 'student':
            profile = Student.objects.get(user=self)
        elif self.role == 'lecturer':
            profile = Lecturer.objects.get(user=self)
        else:
            # This should never happen
            print("Undetected Role")
        return profile


class Student(models.Model):
    user = models.OneToOneField(CustomizedUser, on_delete=models.CASCADE, related_name='student')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    profile_pic = models.ImageField(null=True, upload_to="stu_profile_pics")
    id_pic = models.ImageField(null=True, upload_to="stu_id_pics")

    def __str__(self):
        return f"Student: {self.user.username} [{self.department.name}]"

    """
    =============================
    ASSIGNMENTS
    =============================
    """

    def __get_all_not_completed_assignments(self) -> set:
        """
        Returns all the not done assignments including,
        both pending and missing assignments
        :return:
        """
        _all_ass = self.__get_all_assignments()
        _all_sub = set(ass for ass in self.get_all_completed_assignments())
        not_done = set(ass for ass in _all_ass if ass not in _all_sub)
        return not_done

    def get_pending_assignments(self) -> set:
        """
        Returns all the assignments that due date is not exceeded.
        :return:
        """
        not_complete = self.__get_all_not_completed_assignments()
        now = datetime.now()
        pending = set(ass for ass in not_complete if d_t(ass.date_due) > d_t(now))
        return pending

    def get_no_of_pending_assignments(self):
        return len(self.get_pending_assignments())

    def get_all_completed_assignments(self):
        """
        Get all the assignment submissions done by the student
        for all the available classes.
        Note that this returns <Submission> queryset
        :return:
        """
        submissions = [sub.assignment for sub in self.submission_set.all()]
        return submissions

    def get_missing_assignments(self) -> set:
        """
        Returns all the assignments that didn't completed and also
        due date is exceeded.
        :return:
        """
        not_complete = self.__get_all_not_completed_assignments()
        now = datetime.now()
        missing = set(ass for ass in not_complete if d_t(ass.date_due) < d_t(now))
        return missing

    def get_no_of_missing_assignmets(self):
        return len(self.get_missing_assignments())

    def __get_all_assignments(self):
        """
        Returns all the assignments from all the classrooms
        available for the student.
        :return:
        """
        classes = self.get_classrooms()
        assignments = set()

        for cls in classes:
            _all_ass = [ass for ass in cls.assignment_set.all()]
            for ass in _all_ass:
                assignments.add(ass)
        return assignments

    """
    =============================
    CLASSROOMS
    =============================
    """

    def get_classrooms(self):
        """
        Returns all the assignments in the students department.
        :return:
        """
        classes = self.department.classroom_set.all()
        return classes

    def get_no_of_classes(self) -> int:
        return self.get_classrooms().count()

    """
    =============================
    MEETINGS
    =============================
    """

    def get_today_meetings(self):
        pass

    def get_upcoming_meetings(self):
        pass

    def get_recent_events(self):
        pass


class Lecturer(models.Model):
    user = models.OneToOneField(CustomizedUser, on_delete=models.CASCADE, related_name='lecturer')
    departments = models.ManyToManyField(Department, blank=True)
    profile_pic = models.ImageField(null=True, upload_to="lec_profile_pics")

    def __str__(self):
        return f"Lecturer: {self.user.username}"

    """
    =============================
    CLASSROOMS
    =============================
    """

    def get_classrooms(self):
        """
        Get all the classrooms enrolled by lecturer.
        Both created and assigned classrooms will be counted.
        :return:
        """
        classes = self.classroom_set.all()
        return classes

    def get_no_of_classes(self) -> int:
        """
        Get the no of classes. Just calls the <get_classrooms>
        method and get the queryset count.
        :return:
        """
        return self.get_classrooms().count()

    """
    =============================
    ASSIGNMETS
    =============================
    """

    def get_all_assignments(self):
        """All the assignments that ever created """
        assignments = self.assignment_set.all()
        return assignments

    def get_no_of_all_assignments(self):
        """
        Get all the assignments as a count
        :return:
        """
        return self.get_all_assignments().count()

    def get_ongoing_assignments(self):
        """
        Get all the assignments that due date has not exceeded.
        :return:
        """
        _all = self.get_all_assignments()
        ongoing = _all.filter(date_due__gte=d_t(datetime.now()))
        return ongoing

    def get_no_of_ongoing_assignments(self):
        return self.get_ongoing_assignments().count()

    def get_pending_review_assignments(self):
        """
        Returns all the assignments that due date is
        exceeded and not review completed. This s detected
        by using <Assignment> model's boolean attribute 'review_complete'.
        :return:
        """
        _all = self.get_all_assignments()
        pending_review = set(ass for ass in _all
                             if not ass.review_complete
                             and d_t(ass.date_due) < d_t(datetime.now()))
        return pending_review

    def get_reviewed_assignments(self):
        """
        Returns all the review completed assignments
        :return:
        """
        reviewed = set(ass for ass in self.get_all_assignments() if ass.review_complete)
        return reviewed

    def get_recent_activities(self):
        pass


