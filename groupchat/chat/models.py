from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    code = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField(User, related_name='rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def user_names(self):
        return [user.username for user in self.users.all()]

    def all_messages(self):
        return self.messages.all()

    def user_count(self):
        return self.users.count()

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    username = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.username}: {self.content}"