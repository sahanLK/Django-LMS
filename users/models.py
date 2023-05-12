
from datetime import datetime
from PIL import Image
from PIL import UnidentifiedImageError
from django.db import models
from django.contrib.auth.models import AbstractUser
from main.models import Batch, Department
from main.funcs import (utc_to_local_naive,
                        utc_to_local_aware,
                        local_to_utc_naive,
                        local_to_utc_aware,
                        get_naive_dt)


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
    id_pic = models.ImageField(null=True, blank=True, upload_to="stu_id_pics")

    def __str__(self):
        return f"Student: {self.user.username} [{self.department.name}]"

    def save(self,
             force_insert=False,
             force_update=False,
             using=None,
             update_fields=None):
        super().save()

        images = [self.profile_pic, self.id_pic]

        output_size = (250, 250)
        for img in images:
            try:
                im = Image.open(img.path)

                if im.height > 250 or im.width > 250:
                    im.thumbnail(output_size)
                    im.save(img.path)
            except ValueError:  # No file associated
                continue
            except UnidentifiedImageError:
                print("Unidentified Image. Probably someone is trying to sign in with svg")
                continue

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
        pending = set(ass for ass in not_complete if ass.date_due > now)
        return pending

    def get_no_of_pending_assignments(self):
        return len(self.get_pending_assignments())

    def today_assignments(self):
        today = set()
        for a in self.get_pending_assignments():
            if a.date_due.date() == datetime.today().date():
                today.add(a)
        return today

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
        missing = set(ass for ass in not_complete if ass.date_due < now)
        return missing

    def get_no_of_missing_assignments(self):
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

    def get_all_meetings(self):
        """
        Returns all the meetings ever for the student.
        :return:
        """
        classes = self.get_classrooms()
        _all = set()

        for cls in classes:
            meets = cls.meeting_set.all()
            for meet in meets:
                _all.add(meet)
        return _all

    def get_today_meetings(self):
        """
        Get all the today meetings.
        :return:
        """
        _all = self.get_all_meetings()
        today = set()

        for meet in _all:
            if meet.is_today:
                today.add(meet)
        return today

    def get_no_of_today_meetings(self):
        return len(self.get_today_meetings())

    def get_upcoming_meetings(self):
        """
        Get all the upcoming meetings except today
        :return:
        """
        _all = self.get_all_meetings()
        upcoming = set()

        for meet in _all:
            if meet.start.date() > datetime.now().date():
                upcoming.add(meet)
        return upcoming

    def get_prev_meetings(self):
        _all = self.get_all_meetings()
        prev = set()

        for meet in _all:
            if meet.is_expired:
                prev.add(meet)
        return prev

    """
    =============================
    QUIZZES
    =============================
    """

    def _get_all_quizzes(self):
        """
        Returns all the quizzes from all the classrooms
        available for the student.
        :return:
        """
        classes = self.get_classrooms()
        quizzes = set()

        for cls in classes:
            _all_ass = [q for q in cls.quiz_set.all()]
            for ass in _all_ass:
                quizzes.add(ass)
        return quizzes

    def get_today_quizzes(self):
        today = set()

        for q in self._get_all_quizzes():
            if q.start.date() == datetime.today().date():
                today.add(q)
        return today

    def get_no_of_today_quizzes(self):
        return len(self.get_today_quizzes())

    def get_upcoming_quizzes(self):
        upcoming = set()

        for q in self._get_all_quizzes():
            if q.start.date() > datetime.today().date():
                upcoming.add(q)
        return upcoming

    def expired_quizzes(self):
        expired = set()
        for q in self._get_all_quizzes():
            if q.expired:
                expired.add(q)
        return expired

    def get_missing_quizzes(self):
        missing = set()
        for q in self.expired_quizzes():
            # check if a response has been made for the quiz or not
            from classrooms.models import QuizStudentResponse
            response = QuizStudentResponse.objects.filter(
                quiz=q,
                owner=self).first()
            if not response:
                missing.add(q)
        return missing

    def get_completed_quizzes(self):
        done = set()
        for q in self.expired_quizzes():
            # check if a response has been made for the quiz or not
            from classrooms.models import QuizStudentResponse
            response = QuizStudentResponse.objects.filter(
                quiz=q,
                owner=self).first()
            if response:
                done.add(q)
        return done

    """
    =============================
    OTHER
    =============================
    """

    def today_events(self):
        """
        Get a list of most recent events for a student
        """
        events = set()
        events.update(self.today_assignments())
        events.update(self.get_today_meetings())
        events.update(self.get_today_quizzes())
        return list(events)

    def this_month_assignments(self):
        """
        Current month's assignments are taken based on the
        due_date instead of created data
        """
        today = datetime.today().date()
        assignments = set()
        for ass in self.__get_all_assignments():
            if ass.date_due.date().year == today.year \
                    and ass.date_due.date().month == today.month:
                assignments.add(ass)
        return assignments

    def this_month_quizzes(self):
        """
        Current month's quizzes are taken based on the
        start date instead of created data
        """
        today = datetime.today().date()
        quizzes = set()
        for quiz in self._get_all_quizzes():
            if quiz.start.date().year == today.year \
                    and quiz.start.date().month == today.month:
                quizzes.add(quiz)
        return quizzes

    def this_month_meetings(self):
        """
        Current month's assignments are taken based on the
        start date instead of created data
        """
        today = datetime.today().date()
        meetings = set()
        for meet in self.get_all_meetings():
            if meet.start.date().year == today.year \
                    and meet.start.date().month == today.month:
                meetings.add(meet)
        return meetings


