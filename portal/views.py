import json
import threading
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import AdditionalWork
from django.contrib.auth.decorators import login_required
from classroom.models import Question, QuizResult
from django.db.models import Avg, Count
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from classroom.models import LiveClass
from .models import LiveClass 
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
import uuid
from django.db import IntegrityError
from django.http import JsonResponse
import os
import resend
from classroom.models import QuizResult
from django.db.models import Avg, Count
import json

resend.api_key = os.getenv("RESEND_API_KEY")

def welcome_page(view):
    return render(view, 'portal/welcome.html')

def selection_page(request):
    return render(request, 'portal/selection.html')

def teacher_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        
        try:
            user_obj = User.objects.get(email=email, role='teacher')
            user = authenticate(request, username=user_obj.username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('teacher_dashboard')
            else:
                return render(request, 'portal/teacher_login.html', {'error': 'Invalid Password'})
        except User.DoesNotExist:
            return render(request, 'portal/teacher_login.html', {'error': 'Teacher account not found'})
            
    return render(request, 'portal/teacher_login.html')

def teacher_dashboard(request):
    return render(request, 'classroom/dashboard_teacher.html')

def student_register(request, grade):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        try:
            user = User.objects.create_user(
                username=username, 
                email=email, 
                password=password, 
                role=role
            )
            user.is_verified = False 
            user.save()

            def send_resend_notification():
                try:
                    resend.Emails.send({
                        "from": "Netwronix <onboarding@resend.dev>",
                        "to": ["vaaltein.t@gmail.com"], 
                        "subject": f"Action Required: {username} Registered",
                        "html": f"<p>Student <strong>{username}</strong> registered for Grade {grade}. Please verify them in the dashboard.</p>"
                    })
                    print(f"✅ Teacher alerted via Resend for {username}")
                except Exception as e:
                    print(f"❌ Resend Teacher Alert Error: {e}")

            threading.Thread(target=send_resend_notification).start()

            return render(request, 'portal/student_register.html', {
                'grade': grade, 'registration_success': True, 'username': username
            })

        except IntegrityError:
            return render(request, 'portal/student_register.html', {'grade': grade, 'registration_error': True})
    
    return render(request, 'portal/student_register.html', {'grade': grade})

def verify_students(request):
    pending_students = User.objects.filter(is_verified=False).exclude(role='teacher')
    
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        action = request.POST.get('action')
        student = User.objects.get(id=student_id)

        if action == "approve":
            student.is_verified = True
            student.save()
            subject = "Netwronix | Account Verified!"
            message = f"Hi {student.username}, your account for Grade {student.role} has been verified. Log in here: https://netwronix-project-u3vs.onrender.com/login/student/"
        elif action == "decline":
            student_name = student.username
            recipient = student.email
            student.delete()
            subject = "Netwronix | Registration Declined"
            message = f"Hi {student_name}, unfortunately, your registration request was not approved."
        
      
        def send_resend_verification():
            try:
                
                resend.Emails.send({
                    "from": "Netwronix <onboarding@resend.dev>",
                    "to": [student.email if action == "approve" else recipient],
                    "subject": subject,
                    "html": f"<p>{message}</p>"
                })
                print(f"✅ Student notification sent via Resend")
            except Exception as e:
                print(f"❌ Resend Student Notification Error: {e}")

        threading.Thread(target=send_resend_verification).start()
        return redirect('verify_students')

    return render(request, 'classroom/verify_students.html', {'students': pending_students})

def student_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        p_word = request.POST.get('password')
        
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=p_word)
            
            if user is not None:
                if user.role == 'teacher':
                    return render(request, 'portal/student_login.html', {'error': 'This is for students. Use the Teacher Portal.'})
                
                if user.is_verified:
                    login(request, user)
                    return redirect('dashboard_student')
                else:
                    return render(request, 'portal/student_login.html', {'error': 'Your account is pending teacher verification.'})
            else:
                return render(request, 'portal/student_login.html', {'error': 'Invalid password.'})
                
        except User.DoesNotExist:
            return render(request, 'portal/student_login.html', {'error': 'No student account found with this email.'})
            
    return render(request, 'portal/student_login.html')


