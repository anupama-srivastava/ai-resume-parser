from django.db import models
from django.contrib.auth.models import User
import uuid

# Organization model for multi-tenant support
class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#1976d2')
    secondary_color = models.CharField(max_length=7, default='#dc004e')
    custom_domain = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

# Team member model for collaboration features
class TeamMember(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('member', 'Member'),
        ('viewer', 'Viewer')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'organization']
    
    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"

# Enhanced Resume model with organization support
class Resume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='resumes', null=True, blank=True)
    file = models.FileField(upload_to='resumes/')
    original_filename = models.CharField(max_length=255)
    file_size = models.IntegerField(default=0)
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
    is_shared = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(User, related_name='shared_resumes', blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.original_filename} - {self.user.username}"

# Enhanced ParsedResume model
class ParsedResume(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='parsed_resume')
    personal_info = models.JSONField(default=dict)
    work_experience = models.JSONField(default=list)
    education = models.JSONField(default=list)
    skills = models.JSONField(default=dict)
    certifications = models.JSONField(default=list)
    projects = models.JSONField(default=list)
    summary = models.TextField(blank=True)
    contact_info = models.JSONField(default=dict)
    parsed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Parsed Resume: {self.resume.original_filename}"

# Enhanced JobDescription model
class JobDescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_descriptions')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='job_descriptions', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.JSONField(default=list)
    skills_required = models.JSONField(default=list)
    experience_required = models.CharField(max_length=100, blank=True)
    salary_range = models.JSONField(default=dict, blank=True)
    location = models.CharField(max_length=255, blank=True)
    employment_type = models.CharField(max_length=50, choices=[
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship')
    ], default='full-time')
    is_shared = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(User, related_name='shared_jobs', blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

# Enhanced MatchResult model
class MatchResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='matches')
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='matches')
    match_score = models.FloatField()
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    experience_match = models.JSONField(default=dict)
    cultural_fit_score = models.FloatField(default=0.0)
    salary_match_score = models.FloatField(default=0.0)
    summary = models.TextField()
    notes = models.TextField(blank=True)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-match_score']
    
    def __str__(self):
        return f"Match: {self.resume.original_filename} - {self.job_description.title} ({self.match_score}%)"

# Analytics data storage
class AnalyticsData(models.Model):
    """Store pre-calculated analytics data for performance"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='analytics_data', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_data')
    data_type = models.CharField(max_length=50, choices=[
        ('skills_gap', 'Skills Gap Analysis'),
        ('career_trajectory', 'Career Trajectory'),
        ('industry_trends', 'Industry Trends'),
        ('salary_insights', 'Salary Insights'),
        ('team_analytics', 'Team Analytics')
    ])
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'data_type', 'organization']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.data_type} - {self.user.username}"

# Career insights storage
class CareerInsights(models.Model):
    """Store career insights and recommendations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='career_insights')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='career_insights')
    insight_type = models.CharField(max_length=50, choices=[
        ('skill_recommendation', 'Skill Recommendation'),
        ('role_recommendation', 'Role Recommendation'),
        ('salary_recommendation', 'Salary Recommendation'),
        ('career_path', 'Career Path')
    ])
    title = models.CharField(max_length=255)
    description = models.TextField()
    data = models.JSONField(default=dict)
    confidence_score = models.FloatField(default=0.0)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.insight_type}: {self.title}"

# Comments for collaboration features
class Comment(models.Model):
    """Comments for collaboration features"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    match_result = models.ForeignKey(MatchResult, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username}"
