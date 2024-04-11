from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path('',views.login_page,name='login_page'),
    path('admin_home/',views.admin_home,name='admin_home'),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),
    path('delete_teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('logout/',views.logout_user,name='logout_user'),
    path('teacher_home/',views.teacher_home,name='teacher_home'),
    path('teacher_home/assignments/', views.assignments_page, name='assignments_page'),
    path('teacher_home/exams/', views.exams_page, name='exams_page'),
    path('teacher_home/notifications/', views.notifications_page, name='notifications_page'),
    path('teacher_home/attendance/', views.attendance_page, name='attendance_page'),
    path('teacher_home/grades/', views.grades_page, name='grades_page'),
    path('teacher_home/study-material/', views.study_material_page, name='study_material_page'),
    path('delete_assignment/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),
    path('delete_exam/<str:exam_name>/', views.delete_exam, name='delete_exam'),
    path('student_home/',views.student_home,name='student_home'),
    path('student_home/assignments/',views.stu_assignments_page,name='stu_assignments_page'),
    path('student_home/grades/',views.stu_grades_page,name='stu_grades_page'),
    path('student_home/attendance/',views.stu_attendance_page,name='stu_attendance_page'),
    path('student_home/study_material/',views.stu_study_material_page,name='stu_study_material_page'),
    path('record_attendance',views.record_attendance,name='record_attendance'),
    path('submit_marks',views.submit_marks,name='submit_marks'),
    path('submit_assignment',views.submit_assignment,name='submit_assignment'),
    path('view_file/',views.view_file,name='view_file'),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)