@login_required
def dashboard_student(request):
    
    user_role = request.user.role
    grade_number = user_role.replace('grade', '') if 'grade' in user_role else user_role
    
    active_classes = LiveClass.objects.filter(grade=grade_number)
    
    context = {
        'grade': grade_number,
        'role': user_role,
        'active_classes': active_classes  
    }
    return render(request, 'classroom/dashboard_student.html', context)

def logout_view(request):
    logout(request)
    return redirect('welcome')

def manage_students(request):
    students = User.objects.exclude(role='teacher').order_by('role', 'username')
    
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        action = request.POST.get('action')
        student = User.objects.get(id=student_id)

        if action == "deactivate":
            student.is_verified = False
        elif action == "activate":
            student.is_verified = True
            
        student.save()
        return redirect('manage_students')

    return render(request, 'classroom/manage_students.html', {'students': students})

def additional_work(request):
    if request.method == "POST":
        title = request.POST.get('title')
        link = request.POST.get('link')
        grade = request.POST.get('grade')
        
        AdditionalWork.objects.create(title=title, link=link, grade=grade)
        return redirect('additional_work')

    works = AdditionalWork.objects.all().order_by('-date_posted')
    return render(request, 'classroom/additional_work.html', {'works': works})

def delete_additional_work(request, work_id):
    work = AdditionalWork.objects.get(id=work_id)
    work.delete()
    return redirect('additional_work')



@login_required
def grade11_dashboard(request):
    return render(request, 'classroom/dashboard_student.html', {'grade': '11'})

@login_required
def more_materials(request, grade):
    resources = AdditionalWork.objects.filter(grade=grade).order_by('-date_posted')
    
    return render(request, 'classroom/more_materials.html', {
        'grade': grade,
        'resources': resources
    })

@login_required
def lab_selection(request, grade): 
   
    return render(request, 'classroom/lab_selection.html', {
        'grade': grade
    })

@login_required
def physics_simulations(request, grade, topic):
    simulations = {
        
        'vectors': {
            'title': 'Vector Addition',
            'url': 'https://phet.colorado.edu/sims/html/vector-addition/latest/vector-addition_en.html',
            'desc': 'Experiment with vector magnitude, angle, and components.'
        },
        'newton-laws': {
            'title': 'Forces and Motion',
            'url': 'https://phet.colorado.edu/sims/html/forces-and-motion-basics/latest/forces-and-motion-basics_en.html',
            'desc': 'Explore the relationship between force, mass, and acceleration.'
        },
        'gravitation': {
            'title': 'Gravity Force Lab',
            'url': 'https://phet.colorado.edu/sims/html/gravity-force-lab/latest/gravity-force-lab_en.html',
            'desc': 'Visualize how mass and distance affect the gravitational pull between objects.'
        },
        'coulomb-law': {
            'title': 'Coulomb\'s Law',
            'url': 'https://phet.colorado.edu/sims/html/coulombs-law/latest/coulombs-law_en.html',
            'desc': 'Visualize the electrostatic force between two charged particles.'
        },
        
        
        'projectile-motion': {
            'title': 'Vertical Projectile Motion',
            'url': 'https://phet.colorado.edu/sims/html/projectile-motion/latest/projectile-motion_en.html',
            'desc': 'Launch objects and analyze their flight path and velocity.'
        },
        'momentum': {
            'title': 'Collision Lab',
            'url': 'https://phet.colorado.edu/sims/html/collision-lab/latest/collision-lab_en.html',
            'desc': 'Investigate simple and complex collisions in 1D and 2D.'
        },
        'organic-chem': {
            'title': 'Build a Molecule',
            'url': 'https://phet.colorado.edu/sims/html/build-a-molecule/latest/build-a-molecule_en.html',
            'desc': 'Construct organic structures and learn molecular geometry.'
        }
    }

    selected_sim = simulations.get(topic)
    
    context = {
        'sim': selected_sim,
        'grade': grade,
        'topic': topic
    }
    return render(request, 'classroom/simulations.html', context)

@login_required
def quiz_view(request, grade):
    questions = Question.objects.filter(grade=grade)
    
    return render(request, 'classroom/quiz.html', {
        'questions': questions,
        'grade': grade
    })


