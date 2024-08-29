# models.py
from django.db import models

class PDF(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Ensure 'name' is unique
    pdf_file = models.FileField(upload_to='pdfs/')

    def __str__(self):
        return self.name



class Item(models.Model):

    name = models.CharField(max_length=100)
    description = models.TextField()
