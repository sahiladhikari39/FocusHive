from django.shortcuts import redirect, render
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
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
    if request.method=="POST":
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
    return render(request, 'dashboard.html', {'name': request.user.first_name})


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
        return redirect("/meeting?roomID=" + roomID)
    return render(request, 'joinroom.html')


# Add these imports
from django.http import JsonResponse
import json
from .models import UserInterest, StudySession, PomodoroSession
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.views.decorators.csrf import csrf_exempt


# Add after logout_view function
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

# Update the dashboard view
@login_required
def dashboard(request):
    # Get user interests
    try:
        user_interest = UserInterest.objects.get(user=request.user)
        user_interests = user_interest.interests
    except UserInterest.DoesNotExist:
        user_interests = ""
    
    # Get recommendations with scores
    scored_recommendations = get_recommendations(request.user)
    
    # Extract just the sessions for display
    recommendations = [session for session, score in scored_recommendations]
    
    # Add tags_list to each session for template
    for session in recommendations:
        session.tags_list = [tag.strip() for tag in session.tags.split(",")]
    
    return render(request, 'dashboard.html', {
        'name': request.user.first_name,
        'recommendations': recommendations,
        'user_interests': user_interests,
        'scored_recommendations': scored_recommendations
    })

# Update the get_recommendations function to return scores
def get_recommendations(user):
    try:
        user_interest = UserInterest.objects.get(user=user)
        interests = [tag.strip().lower() for tag in user_interest.interests.split(",") if tag.strip()]
    except UserInterest.DoesNotExist:
        return []
    
    sessions = StudySession.objects.all()
    if not sessions:
        return []
    
    scored_sessions = []
    
    for session in sessions:
        # Normalize session tags
        session_tags = [tag.strip().lower() for tag in session.tags.split(",")]
        
        # Calculate match score
        match_score = 0
        for interest in interests:
            if interest in session_tags:
                match_score += 1  # Exact match bonus
            else:
                # Partial match (substring)
                for tag in session_tags:
                    if interest in tag:
                        match_score += 0.5
                        break
        
        # Apply length penalty to prevent over-matching
        relevance = match_score / max(1, len(interests))
        
        if relevance > 0:
            scored_sessions.append((session, relevance))
    
    # Sort by relevance
    scored_sessions.sort(key=lambda x: x[1], reverse=True)
    
    # Return only top 3 relevant sessions with scores
    return scored_sessions[:3]