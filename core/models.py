from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

class RegisteredUser(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('community_leader', 'Community Leader'),
        ('events_leader', 'Events Leader'),
        ('user', 'User'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user'
    )

    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    course = models.CharField(max_length=255, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.email}) - {self.role}"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    

class Community(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class CommunityMembership(models.Model):
    user = models.ForeignKey(RegisteredUser, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)


class Thread(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='threads')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey(RegisteredUser, on_delete=models.SET_NULL, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_by = models.ForeignKey(RegisteredUser, on_delete=models.SET_NULL, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.created_by.username if self.created_by else 'Unknown'}"