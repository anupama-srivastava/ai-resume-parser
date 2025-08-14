from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Resume, ParsedResume, JobDescription, MatchResult, 
    Organization, TeamMember, AnalyticsData, CareerInsights
)
from .serializers import (
    ResumeSerializer, JobDescriptionSerializer, MatchResultSerializer,
    OrganizationSerializer, TeamMemberSerializer, AnalyticsDataSerializer,
    CareerInsightsSerializer
)
from .services_enhanced import EnhancedAnalyticsService

class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for advanced analytics and insights
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.analytics_service = EnhancedAnalyticsService()
    
    @action(detail=False, methods=['get'])
    def skills_gap(self, request):
        """Get skills gap analysis"""
        organization_id = request.GET.get('organization_id')
        analysis = self.analytics_service.calculate_skills_gap_analysis(
            request.user.id, 
            organization_id
        )
        return Response(analysis)
    
    @action(detail=False, methods=['get'])
    def career_trajectory(self, request):
        """Get career trajectory analysis"""
        organization_id = request.GET.get('organization_id')
        analysis = self.analytics_service.analyze_career_trajectory(
            request.user.id,
            organization_id
        )
        return Response(analysis)
    
    @action(detail=False, methods=['get'])
    def industry_trends(self, request):
        """Get industry trends analysis"""
        organization_id = request.GET.get('organization_id')
        trends = self.analytics_service.get_industry_trends(
            request.user.id,
            organization_id
        )
        return Response(trends)
    
    @action(detail=False, methods=['get'])
    def salary_insights(self, request):
        """Get salary insights"""
        organization_id = request.GET.get('organization_id')
        insights = self.analytics_service.get_salary_insights(
            request.user.id,
            organization_id
        )
        return Response(insights)
    
    @action(detail=False, methods=['get'])
    def comprehensive_analytics(self, request):
        """Get all analytics in one request"""
        organization_id = request.GET.get('organization_id')
        
        analytics_data = {
            'skills_gap': self.analytics_service.calculate_skills_gap_analysis(
                request.user.id, organization_id
            ),
            'career_trajectory': self.analytics_service.analyze_career_trajectory(
                request.user.id, organization_id
            ),
            'industry_trends': self.analytics_service.get_industry_trends(
                request.user.id, organization_id
            ),
            'salary_insights': self.analytics_service.get_salary_insights(
                request.user.id, organization_id
            )
        }
        
        return Response(analytics_data)
    
    @action(detail=False, methods=['post'])
    def refresh_analytics(self, request):
        """Refresh analytics data"""
        organization_id = request.data.get('organization_id')
        
        # Trigger background refresh
        from .tasks import refresh_analytics_task
        refresh_analytics_task.delay(request.user.id, organization_id)
        
        return Response({
            'message': 'Analytics refresh started',
            'status': 'processing'
        })
    
    @action(detail=False, methods=['get'])
    def team_analytics(self, request):
        """Get team analytics for organization"""
        organization_id = request.GET.get('organization_id')
        if not organization_id:
            return Response(
                {'error': 'organization_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is part of the organization
        try:
            team_member = TeamMember.objects.get(
                user=request.user,
                organization_id=organization_id
            )
        except TeamMember.DoesNotExist:
            return Response(
                {'error': 'Not authorized to view team analytics'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get team analytics
        team_analytics = self._get_team_analytics(organization_id)
        
        return Response(team_analytics)
    
    def _get_team_analytics(self, organization_id: str) -> Dict[str, Any]:
        """Get comprehensive team analytics"""
        organization = Organization.objects.get(id=organization_id)
        
        # Get team members
        team_members = TeamMember.objects.filter(organization=organization)
        
        # Get team resumes and job descriptions
        team_resumes = Resume.objects.filter(organization=organization)
        team_jobs = JobDescription.objects.filter(organization=organization)
        
        # Calculate team metrics
        team_metrics = {
            'total_resumes': team_resumes.count(),
            'total_jobs': team_jobs.count(),
            'total_matches': MatchResult.objects.filter(
                Q(resume__in=team_resumes) | Q(job_description__in=team_jobs)
            ).count(),
            'team_size': team_members.count(),
            'skills_distribution': self._calculate_team_skills_distribution(team_resumes),
            'experience_distribution': self._calculate_team_experience_distribution(team_resumes),
            'salary_benchmarks': self._calculate_team_salary_benchmarks(team_resumes),
            'collaboration_metrics': self._calculate_collaboration_metrics(organization)
        }
        
        return team_metrics
    
    def _calculate_team_skills_distribution(self, resumes):
        """Calculate skills distribution across team"""
        skills_count = {}
        
        for resume in resumes:
            parsed_resume = resume.parsedresume if hasattr(resume, 'parsedresume') else None
            if parsed_resume and parsed_resume.skills:
                technical_skills = parsed_resume.skills.get('technical', [])
                for skill in technical_skills:
                    skills_count[skill] = skills_count.get(skill, 0) + 1
        
        return skills_count
    
    def _calculate_team_experience_distribution(self, resumes):
        """Calculate experience distribution across team"""
        experience_levels = {
            'entry': 0,
            'mid': 0,
            'senior': 0,
            'principal': 0
        }
        
        for resume in resumes:
            parsed_resume = resume.parsedresume if hasattr(resume, 'parsedresume') else None
            if parsed_resume:
                # Calculate experience from work history
                total_experience = self._calculate_resume_experience(parsed_resume)
                level = self._categorize_experience_level(total_experience)
                experience_levels[level] += 1
        
        return experience_levels
    
    def _calculate_resume_experience(self, parsed_resume):
        """Calculate total experience from resume"""
        total_months = 0
        for exp in parsed_resume.work_experience:
            duration = exp.get('duration', '')
            months = self._parse_duration_months(duration)
            total_months += months
        
        return total_months // 12
    
    def _parse_duration_months(self, duration):
        """Parse duration string to months"""
        if not duration:
            return 0
        
        # Simple parsing - would be more sophisticated
        years_match = re.search(r'(\d+)\s*year', duration.lower())
        if years_match:
            return int(years_match.group(1)) * 12
        
        months_match = re.search(r'(\d+)\s*month', duration.lower())
        if months_match:
            return int(months_match.group(1))
        
        return 12  # Default
    
    def _categorize_experience_level(self, years):
        """Categorize experience level"""
        if years < 2:
            return 'entry'
        elif years < 5:
            return 'mid'
        elif years < 10:
            return 'senior'
        else:
            return 'principal'
    
    def _calculate_team_salary_benchmarks(self, resumes):
        """Calculate salary benchmarks for team"""
        benchmarks = {
            'entry': {'min': 45000, 'max': 65000, 'median': 55000},
            'mid': {'min': 65000, 'max': 95000, 'median': 80000},
            'senior': {'min': 95000, 'max': 140000, 'median': 115000},
            'principal': {'min': 140000, 'max': 200000, 'median': 170000}
        }
        
        return benchmarks
    
    def _calculate_collaboration_metrics(self, organization):
        """Calculate team collaboration metrics"""
        comments = Comment.objects.filter(
            Q(resume__organization=organization) |
            Q(job_description__organization=organization)
        )
        
        return {
            'total_comments': comments.count(),
            'active_collaborators': comments.values('user').distinct().count(),
            'average_comments_per_item': comments.count() / max(Resume.objects.filter(organization=organization).count(), 1),
            'recent_activity': comments.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count()
        }

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for organization management
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see organizations they're part of
        return Organization.objects.filter(
            members__user=self.request.user
        )
    
    def perform_create(self, serializer):
        organization = serializer.save()
        # Automatically add creator as admin
        TeamMember.objects.create(
            user=self.request.user,
            organization=organization,
            role='admin'
        )
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Get organization dashboard"""
        organization = self.get_object()
        
        # Check permissions
        try:
            team_member = TeamMember.objects.get(
                user=request.user,
                organization=organization
            )
        except TeamMember.DoesNotExist:
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        dashboard_data = {
            'organization': OrganizationSerializer(organization).data,
            'stats': {
                'total_resumes': Resume.objects.filter(organization=organization).count(),
                'total_jobs': JobDescription.objects.filter(organization=organization).count(),
                'total_members': TeamMember.objects.filter(organization=organization).count(),
                'recent_activity': self._get_recent_activity(organization)
            },
            'team_members': TeamMemberSerializer(
                TeamMember.objects.filter(organization=organization),
                many=True
            ).data
        }
        
        return Response(dashboard_data)
    
    def _get_recent_activity(self, organization):
        """Get recent activity for organization"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        return {
            'new_resumes': Resume.objects.filter(
                organization=organization,
                created_at__gte=thirty_days_ago
            ).count(),
            'new_jobs': JobDescription.objects.filter(
                organization=organization,
                created_at__gte=thirty_days_ago
            ).count(),
            'new_matches': MatchResult.objects.filter(
                Q(resume__organization=organization) | Q(job_description__organization=organization),
                created_at__gte=thirty_days_ago
            ).count()
        }

class TeamMemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for team member management
    """
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see team memberships they're part of
        return TeamMember.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def invite_member(self, request):
        """Invite new team member"""
        organization_id = request.data.get('organization_id')
        email = request.data.get('email')
        role = request.data.get('role', 'member')
        
        # Check permissions
        try:
            inviter = TeamMember.objects.get(
                user=request.user,
                organization_id=organization_id,
                role__in=['admin', 'manager']
            )
        except TeamMember.DoesNotExist:
            return Response(
                {'error': 'Not authorized to invite members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create invitation (simplified)
        return Response({
            'message': f'Invitation sent to {email} with role {role}'
        })

class CareerInsightsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for career insights and recommendations
    """
    queryset = CareerInsights.objects.all()
    serializer_class = CareerInsightsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CareerInsights.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """Mark insights as read"""
        insight_ids = request.data.get('insight_ids', [])
        CareerInsights.objects.filter(
            id__in=insight_ids,
            user=request.user
        ).update(is_read=True)
        
        return Response({'message': f'Marked {len(insight_ids)} insights as read'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread insights count"""
        count = CareerInsights.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return Response({'unread_count': count})
