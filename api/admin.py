from django.contrib import admin
from .models import Resume, ParsedResume, JobDescription, MatchResult

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'user', 'processing_status', 'created_at']
    list_filter = ['processing_status', 'created_at']
    search_fields = ['original_filename', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(ParsedResume)
class ParsedResumeAdmin(admin.ModelAdmin):
    list_display = ['resume', 'parsed_at']
    search_fields = ['resume__original_filename']
    readonly_fields = ['parsed_at']

@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['id', 'created_at']

@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ['resume', 'job_description', 'match_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['resume__original_filename', 'job_description__title']
    readonly_fields = ['id', 'created_at']