@login_required
def submit_quiz(request):
    if request.method == 'POST':
        score = 0
        total_questions = 0
        results_list = []
        quiz_topic = "General" 

        for key, value in request.POST.items():
            if key.startswith('question_'):
                question_id = key.replace('question_', '')
                try:
                    question = Question.objects.get(id=question_id)
                    total_questions += 1
                    
                   
                    if total_questions == 1:
                        quiz_topic = question.topic

                    
                    is_correct = (question.correct_answer == value)
                    
                    if is_correct:
                        score += 1
                    
                    results_list.append({
                        'question': question.text,
                        'your_answer': value,
                        'correct_answer': question.correct_answer,
                        'is_correct': is_correct
                    })
                except Question.DoesNotExist:
                    continue

        percentage = (score / total_questions * 100) if total_questions > 0 else 0

        
        QuizResult.objects.create(
            student=request.user,
            topic=quiz_topic, 
            grade=getattr(request.user, 'role', 'N/A'), 
            score=score,
            total_questions=total_questions,
            percentage=round(percentage, 2)
        )

        return render(request, 'classroom/results.html', {
            'score': score,
            'total': total_questions,
            'percentage': round(percentage, 2),
            'results': results_list
        })
    return redirect('welcome')



@login_required
def manage_quizzes(request):
    if request.user.role != 'teacher':
        return redirect('welcome')

    if request.method == "POST":
        Question.objects.create(
            text=request.POST.get('text'),
            grade=request.POST.get('grade'),
            topic=request.POST.get('topic'),
            option_a=request.POST.get('option_a'),
            option_b=request.POST.get('option_b'),
            option_c=request.POST.get('option_c'),
            option_d=request.POST.get('option_d'),
            correct_answer=request.POST.get('correct_option') 
        )
        return redirect('manage_quizzes')

    questions = Question.objects.all().order_by('-id')
    return render(request, 'classroom/manage_quizzes.html', {'questions': questions})

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

@login_required
def view_results(request):
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        return redirect('welcome')
        
    

    
    results = QuizResult.objects.all().order_by('-date_taken')

    
    topic_performance = list(QuizResult.objects.values('topic').annotate(
        avg_score=Avg('percentage'),  
        student_count=Count('id')
    ).order_by('-avg_score'))

    
    grade_performance = list(QuizResult.objects.values('grade').annotate(
        avg_score=Avg('percentage'),
        student_count=Count('id')
    ).order_by('grade'))

    context = {
        'results': results,
        'topic_json': json.dumps(topic_performance, cls=DecimalEncoder),
        'grade_json': json.dumps(grade_performance, cls=DecimalEncoder),
    }
    return render(request, 'classroom/student_results.html', context)

@login_required
def clear_all_results(request):
    if hasattr(request.user, 'role') and request.user.role == 'teacher':
        from classroom.models import QuizResult
        QuizResult.objects.all().delete()
    return redirect('view_results')

@login_required
def delete_question(request, question_id):
    if hasattr(request.user, 'role') and request.user.role == 'teacher':
        from classroom.models import Question
        try:
            question = Question.objects.get(id=question_id)
            question.delete()
        except Question.DoesNotExist:
            pass
    return redirect('manage_quizzes')


@login_required
def join_class(request, meeting_id):
    live_class = get_object_or_404(LiveClass, meeting_id=meeting_id)
    return render(request, 'classroom/live_room.html', {
        'live_class': live_class,
        'room_name': live_class.meeting_id,
        'user_name': request.user.get_full_name() or request.user.username
        
    })

def check_class_exists(request, meeting_id):
    exists = LiveClass.objects.filter(meeting_id=meeting_id).exists()
    return JsonResponse({'active': exists})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard_student')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'classroom/change_password.html', {'form': form})





def create_live_class(request):
    if request.method == "POST":
        title = request.POST.get('title')
        grade = request.POST.get('grade')
        
        
        unique_id = uuid.uuid4().hex[:10]
        meeting_id = f"{title}_{grade}_{unique_id}".replace(" ", "_")
        
        
        LiveClass.objects.create(
            title=title,
            grade=grade,
            meeting_id=meeting_id,
            teacher=request.user
        )
        
        
        return redirect('join_class', meeting_id=meeting_id)
    
    
    return render(request, 'classroom/create_live_class.html')

@login_required
def end_live_class(request, meeting_id):
    if request.user.role == 'teacher':

        LiveClass.objects.all().delete()
        messages.success(request, "Live classes have ended.")
        return redirect('teacher_dashboard')
    return redirect('dashboard_student')