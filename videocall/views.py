from django.shortcuts import redirect, render
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from .models import UserInterest, StudySession, PomodoroSession
from django.views.decorators.csrf import csrf_exempt

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'login.html', {'success': "Registration successful. Please login."})
        else:
            error_message = form.errors.as_text()
            return render(request, 'register.html', {'error': error_message})
    return render(request, 'register.html')

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("/dashboard")
        else:
            return render(request, 'login.html', {'error': "Invalid credentials. Please try again."})
    return render(request, 'login.html')

@login_required
def dashboard(request):
    from .recommendations import get_recommendations
    
    try:
        user_interests = UserInterest.objects.get(user=request.user).interests
    except UserInterest.DoesNotExist:
        user_interests = ""
    
    all_sessions = StudySession.objects.all()
    
    try:
        # Get recommendations with similarity scores (0-1 range)
        recommendations_with_scores = get_recommendations(request.user)
        
        # Create a list of sessions with their scores attached
        recommendations_with_data = []
        for item in recommendations_with_scores:
            if isinstance(item, tuple) and len(item) == 2:
                session, score = item
                # Format score to 2 decimal places (0-1 range)
                session.similarity_score = round(score, 2)
            else:
                # Handle case where we get just a session object
                session = item
                session.similarity_score = 0.5  # Default score
                
            session.tags_list = [tag.strip() for tag in session.tags.split(",")]
            recommendations_with_data.append(session)
            
    except Exception as e:
        print(f"Error processing recommendations: {e}")
        # Fallback: show recent sessions with default scores
        recommendations_with_data = []
        recent_sessions = StudySession.objects.all().order_by('-created_at')[:5]
        for session in recent_sessions:
            session.similarity_score = 0.5
            session.tags_list = [tag.strip() for tag in session.tags.split(",")]
            recommendations_with_data.append(session)
    
    return render(request, 'dashboard.html', {
        'name': request.user.first_name,
        'recommendations': recommendations_with_data,
        'user_interests': user_interests,
        'all_sessions': all_sessions,
    })

@login_required
def profile(request):
    try:
        interest = UserInterest.objects.get(user=request.user)
    except UserInterest.DoesNotExist:
        interest = UserInterest(user=request.user, interests="")

    if request.method == 'POST':
        interests = request.POST.get('interests', '')
        interest.interests = interests
        interest.save()
        return redirect('dashboard')

    return render(request, 'profile.html', {'interests': interest.interests})

@login_required
def videocall(request):
    return render(request, 'videocall.html', {'name': request.user.first_name + " " + request.user.last_name})

@login_required
def logout_view(request):
    logout(request)
    return redirect("/login")

@login_required
def join_room(request):
    if request.method == 'POST':
        roomID = request.POST['roomID']
        try:
            session = StudySession.objects.get(id=roomID)
            session.participants.add(request.user)
            session.save()
        except StudySession.DoesNotExist:
            pass
        return redirect(f"/meeting?roomID={roomID}")
    return render(request, 'joinroom.html')

@csrf_exempt
@login_required
def save_pomodoro(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_type = 'work' if data['is_work_time'] else 'break'
        PomodoroSession.objects.create(
            user=request.user,
            duration=data['duration'],
            session_type=session_type
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def create_session(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        tags = request.POST.get('tags', '')
        
        session = StudySession.objects.create(
            name=name,
            description=description,
            tags=tags,
            created_by=request.user
        )
        
        return redirect(f"/meeting?roomID={session.id}")
    
    return render(request, 'create_session.html')

def root_redirect(request):
    return redirect('/login/')