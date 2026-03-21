from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    # Portal & Authentication
    path('', views.welcome_page, name='welcome'),
    path('portal-selection/', views.selection_page, name='selection'),
    path('login/teacher/', views.teacher_login, name='teacher_login'),
    path('login/student/', views.student_login, name='student_login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/', views.dashboard_student, name='dashboard_student'),

    # Student Management
    path('register/<str:grade>/', views.student_register, name='student_register'),
    path('verify-students/', views.verify_students, name='verify_students'),
    path('manage-students/', views.manage_students, name='manage_students'),

    # Live Classroom (Cleaned up: Only ONE join-class path)
    path('join-class/<str:meeting_id>/', views.join_class, name='join_class'),
    path('end-live-class/<str:meeting_id>/', views.end_live_class, name='end_live_class'),
    path('create-live-class/', views.create_live_class, name='create_live_class'),
    path('check-class/<str:meeting_id>/', views.check_class_exists, name='check_class_exists'),

    # Content & Materials
    path('additional-work/', views.additional_work, name='additional_work'),
    path('delete-work/<int:work_id>/', views.delete_additional_work, name='delete_additional_work'),
    path('more-materials/<str:grade>/', views.more_materials, name='more_materials'),
    path('labs/<str:grade>/', views.lab_selection, name='lab_selection'),
    path('simulations/<str:grade>/<str:topic>/', views.physics_simulations, name='physics_simulations'),

    # Quizzes & Results
    path('quizzes/<str:grade>/', views.quiz_view, name='quiz_view'),
    path('submit-quiz/', views.submit_quiz, name='submit_quiz'),
    path('manage-quizzes/', views.manage_quizzes, name='manage_quizzes'),
    path('delete-question/<int:question_id>/', views.delete_question, name='delete_question'),
    path('student-results/', views.view_results, name='view_results'),
    path('clear-results/', views.clear_all_results, name='clear_results'),

    # Password Management (Internal & Reset)
    path('change-password/', auth_views.PasswordChangeView.as_view(
        template_name='classroom/change_password.html',
        success_url='/'
    ), name='change_password'),
    
    path('reset-password/', 
         auth_views.PasswordResetView.as_view(template_name='portal/password_reset.html'), 
         name='password_reset'),
    path('reset-password-done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='portal/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='portal/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('reset-password-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='portal/password_reset_complete.html'), 
         name='password_reset_complete'),
]