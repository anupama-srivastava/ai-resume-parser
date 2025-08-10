from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Resume, ParsedResume, JobDescription, MatchResult

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ResumeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Resume
        fields = ['id', 'user', 'file', 'original_filename', 'parsed_data', 
                 'extracted_text', 'processing_status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'parsed_data', 'extracted_text', 
                          'processing_status', 'created_at', 'updated_at']

class ResumeUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['file']
    
    def validate_file(self, value):
        if value.size > 5 * 1024 * 1024:  # 5MB
            raise serializers.ValidationError("File size must be under 5MB")
        
        allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Only PDF, DOCX, and TXT files are allowed")
        
        return value

class ParsedResumeSerializer(serializers.ModelSerializer):
    resume = ResumeSerializer(read_only=True)
    
    class Meta:
        model = ParsedResume
        fields = '__all__'

class JobDescriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = JobDescription
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at']

class MatchResultSerializer(serializers.ModelSerializer):
    resume = ResumeSerializer(read_only=True)
    job_description = JobDescriptionSerializer(read_only=True)
    
    class Meta:
        model = MatchResult
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

class ResumeParseRequestSerializer(serializers.Serializer):
    resume_id = serializers.UUIDField()

class MatchRequestSerializer(serializers.Serializer):
    resume_id = serializers.UUIDField()
    job_description_id = serializers.UUIDField()
