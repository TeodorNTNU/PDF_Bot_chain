# models.py
from django.db import models

class PDF(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Ensure 'name' is unique
    pdf_file = models.FileField(upload_to='pdfs/')

    def __str__(self):
        return self.name

class ChatMessage(models.Model):
    session_id = models.CharField(max_length=255)  # Unique session identifier
    sender = models.CharField(max_length=50)  # Sender of the message, e.g., 'user' or 'bot'
    message = models.TextField()  # Message content
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp of when the message was created

    def __str__(self):
        return f"[{self.timestamp}] {self.sender}: {self.content[:50]}"



class Item(models.Model):

    name = models.CharField(max_length=100)
    description = models.TextField()

