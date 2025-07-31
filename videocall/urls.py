from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('meeting/', views.videocall, name='meeting'),
    path('join/', views.join_room, name='join'),
    path('logout/', views.logout_view, name='logout'),

    # Add home and about paths
    path('home/', views.home, name='home'),  # This will be accessed via '/home/' in the browser
    path('about/', views.about, name='about'),  # This will be accessed via '/about/' in the browser
    path('contact/', views.contact, name='contact'),
    
    path('profile/', views.profile, name='profile'),
    path('save-pomodoro/', views.save_pomodoro, name='save_pomodoro'),
]
