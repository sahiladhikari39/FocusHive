from django.contrib import admin
from .models import StudySession, UserInterest, PomodoroSession

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'tags', 'created_by')

@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    list_display = ('user', 'interests')

@admin.register(PomodoroSession)
class PomodoroSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'duration', 'session_type', 'start_time')