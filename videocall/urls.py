from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False), name='root_redirect'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('meeting/', views.videocall, name='meeting'),
    path('join/', views.join_room, name='join'),
    path('logout/', views.logout_view, name='logout'),
    path('save-pomodoro/', views.save_pomodoro, name='save_pomodoro'),
    path('profile/', views.profile, name='profile'),

    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('create-session/', views.create_session, name='create_session'),
]