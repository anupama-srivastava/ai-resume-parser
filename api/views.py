from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import HttpResponse
import csv
import io
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
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

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get enhanced dashboard statistics."""
        user = request.user
        
        # Basic stats
        total_resumes = Resume.objects.filter(user=user).count()
        total_jobs = JobDescription.objects.filter(user=user).count()
        total_matches = MatchResult.objects.filter(
            Q(resume__user=user) | Q(job_description__user=user)
        ).count()
        
        # Processing stats
        processing_stats = Resume.objects.filter(user=user).aggregate(
            completed=Count('id', filter=Q(processing_status='completed')),
            pending=Count('id', filter=Q(processing_status='pending')),
            failed=Count('id', filter=Q(processing_status='failed')),
        )
        
        success_rate = 0
        if total_resumes > 0:
            success_rate = round((processing_stats['completed'] / total_resumes) * 100)
        
        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        recent_resumes = Resume.objects.filter(
            user=user,
            created_at__gte=thirty_days_ago
        ).extra(
            select={'date': 'date(created_at)'}
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        recent_jobs = JobDescription.objects.filter(
            user=user,
            created_at__gte=thirty_days_ago
        ).extra(
            select={'date': 'date(created_at)'}
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Skills analysis
        skills_data = []
        parsed_resumes = ParsedResume.objects.filter(resume__user=user)
        for parsed in parsed_resumes:
            if parsed.skills:
                skills_data.extend(parsed.skills.get('technical', []))
        
        top_skills = {}
        for skill in skills_data:
            top_skills[skill] = top_skills.get(skill, 0) + 1
        
        top_skills_list = [
            {'skill': skill, 'count': count}
            for skill, count in sorted(top_skills.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # File type distribution
        file_types = Resume.objects.filter(user=user).values(
            'original_filename'
        ).annotate(
            count=Count('id')
        )
        
        file_type_stats = {}
        for ft in file_types:
            ext = ft['original_filename'].split('.')[-1].upper()
            file_type_stats[ext] = file_type_stats.get(ext, 0) + ft['count']
        
        return Response({
            'total_resumes': total_resumes,
            'total_jobs': total_jobs,
            'total_matches': total_matches,
            'success_rate': success_rate,
            'processing_stats': processing_stats,
            'recent_activity': {
                'resumes': list(recent_resumes),
                'jobs': list(recent_jobs),
            },
            'top_skills': top_skills_list,
            'file_types': [
                {'type': k, 'count': v}
                for k, v in file_type_stats.items()
            ],
        })

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search across resumes."""
        user = request.user
        query = request.GET.get('q', '')
        status_filter = request.GET.get('status', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        file_type = request.GET.get('file_type', '')
        
        resumes = Resume.objects.filter(user=user)
        
        if query:
            resumes = resumes.filter(
                Q(original_filename__icontains=query) |
                Q(extracted_text__icontains=query) |
                Q(parsed_data__icontains=query)
            )
        
        if status_filter:
            resumes = resumes.filter(processing_status=status_filter)
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d')
                resumes = resumes.filter(created_at__gte=date_from)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d')
                resumes = resumes.filter(created_at__lte=date_to)
            except ValueError:
                pass
        
        if file_type:
            resumes = resumes.filter(original_filename__endswith=file_type)
        
        serializer = self.get_serializer(resumes.order_by('-created_at'), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Upload multiple resumes at once."""
        files = request.FILES.getlist('files')
        uploaded_resumes = []
        
        for file in files:
            try:
                resume = Resume.objects.create(
                    user=request.user,
                    file=file,
                    original_filename=file.name,
                    file_size=file.size
                )
                uploaded_resumes.append(ResumeSerializer(resume).data)
            except Exception as e:
                continue
        
        return Response({
            'message': f'Uploaded {len(uploaded_resumes)} resumes',
            'resumes': uploaded_resumes
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def bulk_parse(self, request):
        """Parse multiple resumes at once."""
        resume_ids = request.data.get('resume_ids', [])
        parsed_count = 0
        
        for resume_id in resume_ids:
            try:
                resume = Resume.objects.get(id=resume_id, user=request.user)
                if resume.processing_status == 'pending':
                    # Trigger async parsing
                    parse_resume_task.delay(resume.id)
                    parsed_count += 1
            except Resume.DoesNotExist:
                continue
        
        return Response({
            'message': f'Started parsing {parsed_count} resumes',
            'count': parsed_count
        })

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """Delete multiple resumes at once."""
        resume_ids = request.data.get('resume_ids', [])
        deleted_count = Resume.objects.filter(
            id__in=resume_ids,
            user=request.user
        ).delete()[0]
        
        return Response({
            'message': f'Deleted {deleted_count} resumes',
            'count': deleted_count
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export resumes data in various formats."""
        format_type = request.GET.get('format', 'csv')
        resume_ids = request.GET.get('ids', '').split(',') if request.GET.get('ids') else None
        
        resumes = Resume.objects.filter(user=request.user)
        if resume_ids and resume_ids[0]:
            resumes = resumes.filter(id__in=resume_ids)
        
        if format_type == 'csv':
            return self.export_csv(resumes)
        elif format_type == 'excel':
            return self.export_excel(resumes)
        elif format_type == 'pdf':
            return self.export_pdf(resumes)
        else:
            return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)

    def export_csv(self, resumes):
        """Export resumes as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            'Filename', 'Upload Date', 'Status', 'File Size (MB)',
            'Parsed Skills', 'Work Experience Count'
        ])
        
        # Write data
        for resume in resumes:
            parsed_resume = resume.parsedresume if hasattr(resume, 'parsedresume') else None
            skills = ', '.join(parsed_resume.skills.get('technical', [])) if parsed_resume else ''
            experience_count = len(parsed_resume.work_experience) if parsed_resume else 0
            
            writer.writerow([
                resume.original_filename,
                resume.created_at.strftime('%Y-%m-%d %H:%M'),
                resume.processing_status,
                round(resume.file_size / 1024 / 1024, 2),
                skills,
                experience_count
            ])
        
        output.seek(0)
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="resumes_export.csv"'
        return response

    def export_excel(self, resumes):
        """Export resumes as Excel."""
        data = []
        for resume in resumes:
            parsed_resume = resume.parsedresume if hasattr(resume, 'parsedresume') else None
            skills = ', '.join(parsed_resume.skills.get('technical', [])) if parsed_resume else ''
            experience_count = len(parsed_resume.work_experience) if parsed_resume else 0
            
            data.append({
                'Filename': resume.original_filename,
                'Upload Date': resume.created_at,
                'Status': resume.processing_status,
                'File Size (MB)': round(resume.file_size / 1024 / 1024, 2),
                'Skills': skills,
                'Experience Count': experience_count
            })
        
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Resumes')
        
        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="resumes_export.xlsx"'
        return response

    def export_pdf(self, resumes):
        """Export resumes as PDF."""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="resumes_export.pdf"'
        
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter
        
        y_position = height - 50
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y_position, "Resume Export Report")
        y_position -= 30
        
        for resume in resumes:
            if y_position < 100:
                p.showPage()
                y_position = height - 50
            
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y_position, f"File: {resume.original_filename}")
            y_position -= 20
            
            p.setFont("Helvetica", 10)
            p.drawString(50, y_position, f"Upload Date: {resume.created_at.strftime('%Y-%m-%d %H:%M')}")
            y_position -= 15
            p.drawString(50, y_position, f"Status: {resume.processing_status}")
            y_position -= 15
            p.drawString(50, y_position, f"File Size: {round(resume.file_size / 1024 / 1024, 2)} MB")
            y_position -= 30
        
        p.save()
        return response

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
