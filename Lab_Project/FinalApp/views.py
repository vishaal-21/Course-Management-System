from django.shortcuts import render, redirect, get_object_or_404
from distutils.util import strtobool
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from .models import UsersAll, Courses, Assignment, Exam, Attendance
import hashlib
from django.db.models import Count,Avg,Sum
from django.urls import reverse
from django.db import connection

from django.conf import settings
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os

def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        try:
            users=UsersAll.objects.filter(name=username)

            for user in users:
                if user.password_hash==hashlib.sha256(password.encode()).hexdigest():
                    request.session['username'] = username
                    request.session['password'] = password

                    if user.type_of_user == 'Admin':
                        return redirect('admin_home')  
                    elif user.type_of_user == 'Teacher':
                        return redirect('teacher_home')  
                    elif user.type_of_user == 'Student':
                        return redirect('student_home') 
                else:
                    return render(request, 'login.html', {'error': 'Invalid username or password'})
        except UsersAll.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid completely'})
    else:
        return render(request, 'login.html')

def admin_home(request):
    if request.method == 'POST':
        form_name=request.POST.get('form_name')

        if form_name=="course":
            name = request.POST.get('name')
            course_code = request.POST.get('course_code')
            creds = request.POST.get('credits')
            teacher = request.POST.get('teacher')

            if Courses.objects.filter(name=name, code=course_code).exists():
                error_message = "Course with the same name and code already exists."
                courses = Courses.objects.all() 
                return render(request, 'admin_home.html', {'courses': courses, 'error_message': error_message})
            else:
                new_course = Courses(name=name, code=course_code, total_credits=creds, teacher=teacher)
                new_course.save()

        elif form_name=="teacher":
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            tid = request.POST.get('id')

            if UsersAll.objects.filter(name=name, user_id=tid).exists():
                error_message = "User with the same name and ID already exists."
                users = UsersAll.objects.all() 
                return render(request, 'admin_home.html', {'users': users, 'error_message': error_message})
            else:
                new_user = UsersAll(name=name, email=email, phone_number=phone_number,user_id=tid,type_of_user='Teacher')
                new_user.set_password(tid)
                new_user.save()

        elif form_name=="student":
            name = request.POST.get('name')
            student_id = request.POST.get('student_id')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            cgpa= request.POST.get('cgpa')

            if UsersAll.objects.filter(name=name, user_id=student_id).exists():
                error_message = "User with the same name and ID already exists."
                users = UsersAll.objects.all() 
                return render(request, 'admin_home.html', {'users': users, 'error_message': error_message})
            else:
                new_user = UsersAll(name=name, user_id=student_id, email=email, phone_number=phone_number,cgpa=cgpa,type_of_user='Student')
                new_user.set_password(student_id)
                new_user.save()
    else:
        pass

    courses=Courses.objects.all()
    teachers=UsersAll.objects.filter(type_of_user='Teacher')
    students=UsersAll.objects.filter(type_of_user='Student')
    return render(request,'admin_home.html',{'courses':courses,'teachers':teachers,'students':students})

def delete_course(request, course_id):
    course = get_object_or_404(Courses, id=course_id)
    course.delete()
    return redirect('admin_home')

def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(UsersAll, id=teacher_id)
    teacher.delete()
    return redirect('admin_home')

def delete_student(request, student_id):
    student = get_object_or_404(UsersAll, id=student_id)
    student.delete()
    return redirect('admin_home')

def logout_user(request):
    logout(request)
    return redirect('login_page')

def teacher_home(request):
    username = request.session.get('username')
    password = request.session.get('password')
    daily_attendees={}

    user=Courses.objects.get(teacher=username)
    assignment_titles=Assignment.objects.values('assignment_name','due_date','total_marks').distinct()
    exam_titles=Exam.objects.values('exam_name','date_of_exam','total_marks').distinct()
    unique_dates = Attendance.objects.values('date').distinct()
    classes_taken=len(unique_dates)
    assignment=Assignment.objects.all()

    assignment_submissions = Assignment.objects.filter(submission_date__isnull=False)
    assignment_counts = assignment_submissions.values('assignment_name').annotate(num_elements=Count('id'))
    average_marks_per_exam = Exam.objects.values('exam_name').annotate(average_marks=Avg('student_marks'))

    num_ungraded_assignments=num_ungraded_exams=0
    total_marks_per_assignment = Assignment.objects.values('assignment_name').annotate(total_marks=Sum('student_marks'))
    total_marks_per_exam = Exam.objects.values('exam_name').annotate(total_marks=Sum('student_marks'))

    for entry in total_marks_per_assignment:
        if entry['total_marks']==0:
            num_ungraded_assignments+=1

    for entry in total_marks_per_exam:
        if entry['total_marks']==0:
            num_ungraded_exams+=1

    for date_entry in unique_dates:
        date = date_entry['date']
        attendees = Attendance.objects.filter(date=date, attended_or_not=True).count()
        daily_attendees[date]=attendees

    for entry in average_marks_per_exam:
        entry['average_marks'] = round(entry['average_marks'], 2)

    total_assignments=len(assignment_titles)
    total_exams=len(exam_titles)
    students_num=len(UsersAll.objects.filter(type_of_user='Student'))
    return render(request,'teacher_home.html',{'user':user,'assignment_titles':assignment_titles,'assignment':assignment,
                                               'total':total_assignments,'total_exams':total_exams,'tot_students':students_num,
                                               'assignment_counts':assignment_counts,'exam_titles':exam_titles,'exam_average':average_marks_per_exam,
                                               'unique_dates':unique_dates,'daily_attendees':daily_attendees,'tot_classes':36,'classes_taken':classes_taken,
                                               'num_ungraded_assignments':num_ungraded_assignments,'num_ungraded_exams':num_ungraded_exams})

