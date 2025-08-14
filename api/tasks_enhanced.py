from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Resume, ParsedResume, JobDescription, MatchResult, 
    AnalyticsData, CareerInsights, Organization
)
from .services_enhanced import EnhancedAnalyticsService
import logging

logger = logging.getLogger(__name__)

@shared_task
def refresh_analytics_task(user_id, organization_id=None):
    """Background task to refresh analytics data"""
    try:
        user = User.objects.get(id=user_id)
        analytics_service = EnhancedAnalyticsService()
        
        # Refresh skills gap analysis
        skills_gap = analytics_service.calculate_skills_gap_analysis(user_id, organization_id)
        AnalyticsData.objects.update_or_create(
            user=user,
            organization_id=organization_id,
            data_type='skills_gap',
            defaults={
                'data': skills_gap,
                'updated_at': timezone.now()
            }
        )
        
        # Refresh career trajectory analysis
        career_trajectory = analytics_service.analyze_career_trajectory(user_id, organization_id)
        AnalyticsData.objects.update_or_create(
            user=user,
            organization_id=organization_id,
            data_type='career_trajectory',
            defaults={
                'data': career_trajectory,
                'updated_at': timezone.now()
            }
        )
        
        # Refresh industry trends
        industry_trends = analytics_service.get_industry_trends(user_id, organization_id)
        AnalyticsData.objects.update_or_create(
            user=user,
            organization_id=organization_id,
            data_type='industry_trends',
            defaults={
                'data': industry_trends,
                'updated_at': timezone.now()
            }
        )
        
        # Refresh salary insights
        salary_insights = analytics_service.get_salary_insights(user_id, organization_id)
        AnalyticsData.objects.update_or_create(
            user=user,
            organization_id=organization_id,
            data_type='salary_insights',
            defaults={
                'data': salary_insights,
                'updated_at': timezone.now()
            }
        )
        
        # Generate career insights
        generate_career_insights(user_id, organization_id)
        
        logger.info(f"Analytics refreshed for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error refreshing analytics: {str(e)}")
        return False

@shared_task
def generate_career_insights(user_id, organization_id=None):
    """Generate personalized career insights"""
    try:
        user = User.objects.get(id=user_id)
        analytics_service = EnhancedAnalyticsService()
        
        # Get latest analytics
        skills_gap = analytics_service.calculate_skills_gap_analysis(user_id, organization_id)
        career_trajectory = analytics_service.analyze_career_trajectory(user_id, organization_id)
        salary_insights = analytics_service.get_salary_insights(user_id, organization_id)
        
        # Generate skill recommendations
        if skills_gap.get('missing_skills'):
            for skill in skills_gap['missing_skills'][:3]:
                CareerInsights.objects.create(
                    user=user,
                    resume=Resume.objects.filter(user=user).first(),
                    insight_type='skill_recommendation',
                    title=f"Learn {skill}",
                    description=f"Based on market trends, learning {skill} could increase your market value by ${skills_gap.get('skill_scores', {}).get(skill, {}).get('salary_impact', 0)}",
                    data={'skill': skill, 'market_impact': skills_gap.get('skill_scores', {}).get(skill, {})},
                    confidence_score=0.85
                )
        
        # Generate role recommendations
        if career_trajectory.get('next_roles'):
            for role in career_trajectory['next_roles'][:2]:
                CareerInsights.objects.create(
                    user=user,
                    resume=Resume.objects.filter(user=user).first(),
                    insight_type='role_recommendation',
                    title=f"Consider {role['predicted_role']}",
                    description=f"Based on your career trajectory, you could be ready for {role['predicted_role']} in {role['timeline']}",
                    data=role,
                    confidence_score=role.get('probability', 0.75)
                )
        
        # Generate salary recommendations
        if salary_insights.get('recommendations'):
            for rec in salary_insights['recommendations'][:2]:
                CareerInsights.objects.create(
                    user=user,
                    resume=Resume.objects.filter(user=user).first(),
                    insight_type='salary_recommendation',
                    title=rec.get('title', 'Salary Insight'),
                    description=rec.get('description', 'Based on market analysis'),
                    data=rec,
                    confidence_score=0.80
                )
        
        logger.info(f"Career insights generated for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating career insights: {str(e)}")
        return False

@shared_task
def update_team_analytics(organization_id):
    """Update team-level analytics"""
    try:
        from .services_enhanced import EnhancedAnalyticsService
        
        analytics_service = EnhancedAnalyticsService()
        
        # Get all team members
        organization = Organization.objects.get(id=organization_id)
        team_members = organization.members.all()
        
        # Calculate team analytics
        team_analytics = {
            'skills_distribution': {},
            'experience_distribution': {},
            'salary_benchmarks': {},
            'collaboration_metrics': {},
            'updated_at': timezone.now().isoformat()
        }
        
        # Save team analytics
        AnalyticsData.objects.update_or_create(
            user=organization.members.first().user,  # Use first member as owner
            organization=organization,
            data_type='team_analytics',
            defaults={
                'data': team_analytics,
                'updated_at': timezone.now()
            }
        )
        
        logger.info(f"Team analytics updated for organization {organization_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating team analytics: {str(e)}")
        return False

@shared_task
def process_market_data():
    """Process and update market data from external sources"""
    try:
        # This would integrate with real APIs
        # For now, we'll just log the process
        logger.info("Processing market data...")
        
        # Update trending skills cache
        # Update salary benchmarks
        # Update industry trends
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing market data: {str(e)}")
        return False

@shared_task
def cleanup_old_analytics():
    """Clean up old analytics data"""
    try:
        # Remove analytics older than 90 days
        cutoff_date = timezone.now() - timedelta(days=90)
        
        old_analytics = AnalyticsData.objects.filter(
            updated_at__lt=cutoff_date
        )
        
        deleted_count = old_analytics.count()
        old_analytics.delete()
        
        logger.info(f"Cleaned up {deleted_count} old analytics records")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up old analytics: {str(e)}")
        return 0
