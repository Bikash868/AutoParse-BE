from django.contrib import admin
from .models import Candidate
# Register your models here.

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'employer', 'created_at', 'updated_at']
    list_filter = ['employer', 'created_at', 'updated_at']
    search_fields = ['name', 'email', 'phone']
    ordering = ['-created_at']