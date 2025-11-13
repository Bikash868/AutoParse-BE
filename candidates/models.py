from django.db import models

# Create your models here.
class Candidate(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    employer = models.CharField(max_length=255, blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    aadhar_card = models.FileField(upload_to='aadhar_cards/', blank=True, null=True)
    pan_card = models.FileField(upload_to='pan_cards/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    # Added default sorting by created_at in descending order
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name or ""