def assignments_page(request):
    if request.method == 'POST':
        form_name = request.POST.get('form_name')
        if form_name == 'assignment':
            assignment_number = request.POST.get('assignment_number')
            assignment_name = request.POST.get('assignment_name')
            total_marks = request.POST.get('total_marks')
            upload_date = timezone.now().date()
            due_date = request.POST.get('due_date')

            if Assignment.objects.filter(assignment_number=assignment_number,assignment_name=assignment_name).exists():
                error_message = "User with the same name and ID already exists."
                return render(request, 'teacher/assignments.html', {'error_message': error_message})
            else:
                students=UsersAll.objects.filter(type_of_user='Student')

                for student in students:
                    assignment = Assignment(
                        assignment_number=assignment_number,
                        assignment_name=assignment_name,
                        total_marks=total_marks,
                        upload_date=upload_date,
                        due_date=due_date,
                        student_name=student.name,
                        student_id=student.user_id
                    )
                    assignment.save()

    assignment_titles=Assignment.objects.values('assignment_name','assignment_number','total_marks','upload_date','due_date').distinct()
    assignments=Assignment.objects.all()
    return render(request, 'teacher/assignments.html',{'assignment_titles':assignment_titles,'assignments':assignments})

def exams_page(request):
    if request.method == 'POST':
        form_name = request.POST.get('form_name')
        if form_name == 'exam':
            exam_name = request.POST.get('exam_name')
            total_marks = request.POST.get('total_marks')
            date_of_exam = request.POST.get('date_of_exam')

            if Exam.objects.filter(exam_name=exam_name,total_marks=total_marks).exists():
                error_message = "User with the same name and ID already exists."
                return render(request, 'teacher/exams.html', {'error_message': error_message})
            else:
                students=UsersAll.objects.filter(type_of_user='Student')

                for student in students:
                    exam = Exam(
                        exam_name=exam_name,
                        date_of_exam=date_of_exam,
                        total_marks=total_marks,
                        student_name=student.name,
                        student_id=student.user_id
                    )
                    exam.save()

    exam_titles=Exam.objects.values('date_of_exam','exam_name','total_marks').distinct()
    exams=Exam.objects.all()
    return render(request, 'teacher/exams.html',{'exams':exams,'exam_titles':exam_titles})

def notifications_page(request):
    return render(request, 'teacher/notifications.html')

def attendance_page(request):
    if request.method == 'POST':
        form_name = request.POST.get('form_name')
        if form_name == 'attendance':
            attendance_id = request.POST.get('attendance_id')
            attendance_date = request.POST.get('date')

            if Attendance.objects.filter(date=attendance_date).exists():
                error_message = "User with the same name and ID already exists."
                return render(request, 'teacher/attendance.html', {'error_message': error_message})
            else:
                students=UsersAll.objects.filter(type_of_user='Student')
                for student in students:
                    attendances=Attendance(
                        date=attendance_date,
                        student_name=student.name,
                        student_id=student.user_id
                    )
                    attendances.save()

    students=UsersAll.objects.filter(type_of_user='Student').order_by('user_id')
    unique_dates = Attendance.objects.values('date').distinct()
    attendances=Attendance.objects.all()
    return render(request, 'teacher/attendance.html', {'unique_dates': unique_dates,'attendances':attendances,'students':students})

