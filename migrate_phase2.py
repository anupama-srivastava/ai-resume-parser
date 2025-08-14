#!/usr/bin/env python
"""
Phase 2 Migration Script
This script updates the database schema to support Phase 2 features:
- Multi-tenant support with Organization model
- Team collaboration features
- Enhanced analytics capabilities
- Advanced insights and recommendations
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume_parser.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from api.models import Resume, ParsedResume, JobDescription, MatchResult
from api.models_enhanced import (
    Organization, TeamMember, AnalyticsData, CareerInsights, Comment
)
import uuid

def create_default_organization():
    """Create default organization for existing users"""
    print("Creating default organizations...")
    
    for user in User.objects.all():
        # Create personal organization for each user
        org, created = Organization.objects.get_or_create(
            name=f"{user.username}'s Organization",
            defaults={
                'slug': f"{user.username}-org",
                'primary_color': '#1976d2',
                'secondary_color': '#dc004e'
            }
        )
        
        # Add user as admin
        TeamMember.objects.get_or_create(
            user=user,
            organization=org,
            defaults={'role': 'admin'}
        )
        
        # Update existing resumes and job descriptions
        Resume.objects.filter(user=user).update(organization=org)
        JobDescription.objects.filter(user=user).update(organization=org)
        
        print(f"Created organization for {user.username}")

def migrate_existing_data():
    """Migrate existing data to new schema"""
    print("Migrating existing data...")
    
    # Update resume file sizes
    for resume in Resume.objects.all():
        if resume.file and hasattr(resume.file, 'size'):
            resume.file_size = resume.file.size
            resume.save()
    
    # Update skills structure in ParsedResume
    for parsed_resume in ParsedResume.objects.all():
        if isinstance(parsed_resume.skills, list):
            parsed_resume.skills = {
                'technical': parsed_resume.skills,
                'soft': [],
                'languages': []
            }
            parsed_resume.save()
    
    print("Data migration completed")

def create_sample_analytics():
    """Create sample analytics data for demonstration"""
    print("Creating sample analytics data...")
    
    for user in User.objects.all():
        # Create sample skills gap analysis
        AnalyticsData.objects.get_or_create(
            user=user,
            data_type='skills_gap',
            defaults={
                'data': {
                    'current_skills': ['Python', 'JavaScript', 'React'],
                    'trending_skills': {
                        'Python': {'demand': 9500, 'relevance': 0.95, 'salary_impact': 15000},
                        'React': {'demand': 8200, 'relevance': 0.92, 'salary_impact': 12000},
                        'AWS': {'demand': 7800, 'relevance': 0.90, 'salary_impact': 18000}
                    },
                    'missing_skills': ['Docker', 'Kubernetes', 'Machine Learning'],
                    'gap_percentage': 25.5
                }
            }
        )
        
        # Create sample career insights
        CareerInsights.objects.get_or_create(
            user=user,
            insight_type='skill_recommendation',
            title='Learn Docker for DevOps',
            defaults={
                'description': 'Docker is in high demand with 15% salary premium',
                'data': {'skill': 'Docker', 'salary_impact': 10000},
                'confidence_score': 0.85
            }
        )
    
    print("Sample analytics data created")

def setup_team_collaboration():
    """Setup team collaboration features"""
    print("Setting up team collaboration...")
    
    # Create sample comments
    for resume in Resume.objects.all()[:5]:
        Comment.objects.get_or_create(
            user=resume.user,
            resume=resume,
            content="Great resume! Consider adding more details about your projects.",
            defaults={'created_at': resume.created_at}
        )
    
    print("Team collaboration setup completed")

def main():
    """Main migration function"""
    print("Starting Phase 2 migration...")
    
    try:
        with transaction.atomic():
            create_default_organization()
            migrate_existing_data()
            create_sample_analytics()
            setup_team_collaboration()
            
            print("\nPhase 2 migration completed successfully!")
            print("\nNext steps:")
            print("1. Run: python manage.py makemigrations")
            print("2. Run: python manage.py migrate")
            print("3. Run: python manage.py collectstatic")
            print("4. Start the development server")
            
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
