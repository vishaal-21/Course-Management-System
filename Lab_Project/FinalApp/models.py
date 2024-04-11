from django.db import models
import hashlib
from django.core.validators import FileExtensionValidator

ext_validator=FileExtensionValidator(['.pdf'])

class UsersAll(models.Model):
    user_id = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    password_hash = models.CharField(max_length=100, default='')
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    type_of_user = models.CharField(max_length=20)
    cgpa = models.DecimalField(max_digits=5, decimal_places=2, default=0.0) 

    def __str__(self):
        return self.name
    
    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

class Courses(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    teacher = models.CharField(max_length=50)
    total_credits = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
class Assignment(models.Model):
    assignment_number = models.IntegerField()
    assignment_name = models.CharField(max_length=100)
    total_marks = models.IntegerField()
    upload_date = models.DateField()
    due_date = models.DateField()
    student_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=100)
    submission_date = models.DateField(null=True, blank=True)
    student_marks=models.DecimalField(max_digits=5, decimal_places=2, default=0.0) 
    files = models.FileField(upload_to='files/',validators=[ext_validator])

    def __str__(self):
        return f"{self.assignment_number}: {self.assignment_name}"
    
class Exam(models.Model):
    date_of_exam = models.DateField()
    exam_name = models.CharField(max_length=100)
    total_marks = models.PositiveIntegerField()
    student_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20)
    student_marks=models.DecimalField(max_digits=5, decimal_places=2, default=0.0) 

    def __str__(self):
        return self.exam_name
    
class Attendance(models.Model):
    date = models.DateField()
    student_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20)
    attended_or_not = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student_name} - {self.date}"