def grades_page(request):
    assignment_titles=Assignment.objects.values('assignment_name','assignment_number','total_marks','due_date').distinct()
    exam_titles=Exam.objects.values('date_of_exam','exam_name','total_marks').distinct()
    exams=Exam.objects.all()
    assignments=Assignment.objects.all()
    return render(request, 'teacher/grades.html',{'assignment_titles':assignment_titles,'exam_titles':exam_titles,'exams':exams,'assignments':assignments})

def study_material_page(request):
    return render(request, 'teacher/study_material.html')

def delete_assignment(request, assignment_id):
    assignment = Assignment.objects.filter(assignment_number=assignment_id)

    if request.method == 'POST':
        assignment.delete()
        return redirect('assignments_page')
    else:
        pass

def delete_exam(request, exam_name):
    exam=Exam.objects.filter(exam_name=exam_name)
    print(exam)

    if request.method == 'POST':
        exam.delete()
    return redirect('exams_page')

def student_home(request):
    request.session['student_name'] = request.session.get('username')
    request.session['student_id'] = request.session.get('password')
    return render(request,'student_home.html')

def stu_assignments_page(request):
    request.session['student_name'] = request.session.get('student_name')
    request.session['student_id'] = request.session.get('student_id')

    assignments=Assignment.objects.all()
    return render(request,'student/assignment.html',{'assignments':assignments})

def stu_grades_page(request):
    student_name = request.session.get('student_name')
    student_id = request.session.get('student_id')

    assignments=Assignment.objects.filter(student_id=student_id)
    exams=Exam.objects.filter(student_id=student_id)
    total_assignment_marks=assignments.values_list('total_marks',flat=True)
    total_exam_marks=exams.values_list('total_marks',flat=True)

    scored_assignment_marks=assignments.values_list('student_marks',flat=True)
    scored_exam_marks=exams.values_list('student_marks',flat=True)
    
    total=sum(total_assignment_marks) + sum(total_exam_marks)
    scored=sum(scored_exam_marks) + sum(scored_assignment_marks)
    return render(request,'student/grades.html',{'assignments':assignments,'exams':exams,'total':total,'scored':scored})

def stu_attendance_page(request):
    student_name = request.session.get('student_name')
    student_id = request.session.get('student_id')

    attendance=Attendance.objects.filter(student_id=student_id)
    total=len(attendance.values_list('date',flat=True))
    list=attendance.values('date','attended_or_not')

    present=0
    for dict in list:
        print(dict)
        for key,value in dict.items():
            if key=='attended_or_not' and value:
                present+=1

    percentage=round(present/total*100,2)

    return render(request,'student/attendance.html',{'attendance':attendance,"present":present,'total':total,'percentage':percentage})

def stu_study_material_page(request):
    assignments=Assignment.objects.all()
    return render(request,'student/study_material.html',{'assignments':assignments})

def record_attendance(request):
    if request.method=='POST':
        attendance_data=request.POST.getlist('attendance[]')

        for data in attendance_data:
            attendance_date,student_id,attended=data.split('|')
            print(attendance_date,student_id,attended,sep='\t')
            attended = bool(strtobool(attended))

            Attendance.objects.update_or_create(
                student_id=student_id,
                date=attendance_date,
                defaults={'attended_or_not': attended}
            )
    
    return redirect(attendance_page)

def submit_marks(request):
    if request.method=='POST':
        form_name = request.POST.get('form_name')
        if form_name == 'examSubmit':
            for key, value in request.POST.items():
                if key.startswith('marks_'):
                    submission_name,student_id = key.split('_')[1:]
                    marks = value

                    Exam.objects.update_or_create(
                        exam_name=submission_name,
                        student_id=student_id,
                        defaults={'student_marks': marks}
                    )
        elif form_name == 'assignmentSubmit':
            for key, value in request.POST.items():
                if key.startswith('assign_'):
                    submission_name,student_id = key.split('_')[1:]
                    marks = value

                    Assignment.objects.update_or_create(
                        assignment_name=submission_name,
                        student_id=student_id,
                        defaults={'student_marks': marks}
                    )
        
    return redirect('grades_page')

def submit_assignment(request):
    student_name = request.session.get('student_name')
    student_id = request.session.get('student_id')
    
    if request.method=='POST' and request.FILES.get('submission_file'):
        submitted_file = request.FILES['submission_file']
        
        if 'submit_button' in request.POST:
            if is_pdf(submitted_file):
                Assignment.objects.update_or_create(
                    student_id=student_id,
                    defaults={'files': submitted_file, 'submission_date':timezone.now().date()}
                )
            else:
                pass

    return redirect('stu_assignments_page')

def is_pdf(file):
    header = file.read(4)

    if header == b'%PDF':
        return True
    else:
        return False
    
def view_file(request):
    assignments = Assignment.objects.all()
    return render(request, 'student/assignments.html', {'assignments': assignments})
