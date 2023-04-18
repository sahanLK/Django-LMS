import os.path
import random
from datetime import datetime
from django.db import models
from django.urls import reverse
from users.models import CustomizedUser, Student, Lecturer
from main.models import Batch, Department
from main.funcs import get_naive_dt
from ckeditor.fields import RichTextField


class Classroom(models.Model):
    owner = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='owner')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    lecturers = models.ManyToManyField(Lecturer)
    name = models.CharField(max_length=300)
    description = models.TextField(max_length=150, null=True,  blank=True)
    background_img = models.ImageField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('department', 'name'),)

    def __str__(self):
        return f"Class: {self.name} [{self.department}]"


class Post(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    owner = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    _date_created = models.DateTimeField(auto_now_add=True)
    date_last_mod = models.DateTimeField(auto_now=True)
    content = RichTextField(blank=True, null=True)

    class Meta:
        unique_together = (('classroom', 'title'),)

    @property
    def date_created(self):
        return get_naive_dt(self._date_created)

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
    _date_created = models.DateTimeField(auto_now_add=True)
    date_last_mod = models.DateTimeField(auto_now=True)
    date_due = models.DateTimeField()
    content = RichTextField()
    file = models.FileField(null=True, blank=True)
    review_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"Assignment: {self.title} [ {self.classroom} ]"

    @property
    def date_created(self):
        return get_naive_dt(self._date_created)

    @property
    def has_due_expired(self):
        if get_naive_dt(self.date_due) < get_naive_dt(datetime.now()):
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
    date_created = models.DateTimeField(auto_now_add=True)
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
        if get_naive_dt(self.date_created) > get_naive_dt(self.assignment.date_created):
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
    _date_created = models.DateTimeField(auto_now_add=True)
    start = models.DateTimeField()
    description = models.TextField(null=True, blank=True)
    meeting_url = models.URLField(null=True, blank=True)
    meeting_id = models.CharField(null=True, blank=True, max_length=300)
    meeting_pwd = models.CharField(null=True, blank=True, max_length=200)
    recording_url = models.URLField(null=True, blank=True)

    class Meta:
        unique_together = (('classroom', 'topic'),)

    @property
    def date_created(self):
        return get_naive_dt(self._date_created)

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
        start = get_naive_dt(self.start)
        s_year, s_month, s_day = start.year, start.month, start.day

        if t_year == s_year and t_month == s_month and t_day == s_day:
            return True
        return False

    @property
    def is_expired(self):
        if datetime.today() > get_naive_dt(self.start):
            return True


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
    _date_created = models.DateTimeField(auto_now_add=True)
    _date_modified = models.DateTimeField(auto_now=True)
    start = models.DateTimeField()
    duration = models.IntegerField()
    accept_after_expired = models.BooleanField(default=True)

    # Can be used by a lecturer, to manually stop submissions
    accepting_answers = models.BooleanField(default=True)

    def __str__(self):
        return f"Quiz: {self.title}"

    @property
    def date_created(self):
        return get_naive_dt(self._date_created)

    @property
    def date_modified(self):
        return get_naive_dt(self._date_modified)

    @property
    def has_started(self):
        return random.choice([True, False])

    @property
    def start_time(self):
        return get_naive_dt(self.start) - get_naive_dt(datetime.utcnow())


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    question = models.TextField(default="")

    def __str__(self):
        return f"Question: {self.question} -> [<Quiz: {self.quiz.title}>]"

    @property
    def correct_answers(self):
        return self.answer_set.filter(correct=True)

    @property
    def incorrect_answers(self):
        return self.answer_set.filter(correct=False)


LETTER_CHOICES = [
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('E', 'E'),
    ('F', 'F'),
]


class QuizQuestionAnswer(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    letter = models.CharField(max_length=1, choices=LETTER_CHOICES)
    answer = models.CharField(max_length=300, default="")
    correct = models.BooleanField(default=False)    # Whether answer is a correct or incorrect

    def __str__(self):
        return f"Answer: {self.answer} -> " \
               f"[<Quiz: {self.question.quiz.title}> -> " \
               f"<Question: {self.question.question}>]"

    @property
    def get_q_id(self):
        id_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6}
        return id_map.get(str(self.letter))


class QuizStudentResponse(models.Model):
    """
    One single student response made by a student.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    owner = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Quiz Response by: {self.owner.user.get_full_name()}"


class QuizStudentResponseQuestion(models.Model):
    """
    <QuizStudentResponse> related.

    ONLY RELATED TO A ONE SINGLE <QuizStudentResponse> MADE BY A STUDENT.
    Do not use for anything else.
    """
    response = models.ForeignKey(QuizStudentResponse, on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)

    def __str__(self):
        return f"StudentResponseQuestion: {self.question.question}"


class QuizStudentResponseQuestionAnswer(models.Model):
    """
    <QuizStudentResponse> related.

    ONLY RELATED TO A ONE SINGLE <QuizStudentResponseQuestion>.
    Do not use for anything else.
    """
    response_question = models.ForeignKey(QuizStudentResponseQuestion, on_delete=models.CASCADE)
    answer = models.ForeignKey(QuizQuestionAnswer, on_delete=models.CASCADE)

    def __str__(self):
        return f"StudentResponseQuestionAnswer: {self.answer.answer}"