class Lecturer(models.Model):
    user = models.OneToOneField(CustomizedUser, on_delete=models.CASCADE, related_name='lecturer')
    departments = models.ManyToManyField(Department, blank=True)
    profile_pic = models.ImageField(null=True, blank=True, upload_to="lec_profile_pics")

    def __str__(self):
        return f"Lecturer: {self.user.username}"

    def save(self,
             force_insert=False,
             force_update=False,
             using=None,
             update_fields=None):
        super().save()

        output_size = (250, 250)
        try:
            img = Image.open(self.profile_pic.path)
            if img.height > 250 or img.width > 250:
                img.thumbnail(output_size)
                img.save(self.profile_pic.path)
        except ValueError:  # No file associated
            pass
        except UnidentifiedImageError:
            print("Unidentified Image. Probably someone is trying to sign in with svg")

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
    ASSIGNMENTS
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
        ongoing = set()
        for a in self.get_all_assignments():
            if a.date_due >= datetime.now() \
                    and not a.review_complete:
                ongoing.add(a)
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
                             and ass.date_due < datetime.now())
        return pending_review

    def get_no_of_pending_review_assignments(self):
        return len(self.get_pending_review_assignments())

    def get_reviewed_assignments(self):
        """
        Returns all the review completed assignments
        :return:
        """
        return set(ass for ass in self.get_all_assignments() if ass.review_complete)

    def get_recent_activities(self):
        pass

    """
    =============================
    MEETINGS
    =============================
    """

    def get_all_meetings(self):
        """
        Returns all the meetings ever for the student.
        :return:
        """
        return self.meeting_set.all()

    def get_today_meetings(self):
        """
        Get all the today meetings.
        :return:
        """
        _all = self.get_all_meetings()
        today = set()

        for meet in _all:
            if meet.is_today:
                today.add(meet)
        return today

    def get_no_of_today_meetings(self):
        return len(self.get_today_meetings())

    def get_upcoming_meetings(self):
        """
        Get all the upcoming meetings except today
        :return:
        """
        _all = self.get_all_meetings()
        upcoming = set()

        for meet in _all:
            if meet.start.date() > datetime.today().date():
                upcoming.add(meet)
        return upcoming

    def get_prev_meetings(self):
        _all = self.get_all_meetings()
        prev = set()

        for meet in _all:
            if meet.start.date() < datetime.today().date():
                prev.add(meet)
        return prev

    """
    =============================
    QUIZZES
    =============================
    """

    def _get_all_quizzes(self):
        quizzes = self.quiz_set.all()
        return quizzes

    def get_today_quizzes(self):
        today = set()

        for q in self._get_all_quizzes():
            if q.start.date() == datetime.today().date():
                today.add(q)
        return today

    def get_no_of_today_quizzes(self):
        return len(self.get_today_quizzes())

    def get_upcoming_quizzes(self):
        upcoming = set()

        for q in self._get_all_quizzes():
            if q.start.date() > datetime.today().date():
                upcoming.add(q)
        return upcoming

    def get_previous_quizzes(self):
        done = set()
        for q in self._get_all_quizzes():
            if q.expired:
                done.add(q)
        return done

    """
    =============================
    OTHER
    =============================
    """

    def today_events(self):
        """
        Get a list of most recent events for a lecturer
        """
        events = set()
        events.update(self.get_today_meetings())
        events.update(self.get_today_quizzes())
        return list(events)

    def this_month_assignments(self):
        today = datetime.today().date()
        return self.assignment_set.filter(
            _date_due__year=today.year,
            _date_due__month=today.month,
        )

    def this_month_quizzes(self):
        """
        Current month's quizzes are taken based on the
        start date instead of created data
        """
        today = datetime.today().date()
        return self.quiz_set.filter(
            _start__year=today.year,
            _start__month=today.month,)

    def this_month_meetings(self):
        """
        Current month's assignments are taken based on the
        start date instead of created data
        """
        today = datetime.today().date()
        return self.meeting_set.filter(
            _start__year=today.year,
            _start__month=today.month,)
