from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Resume, ParsedResume, JobDescription, MatchResult, Organization, TeamMember
import json

class EnhancedAnalyticsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        
        # Create test organization
        self.organization = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
        
        # Create team member
        self.team_member = TeamMember.objects.create(
            user=self.user,
            organization=self.organization,
            role='admin'
        )
        
        # Create test resume
        self.resume = Resume.objects.create(
            user=self.user,
            organization=self.organization,
            original_filename='test_resume.pdf',
            file_size=1024,
            parsed_data={'skills': ['Python', 'Django']}
        )
        
        # Create parsed resume
        self.parsed_resume = ParsedResume.objects.create(
            resume=self.resume,
            skills={'technical': ['Python', 'Django', 'React']},
            work_experience=[{
                'company': 'Test Company',
                'position': 'Software Engineer',
                'duration': '2 years',
                'description': 'Worked on Python and Django projects'
            }]
        )
        
        # Create test job description
        self.job = JobDescription.objects.create(
            user=self.user,
            organization=self.organization,
            title='Senior Python Developer',
            description='Looking for experienced Python developer',
            skills_required=['Python', 'Django', 'AWS'],
            experience_required='3+ years'
        )
        
        # Create match result
        self.match = MatchResult.objects.create(
            resume=self.resume,
            job_description=self.job,
            match_score=85.5,
            matched_skills=['Python', 'Django'],
            missing_skills=['AWS'],
            summary='Good match for Python developer role'
        )

    def test_skills_gap_analysis(self):
        response = self.client.get('/api/v2/analytics/skills_gap/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('current_skills', data)
        self.assertIn('missing_skills', data)
        self.assertIn('gap_percentage', data)

    def test_career_trajectory_analysis(self):
        response = self.client.get('/api/v2/analytics/career_trajectory/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('work_experiences', data)
        self.assertIn('career_progression', data)
        self.assertIn('next_roles', data)

    def test_industry_trends(self):
        response = self.client.get('/api/v2/analytics/industry_trends/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('skills_trends', data)
        self.assertIn('role_trends', data)

    def test_salary_insights(self):
        response = self.client.get('/api/v2/analytics/salary_insights/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('current_experience', data)
        self.assertIn('salary_benchmarks', data)
        self.assertIn('market_value', data)

    def test_comprehensive_analytics(self):
        response = self.client.get('/api/v2/analytics/comprehensive_analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('skills_gap', data)
        self.assertIn('career_trajectory', data)
        self.assertIn('industry_trends', data)
        self.assertIn('salary_insights', data)

    def test_team_analytics(self):
        response = self.client.get(f'/api/v2/analytics/team_analytics/?organization_id={self.organization.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('total_resumes', data)
        self.assertIn('total_jobs', data)
        self.assertIn('team_size', data)

    def test_organization_dashboard(self):
        response = self.client.get(f'/api/v2/organizations/{self.organization.id}/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('organization', data)
        self.assertIn('stats', data)
        self.assertIn('team_members', data)

    def test_refresh_analytics(self):
        response = self.client.post('/api/v2/analytics/refresh_analytics/', {
            'organization_id': str(self.organization.id)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('message', data)
        self.assertEqual(data['status'], 'processing')
