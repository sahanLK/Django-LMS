import os.path
from datetime import datetime, timedelta
from django.db import models
from users.models import CustomizedUser, Student, Lecturer
from main.models import Batch, Department
from ckeditor.fields import RichTextField
from main.funcs import (
    local_to_utc_aware,
    local_to_utc_naive,
    utc_to_local_aware,
    utc_to_local_naive,
    get_naive_dt
)


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
    _date_last_mod = models.DateTimeField(auto_now=True)
    _date_due = models.DateTimeField()
    content = RichTextField()   # From CK Editor
    file = models.FileField(null=True, blank=True, upload_to='assignment-files')  # This won't be used actually
    review_complete = models.BooleanField(default=False)

    class Meta:
        unique_together = (('title', 'classroom'),)

    def __str__(self):
        return f"Assignment: {self.title} [ {self.classroom} ]"

    @property
    def type(self):
        return "assignment"

    @property
    def date_created(self):
        return utc_to_local_naive(self._date_created)

    @property
    def date_due(self):
        return utc_to_local_naive(self._date_due)

    @property
    def date_mod(self):
        return utc_to_local_naive(self._date_last_mod)

    @property
    def expired(self):
        if get_naive_dt(self.date_due) < get_naive_dt(datetime.utcnow()):
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
    _date_created = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=20, null=True, blank=True)
    file = models.FileField(blank=True, null=True)  # this should not be saved. instead, <SubmissionFile> will be used.
    lec_comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Submission By: {self.owner.user.username}" \
               f" [Assignment-> {self.assignment.title}]"

    @property
    def date_created(self):
        return utc_to_local_naive(self._date_created)

    @property
    def is_late_submit(self):
        """
        If the submission is a late submit or not.
        :return:
        """
        if self.date_created > self.assignment.date_due:
            return True
        return False


class SubmissionFile(models.Model):
    """
    Used for multiple file upload functionality
    """
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submission-files')

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
    _date_mod = models.DateTimeField(auto_now=True)
    _start = models.DateTimeField()
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
    def type(self):
        return 'meeting'

    @property
    def date_created(self):
        return utc_to_local_naive(self._date_created)

    @property
    def date_mod(self):
        return utc_to_local_naive(self._date_mod)

    @property
    def start(self):
        return utc_to_local_naive(self._start)

    @property
    def get_short_meeting_topic(self):
        if len(str(self.topic)) > 24:
            return f"{self.topic[:20]} ..."
        else:
            return self.topic

    @property
    def is_today(self):
        if self.start.date() == datetime.today().date():
            return True
        print("not today:", self.start)
        return False

    @property
    def is_expired(self):
        if get_naive_dt(datetime.utcnow()).date() > get_naive_dt(self._start).date():
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
    _start = models.DateTimeField()
    duration = models.IntegerField()
    accept_after_expired = models.BooleanField(default=True)

    class Meta:
        unique_together = (('classroom', 'title'),)

    def __str__(self):
        return f"Quiz: {self.title}"

    @property
    def type(self):
        return 'quiz'

    @property
    def date_created(self):
        return utc_to_local_naive(self._date_created)

    @property
    def date_modified(self):
        return utc_to_local_naive(self._date_modified)

    @property
    def live(self):
        if self.start < datetime.now() < self.end:
            return True
        return False

    @property
    def expired(self):
        if datetime.now() > self.end:
            return True
        return False

    @property
    def start(self):
        return utc_to_local_naive(self._start)

    @property
    def end(self):
        return self.start + timedelta(minutes=float(self.duration))


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
    _date_created = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0)

    def __str__(self):
        return f"Quiz Response by: {self.owner.user.get_full_name()}"

    @property
    def date_created(self):
        return utc_to_local_naive(self._date_created)


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
