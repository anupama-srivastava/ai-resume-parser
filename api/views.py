from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Resume, ParsedResume, JobDescription, MatchResult
from .serializers import (
    ResumeSerializer, ResumeUploadSerializer, ParsedResumeSerializer,
    JobDescriptionSerializer, MatchResultSerializer, ResumeParseRequestSerializer,
    MatchRequestSerializer
)
from .services import ResumeParserService
from .tasks import parse_resume_task, calculate_match_score_task

class ResumeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing resumes.
    """
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Upload a new resume."""
        serializer = ResumeUploadSerializer(data=request.data)
        if serializer.is_valid():
            resume = serializer.save(user=request.user)
            return Response(
                ResumeSerializer(resume).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def parse(self, request, pk=None):
        """Parse a resume using AI."""
        resume = self.get_object()
        parser_service = ResumeParserService()
        
        try:
            # Extract text from file
            file_path = resume.file.path
            file_type = resume.original_filename.split('.')[-1]
            extracted_text = parser_service.extract_text_from_file(file_path, file_type)
            
            # Parse with OpenAI
            parsed_data = parser_service.parse_resume_with_openai(extracted_text)
            
            # Update resume
            resume.extracted_text = extracted_text
            resume.parsed_data = parsed_data
            resume.processing_status = 'completed'
            resume.save()
            
            # Create or update parsed resume
            parsed_resume, created = ParsedResume.objects.get_or_create(
                resume=resume,
                defaults={
                    'personal_info': parsed_data.get('personal_info', {}),
                    'work_experience': parsed_data.get('work_experience', []),
                    'education': parsed_data.get('education', []),
                    'skills': parsed_data.get('skills', {}),
                    'certifications': parsed_data.get('certifications', []),
                    'projects': parsed_data.get('projects', []),
                    'summary': parsed_data.get('summary', ''),
                    'contact_info': parsed_data.get('contact_info', {})
                }
            )
            
            return Response({
                'message': 'Resume parsed successfully',
                'parsed_data': parsed_data
            })
            
        except Exception as e:
            resume.processing_status = 'failed'
            resume.save()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def my_resumes(self, request):
        """Get current user's resumes."""
        resumes = self.get_queryset()
        serializer = self.get_serializer(resumes, many=True)
        return Response(serializer.data)

class JobDescriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job descriptions.
    """
    queryset = JobDescription.objects.all()
    serializer_class = JobDescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobDescription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MatchResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing match results.
    """
    queryset = MatchResult.objects.all()
    serializer_class = MatchResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MatchResult.objects.filter(
            resume__user=self.request.user
        ) | MatchResult.objects.filter(
            job_description__user=self.request.user
        )

    @action(detail=False, methods=['post'])
    def calculate_match(self, request):
        """Calculate match between resume and job description."""
        serializer = MatchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        resume_id = data['resume_id']
        job_description_id = data['job_description_id']
        
        try:
            resume = Resume.objects.get(id=resume_id, user=request.user)
            job_description = JobDescription.objects.get(id=job_description_id, user=request.user)
            
            parser_service = ResumeParserService()
            
            # Get parsed resume data
            parsed_resume = ParsedResume.objects.get(resume=resume)
            resume_data = {
                'skills': parsed_resume.skills,
                'work_experience': parsed_resume.work_experience,
                'education': parsed_resume.education
            }
            
            job_data = {
                'skills_required': job_description.skills_required,
                'experience_required': job_description.experience_required
            }
            
            # Calculate match
            match_result = parser_service.calculate_match_score(resume_data, job_data)
            
            # Save match result
            match = MatchResult.objects.create(
                resume=resume,
                job_description=job_description,
                match_score=match_result['match_score'],
                matched_skills=match_result['matched_skills'],
                missing_skills=match_result['missing_skills'],
                experience_match=match_result['experience_match'],
                summary=f"Match score: {match_result['match_score']}%"
            )
            
            return Response(MatchResultSerializer(match).data)
            
        except Resume.DoesNotExist:
            return Response(
                {'error': 'Resume not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except JobDescription.DoesNotExist:
            return Response(
                {'error': 'Job description not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ParsedResume.DoesNotExist:
            return Response(
                {'error': 'Resume not parsed yet. Please parse the resume first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
