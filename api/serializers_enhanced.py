from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Resume, ParsedResume, JobDescription, MatchResult,
    Organization, TeamMember, AnalyticsData, CareerInsights, Comment
)

class UserSerializer(serializers.ModelSerializer):
    """Enhanced user serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class OrganizationSerializer(serializers.ModelSerializer):
    """Organization serializer for multi-tenant support"""
    member_count = serializers.SerializerMethodField()
    total_resumes = serializers.SerializerMethodField()
    total_jobs = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'logo', 'primary_color', 'secondary_color',
            'custom_domain', 'member_count', 'total_resumes', 'total_jobs',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.filter(is_active=True).count()
    
    def get_total_resumes(self, obj):
        return obj.resumes.count()
    
    def get_total_jobs(self, obj):
        return obj.job_descriptions.count()

class TeamMemberSerializer(serializers.ModelSerializer):
    """Team member serializer for collaboration"""
    user = UserSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source='organization',
        write_only=True
    )
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'user', 'organization', 'role', 'is_active',
            'joined_at', 'user_id', 'organization_id'
        ]
        read_only_fields = ['id', 'joined_at']

class ResumeEnhancedSerializer(serializers.ModelSerializer):
    """Enhanced resume serializer with organization support"""
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source='organization',
        write_only=True,
        required=False,
        allow_null=True
    )
    shared_with = UserSerializer(many=True, read_only=True)
    shared_with_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False
    )
    
    class Meta:
        model = Resume
        fields = [
            'id', 'user', 'organization', 'organization_id', 'file',
            'original_filename', 'file_size', 'parsed_data', 'extracted_text',
            'processing_status', 'is_shared', 'shared_with', 'shared_with_ids',
            'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class JobDescriptionEnhancedSerializer(serializers.ModelSerializer):
    """Enhanced job description serializer with organization support"""
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source='organization',
        write_only=True,
        required=False,
        allow_null=True
    )
    shared_with = UserSerializer(many=True, read_only=True)
    shared_with_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False
    )
    salary_range = serializers.JSONField(required=False)
    
    class Meta:
        model = JobDescription
        fields = [
            'id', 'user', 'organization', 'organization_id', 'title',
            'description', 'requirements', 'skills_required',
            'experience_required', 'salary_range', 'location',
            'employment_type', 'is_shared', 'shared_with', 'shared_with_ids',
            'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class MatchResultEnhancedSerializer(serializers.ModelSerializer):
    """Enhanced match result serializer with additional fields"""
    resume = ResumeEnhancedSerializer(read_only=True)
    job_description = JobDescriptionEnhancedSerializer(read_only=True)
    cultural_fit_score = serializers.FloatField(read_only=True)
    salary_match_score = serializers.FloatField(read_only=True)
    
    class Meta:
        model = MatchResult
        fields = [
            'id', 'resume', 'job_description', 'match_score',
            'matched_skills', 'missing_skills', 'experience_match',
            'cultural_fit_score', 'salary_match_score', 'summary',
            'notes', 'is_favorite', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class AnalyticsDataSerializer(serializers.ModelSerializer):
    """Analytics data serializer"""
    organization = OrganizationSerializer(read_only=True)
    
    class Meta:
        model = AnalyticsData
        fields = [
            'id', 'organization', 'user', 'data_type', 'data',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class CareerInsightsSerializer(serializers.ModelSerializer):
    """Career insights serializer"""
    resume = ResumeEnhancedSerializer(read_only=True)
    
    class Meta:
        model = CareerInsights
        fields = [
            'id', 'user', 'resume', 'insight_type', 'title',
            'description', 'data', 'confidence_score', 'is_read',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    """Comment serializer for collaboration"""
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'resume', 'job_description', 'match_result',
            'content', 'parent', 'replies', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_replies(self, obj):
        """Get nested replies"""
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

# Enhanced serializers for analytics responses
class SkillsGapAnalysisSerializer(serializers.Serializer):
    """Skills gap analysis response serializer"""
    current_skills = serializers.DictField()
    trending_skills = serializers.DictField()
    missing_skills = serializers.ListField(child=serializers.CharField())
    existing_skills = serializers.ListField(child=serializers.CharField())
    skill_scores = serializers.DictField()
    gap_percentage = serializers.FloatField()
    priority_skills = serializers.ListField()
    learning_path = serializers.ListField()
    market_impact = serializers.DictField()

class CareerTrajectorySerializer(serializers.Serializer):
    """Career trajectory analysis response serializer"""
    work_experiences = serializers.ListField()
    career_progression = serializers.ListField()
    future_predictions = serializers.ListField()
    skill_evolution = serializers.ListField()
    industry_transitions = serializers.ListField()
    current_level = serializers.CharField()
    next_roles = serializers.ListField()
    salary_progression = serializers.ListField()
    skill_gaps = serializers.ListField()
    recommendations = serializers.ListField()

class IndustryTrendsSerializer(serializers.Serializer):
    """Industry trends response serializer"""
    skills_trends = serializers.ListField()
    role_trends = serializers.ListField()
    experience_trends = serializers.ListField()
    salary_trends = serializers.ListField()
    industry_growth = serializers.DictField()
    tech_trends = serializers.ListField()
    market_demand = serializers.DictField()
    emerging_technologies = serializers.ListField()
    regional_trends = serializers.DictField()
    company_size_trends = serializers.DictField()

class SalaryInsightsSerializer(serializers.Serializer):
    """Salary insights response serializer"""
    current_experience = serializers.IntegerField()
    current_skills = serializers.ListField()
    salary_benchmarks = serializers.ListField()
    market_value = serializers.DictField()
    location_salary = serializers.DictField()
    company_size_salary = serializers.DictField()
    skill_premiums = serializers.DictField()
    negotiation_leverage = serializers.DictField()
    career_stage_salary = serializers.DictField()
    industry_comparison = serializers.DictField()
    recommendations = serializers.ListField()

class TeamAnalyticsSerializer(serializers.Serializer):
    """Team analytics response serializer"""
    total_resumes = serializers.IntegerField()
    total_jobs = serializers.IntegerField()
    total_matches = serializers.IntegerField()
    team_size = serializers.IntegerField()
    skills_distribution = serializers.DictField()
    experience_distribution = serializers.DictField()
    salary_benchmarks = serializers.DictField()
    collaboration_metrics = serializers.DictField()
