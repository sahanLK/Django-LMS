import os.path
from datetime import datetime
from django.db import models
from django.urls import reverse
from users.models import CustomizedUser, Student, Lecturer
from main.models import Batch, Department
from main.funcs import d_t


class Classroom(models.Model):
    owner = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='owner')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    lecturers = models.ManyToManyField(Lecturer)
    name = models.CharField(max_length=300)
    description = models.TextField(max_length=150, null=True,  blank=True)
    background_img = models.ImageField(null=True, blank=True)

    class Meta:
        unique_together = (('department', 'name'),)

    def __str__(self):
        return f"Class: {self.name} [{self.department}]"


class Post(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    owner = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    date_pub = models.DateTimeField()
    date_last_mod = models.DateTimeField()
    content = models.TextField()

    class Meta:
        unique_together = (('classroom', 'title'),)

    def __str__(self):
        return f"Post: {self.title} [{self.classroom}]"


"""
=================================
    ASSIGNMENT
=================================
"""


class Assignment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    owner = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    type = models.CharField(max_length=8, default='regular',
                            choices=[('regular', 'Regular'),
                                     ('question', 'Question')])
    title = models.CharField(max_length=300)
    date_pub = models.DateTimeField()
    date_last_mod = models.DateTimeField()
    date_due = models.DateTimeField()
    content = models.TextField()
    file = models.FileField(null=True, blank=True)
    review_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"Assignment: {self.title} [ {self.classroom} ]"

    @property
    def has_due_expired(self):
        if d_t(self.date_due) < d_t(datetime.now()):
            return True
        return False

    @property
    def pending_submissions(self) -> int:
        _all_stu = self.classroom.department.student_set.count()
        _all_sub_done = self.submission_set.count()
        pending = int(_all_stu) - int(_all_sub_done)
        return pending


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    owner = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_sub = models.DateTimeField()
    grade = models.CharField(max_length=20, null=True, blank=True)
    file = models.FileField(upload_to="submitted_assignments", blank=True, null=True)
    lec_comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Submission By: {self.owner.user.username} [Assignment-> {self.assignment.title}]"

    @property
    def is_late_submit(self):
        """
        If the submission is a late submit or not.
        :return:
        """
        if d_t(self.date_sub) > d_t(self.assignment.date_due):
            return True
        return False

    def get_short_file_name(self):
        name = self.file.name
        return os.path.basename(name)[-28:]


"""
=================================
    MEETING
=================================
"""


class Meeting(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    owner = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    topic = models.CharField(max_length=300)
    start = models.DateTimeField()
    description = models.TextField(null=True, blank=True)
    meeting_url = models.URLField(null=True, blank=True)
    meeting_id = models.CharField(null=True, blank=True, max_length=300)
    meeting_pwd = models.CharField(null=True, blank=True, max_length=200)
    recording_url = models.URLField(null=True, blank=True)

    class Meta:
        unique_together = (('classroom', 'topic'),)

    def __str__(self):
        return f"Meeting: {self.topic} [Class-> {self.classroom.name}" \
               f" {self.classroom.department.batch.year} Batch]"

    @property
    def get_short_meeting_topic(self):
        if len(str(self.topic)) > 24:
            return f"{self.topic[:20]} ..."
        else:
            return self.topic

    @property
    def is_today(self):
        now = datetime.now()
        t_year, t_month, t_day = now.year, now.month, now.day
        start = d_t(self.start)
        s_year, s_month, s_day = start.year, start.month, start.day

        if t_year == s_year and t_month == s_month and t_day == s_day:
            return True
        return False

    @property
    def is_expired(self):
        if datetime.today() > d_t(self.start):
            return True




"""
=================================
    QUESTION
=================================
"""


class Question(models.Model):
    title = models.CharField(max_length=300)
    question = models.TextField()
    answer_type = models.CharField(max_length=8, choices=[('fixed', 'Fixed'), ('variable', 'Variable')])


"""
=================================
    QUIZZES
=================================
"""


class Quiz(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    owner = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    description = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(default=datetime.now())
    start = models.DateTimeField()
    duration = models.IntegerField()
    accept_after_expired = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('')


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)


class QuizQuestionAnswer(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)


class QuizStuResponse(models.Model):
    pass

