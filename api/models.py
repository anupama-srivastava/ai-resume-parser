from django.db import models
from django.contrib.auth.models import User
import uuid

class Resume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/')
    original_filename = models.CharField(max_length=255)
    parsed_data = models.JSONField(default=dict, blank=True)
    extracted_text = models.TextField(blank=True)
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.original_filename} - {self.user.username}"

class ParsedResume(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='parsed_resume')
    personal_info = models.JSONField(default=dict)
    work_experience = models.JSONField(default=list)
    education = models.JSONField(default=list)
    skills = models.JSONField(default=list)
    certifications = models.JSONField(default=list)
    projects = models.JSONField(default=list)
    summary = models.TextField(blank=True)
    contact_info = models.JSONField(default=dict)
    parsed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Parsed Resume: {self.resume.original_filename}"

class JobDescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_descriptions')
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.JSONField(default=list)
    skills_required = models.JSONField(default=list)
    experience_required = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class MatchResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='matches')
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='matches')
    match_score = models.FloatField()
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    experience_match = models.JSONField(default=dict)
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-match_score']
    
    def __str__(self):
        return f"Match: {self.resume.original_filename} - {self.job_description.title} ({self.match_score}%)"
