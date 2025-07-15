from django.db import models

class Message(models.Model):
    room_code = models.CharField(max_length=10)
    username = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.username}: {self.content}"
