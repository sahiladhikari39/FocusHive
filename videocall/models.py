from django.db import models
from django.contrib.auth.models import User

class UserInterest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interests = models.TextField(blank=True)

class StudySession(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    tags = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(User, related_name='joined_sessions', blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Vector update garda errors aayo so remove gareko

class PomodoroSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField()
    session_type = models.CharField(max_length=10, choices=[
        ('work', 'Work'),
        ('break', 'Break')
    ])