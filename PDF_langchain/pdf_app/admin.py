# admin.py
from django.contrib import admin
from .models import PDF

@admin.register(PDF)
class PDFAdmin(admin.ModelAdmin):
    list_display = ('name', 'pdf_file')
