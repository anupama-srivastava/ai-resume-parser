import json
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q, F
from django.contrib.auth.models import User
from .models import Resume, ParsedResume, JobDescription, MatchResult
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class AdvancedAnalyticsService:
    """Advanced analytics service for resume insights and career analysis."""
    
    def __init__(self):
        self.nlp = None  # Will be initialized with spaCy or similar
    
    def calculate_skills_gap_analysis(self, user_id: int) -> Dict[str, Any]:
        """Analyze skills gaps based on industry trends and user profile."""
        try:
            user = User.objects.get(id=user_id)
            
            # Get user's current skills
            user_resumes = ParsedResume.objects.filter(resume__user=user)
            current_skills = []
            for resume in user_resumes:
                if resume.skills:
                    current_skills.extend(resume.skills.get('technical', []))
            
            # Get industry trending skills (mock data - would integrate with real APIs)
            trending_skills = self._get_trending_skills()
            
            # Calculate gaps
            current_skill_set = set(current_skills)
            trending_skill_set = set(trending_skills)
            
            missing_skills = list(trending_skill_set - current_skill_set)
            existing_skills = list(current_skill_set.intersection(trending_skill_set))
            
            # Calculate skill relevance scores
            skill_scores = {}
            for skill in current_skills:
                skill_scores[skill] = self._calculate_skill_relevance(skill, trending_skills)
            
            return {
                'current_skills': list(set(current_skills)),
                'trending_skills': trending_skills,
                'missing_skills': missing_skills,
                'existing_skills': existing_skills,
                'skill_relevance_scores': skill_scores,
                'gap_percentage': (len(missing_skills) / len(trending_skills)) * 100 if trending_skills else 0,
                'recommendations': self._generate_skill_recommendations(missing_skills, existing_skills)
            }
            
        except Exception as e:
            logger.error(f"Error in skills gap analysis: {str(e)}")
            return self._get_default_skills_gap()
    
    def analyze_career_trajectory(self, user_id: int) -> Dict[str, Any]:
        """Analyze career progression and predict future trajectory."""
        try:
            user = User.objects.get(id=user_id)
            user_resumes = ParsedResume.objects.filter(resume__user=user)
            
            # Extract work experience
            work_experiences = []
            for resume in user_resumes:
                experiences = resume.work_experience
                for exp in experiences:
                    work_experiences.append({
                        'company': exp.get('company', ''),
                        'position': exp.get('position', ''),
                        'duration': exp.get('duration', ''),
                        'description': exp.get('description', ''),
                        'start_date': self._parse_duration(exp.get('duration', '')),
                        'skills': resume.skills.get('technical', [])
                    })
            
            # Sort by start date
            work_experiences.sort(key=lambda x: x['start_date'])
            
            # Calculate career progression
            career_progression = self._calculate_career_progression(work_experiences)
            
            # Predict future trajectory
            future_predictions = self._predict_career_trajectory(career_progression)
            
            return {
                'work_experiences': work_experiences,
                'career_progression': career_progression,
                'future_predictions': future_predictions,
                'current_level': self._determine_current_level(work_experiences),
                'next_roles': self._suggest_next_roles(work_experiences),
                'skill_growth': self._analyze_skill_growth(work_experiences)
            }
            
        except Exception as e:
            logger.error(f"Error in career trajectory analysis: {str(e)}")
            return self._get_default_career_trajectory()
    
    def get_industry_trends(self, user_id: int) -> Dict[str, Any]:
        """Get industry trends based on job descriptions and market data."""
        try:
            user = User.objects.get(id=user_id)
            
            # Get user's job descriptions
            job_descriptions = JobDescription.objects.filter(user=user)
            
            # Analyze skills trends
            skills_trends = self._analyze_skills_trends(job_descriptions)
            
            # Analyze role trends
            role_trends = self._analyze_role_trends(job_descriptions)
            
            # Analyze experience requirements
            experience_trends = self._analyze_experience_trends(job_descriptions)
            
            # Get salary trends (mock data - would integrate with real APIs)
            salary_trends = self._get_salary_trends()
            
            return {
                'skills_trends': skills_trends,
                'role_trends': role_trends,
                'experience_trends': experience_trends,
                'salary_trends': salary_trends,
                'market_demand': self._calculate_market_demand(skills_trends),
                'industry_growth': self._calculate_industry_growth(role_trends)
            }
            
        except Exception as e:
            logger.error(f"Error in industry trends analysis: {str(e)}")
            return self._get_default_industry_trends()
    
    def get_salary_insights(self, user_id: int) -> Dict[str, Any]:
        """Get salary insights based on experience and skills."""
        try:
            user = User.objects.get(id=user_id)
            user_resumes = ParsedResume.objects.filter(resume__user=user)
            
            # Calculate total experience
            total_experience = self._calculate_total_experience(user_resumes)
            
            # Get current skills
            current_skills = []
            for resume in user_resumes:
                if resume.skills:
                    current_skills.extend(resume.skills.get('technical', []))
            
            # Get salary benchmarks (mock data - would integrate with real APIs)
            salary_benchmarks = self._get_salary_benchmarks(total_experience, current_skills)
            
            # Calculate market value
            market_value = self._calculate_market_value(total_experience, current_skills)
            
            return {
                'current_experience': total_experience,
                'current_skills': list(set(current_skills)),
                'salary_benchmarks': salary_benchmarks,
                'market_value': market_value,
                'skill_impact': self._calculate_skill_impact(current_skills),
                'experience_impact': self._calculate_experience_impact(total_experience),
                'recommendations': self._generate_salary_recommendations(total_experience, current_skills)
            }
            
        except Exception as e:
            logger.error(f"Error in salary insights: {str(e)}")
            return self._get_default_salary_insights()
    
    def _get_trending_skills(self) -> List[str]:
        """Get trending skills from industry data."""
        # Mock data - would integrate with real APIs like LinkedIn, Indeed, etc.
        return [
            'Python', 'React', 'Node.js', 'AWS', 'Docker', 'Kubernetes',
            'Machine Learning', 'Data Science', 'DevOps', 'GraphQL',
            'TypeScript', 'Microservices', 'CI/CD', 'Terraform', 'PostgreSQL'
        ]
    
    def _calculate_skill_relevance(self, skill: str, trending_skills: List[str]) -> float:
        """Calculate relevance score for a skill."""
        if skill in trending_skills:
            return 1.0
        # Simple similarity check - could be enhanced with NLP
        for trending in trending_skills:
            if skill.lower() in trending.lower() or trending.lower() in skill.lower():
                return 0.7
        return 0.3
    
    def _generate_skill_recommendations(self, missing_skills: List[str], existing_skills: List[str]) -> List[str]:
        """Generate personalized skill recommendations."""
        recommendations = []
        
        # Prioritize missing skills based on market demand
        high_priority = ['Python', 'React', 'AWS', 'Machine Learning', 'Docker']
        for skill in high_priority:
            if skill in missing_skills:
                recommendations.append(f"Learn {skill} - High market demand")
        
        # Suggest complementary skills
        if 'Python' in existing_skills and 'Machine Learning' in missing_skills:
            recommendations.append("Add Machine Learning to your Python skills")
        
        if 'React' in existing_skills and 'Node.js' in missing_skills:
            recommendations.append("Learn Node.js for full-stack development")
        
        return recommendations
    
    def _parse_duration(self, duration: str) -> datetime:
        """Parse duration string to datetime."""
        # Simplified parsing - would need more sophisticated parsing
        try:
            if 'present' in duration.lower() or 'current' in duration.lower():
                return datetime.now()
            return datetime.now() - timedelta(days=365)  # Default to 1 year ago
        except:
            return datetime.now()
    
    def _calculate_career_progression(self, experiences: List[Dict]) -> List[Dict]:
        """Calculate career progression based on work experiences."""
        progression = []
        
        for i, exp in enumerate(experiences):
            level = self._determine_job_level(exp['position'])
            progression.append({
                'index': i,
                'position': exp['position'],
                'level': level,
                'company': exp['company'],
                'skills': exp['skills']
            })
        
        return progression
    
    def _predict_career_trajectory(self, progression: List[Dict]) -> List[Dict]:
        """Predict future career trajectory."""
        if not progression:
            return []
        
        # Simple prediction based on current trend
        current_level = progression[-1]['level']
        next_levels = {
            'Junior': ['Mid-level', 'Senior'],
            'Mid-level': ['Senior', 'Lead'],
            'Senior': ['Lead', 'Principal', 'Manager'],
            'Lead': ['Principal', 'Manager', 'Director'],
            'Principal': ['Architect', 'Director', 'VP'],
            'Manager': ['Senior Manager', 'Director', 'VP']
        }
        
        predictions = next_levels.get(current_level, ['Senior', 'Lead'])
        
        return [
            {
                'predicted_role': pred,
                'timeline': f"{i+1} year{'s' if i+1 > 1 else ''}",
                'required_skills': self._get_required_skills_for_role(pred)
            }
            for i, pred in enumerate(predictions[:3])
        ]
    
    def _determine_job_level(self, position: str) -> str:
        """Determine job level from position title."""
        position_lower = position.lower()
        
        if any(junior in position_lower for junior in ['junior', 'entry', 'associate', '0-2']):
            return 'Junior'
        elif any(mid in position_lower for mid in ['mid', 'intermediate', '3-5']):
            return 'Mid-level'
        elif any(senior in position_lower for senior in ['senior', 'lead', 'sr', '6+']):
            return 'Senior'
        elif any(lead in position_lower for lead in ['lead', 'principal', 'architect']):
            return 'Lead'
        elif any(manager in position_lower for manager in ['manager', 'director', 'vp']):
            return 'Manager'
        else:
            return 'Mid-level'  # Default
    
    def _suggest_next_roles(self, experiences: List[Dict]) -> List[str]:
        """Suggest next career roles based on experience."""
        if not experiences:
            return ['Junior Developer', 'Entry-level Engineer']
        
        last_role = experiences[-1]['position']
        skills = experiences[-1]['skills']
        
        suggestions = []
        
        if 'Python' in skills or 'Java' in skills:
            suggestions.extend(['Senior Developer', 'Tech Lead', 'Engineering Manager'])
        
        if 'React' in skills or 'Angular' in skills:
            suggestions.extend(['Senior Frontend Developer', 'UI/UX Lead', 'Frontend Architect'])
        
        if 'AWS' in skills or 'DevOps' in skills:
            suggestions.extend(['DevOps Engineer', 'Cloud Architect', 'Platform Engineer'])
        
        return suggestions[:5]
    
    def _analyze_skill_growth(self, experiences: List[Dict]) -> List[Dict]:
        """Analyze skill growth over time."""
        skill_timeline = []
        accumulated_skills = set()
        
        for exp in experiences:
            new_skills = set(exp['skills']) - accumulated_skills
            if new_skills:
                skill_timeline.append({
                    'position': exp['position'],
                    'new_skills': list(new_skills),
                    'total_skills': len(accumulated_skills.union(new_skills))
                })
                accumulated_skills.update(new_skills)
        
        return skill_timeline
    
    def _analyze_skills_trends(self, job_descriptions: List[JobDescription]) -> List[Dict]:
        """Analyze skills trends from job descriptions."""
        skills_count = {}
        
        for job in job_descriptions:
            skills = job.skills_required
            for skill in skills:
                skills_count[skill] = skills_count.get(skill, 0) + 1
        
        return [
            {'skill': skill, 'count': count, 'trend': 'increasing'}
            for skill, count in sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
    
    def _analyze_role_trends(self, job_descriptions: List[JobDescription]) -> List[Dict]:
        """Analyze role trends from job descriptions."""
        roles_count = {}
        
        for job in job_descriptions:
            title = job.title
            roles_count[title] = roles_count.get(title, 0) + 1
        
        return [
            {'role': role, 'count': count, 'trend': 'growing'}
            for role, count in sorted(roles_count.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
    
    def _analyze_experience_trends(self, job_descriptions: List[JobDescription]) -> List[Dict]:
        """Analyze experience requirements trends."""
        experience_levels = {}
        
        for job in job_descriptions:
            exp = job.experience_required
            if exp:
                experience_levels[exp] = experience_levels.get(exp, 0) + 1
        
        return [
            {'experience': exp, 'count': count}
            for exp, count in sorted(experience_levels.items(), key=lambda x: x[1], reverse=True)
        ]
    
    def _get_salary_trends(self) -> List[Dict]:
        """Get salary trends from market data."""
        # Mock data - would integrate with real salary APIs
        return [
            {'role': 'Junior Developer', 'min_salary': 50000, 'max_salary': 70000, 'median': 60000},
            {'role': 'Mid-level Developer', 'min_salary': 70000, 'max_salary': 100000, 'median': 85000},
            {'role': 'Senior Developer', 'min_salary': 90000, 'max_salary': 130000, 'median': 110000},
            {'role': 'Lead Developer', 'min_salary': 110000, 'max_salary': 150000, 'median': 130000},
            {'role': 'Engineering Manager', 'min_salary': 130000, 'max_salary': 180000, 'median': 155000},
        ]
    
    def _get_salary_benchmarks(self, experience: int, skills: List[str]) -> List[Dict]:
        """Get salary benchmarks based on experience and skills."""
        # Mock data - would integrate with real salary APIs
        base_salary = 50000 + (experience * 10000)
        
        skill_premiums = {
            'Python': 10000,
            'React': 8000,
            'AWS': 12000,
            'Machine Learning': 15000,
            'Docker': 5000,
            'Kubernetes': 10000,
            'Node.js': 7000,
            'GraphQL': 6000,
            'TypeScript': 5000,
            'Microservices': 8000
        }
        
        total_premium = sum(skill_premiums.get(skill, 0) for skill in skills)
        adjusted_salary = base_salary + total_premium
        
        return [
            {'level': 'Entry', 'salary': max(40000, adjusted_salary - 20000)},
            {'level': 'Market', 'salary': adjusted_salary},
            {'level': 'Senior', 'salary': adjusted_salary + 20000},
            {'level': 'Expert', 'salary': adjusted_salary + 40000}
        ]
    
    def _calculate_total_experience(self, user_resumes: List[ParsedResume]) -> int:
        """Calculate total years of experience from resumes."""
        total_months = 0
        
        for resume in user_resumes:
            experiences = resume.work_experience
            for exp in experiences:
                duration = exp.get('duration', '')
                years = self._extract_years_from_duration(duration)
                total_months += years * 12
        
        return total_months // 12
    
    def _extract_years_from_duration(self, duration: str) -> int:
        """Extract years from duration string."""
        import re
        years_match = re.search(r'(\d+)\s*year', duration.lower())
        if years_match:
            return int(years_match.group(1))
        return 1  # Default
    
    def _calculate_market_value(self, experience: int, skills: List[str]) -> Dict[str, Any]:
        """Calculate current market value based on experience and skills."""
        benchmarks = self._get_salary_benchmarks(experience, skills)
        
        return {
            'current_market_value': benchmarks[1]['salary'],
            'potential_range': {
                'min': benchmarks[0]['salary'],
                'max': benchmarks[3]['salary']
            },
            'skill_multiplier': len(skills) * 0.05 + 1
        }
    
    def _calculate_skill_impact(self, skills: List[str]) -> Dict[str, float]:
        """Calculate impact of each skill on salary."""
        skill_impact = {}
        
        for skill in skills:
            impact = {
                'Python': 0.15,
                'React': 0.12,
                'AWS': 0.18,
                'Machine Learning': 0.20,
                'Docker': 0.08,
                'Kubernetes': 0.15,
                'Node.js': 0.10,
                'GraphQL': 0.09,
                'TypeScript': 0.08,
                'Microservices': 0.12
            }.get(skill, 0.05)
            
            skill_impact[skill] = impact
        
        return skill_impact
    
    def _calculate_experience_impact(self, experience: int) -> Dict[str, float]:
        """Calculate impact of experience on salary."""
        return {
            'base_multiplier': 1 + (experience * 0.1),
            'experience_bonus': min(experience * 5000, 50000),
            'seniority_bonus': max(0, (experience - 5) * 10000)
        }
    
    def _generate_salary_recommendations(self, experience: int, skills: List[str]) -> List[str]:
        """Generate salary-related recommendations."""
        recommendations = []
        
        if experience < 2:
            recommendations.append("Focus on gaining experience with in-demand skills")
        elif experience < 5:
            recommendations.append("Consider specializing in high-impact skills like ML or cloud")
        else:
            recommendations.append("Leverage your experience for senior roles or management")
        
        high_impact_skills = ['Machine Learning', 'AWS', 'Python']
        missing_high_impact = [s for s in high_impact_skills if s not in skills]
        
        for skill in missing_high_impact:
            recommendations.append(f"Adding {skill} could increase your market value significantly")
        
        return recommendations
    
    def _calculate_market_demand(self, skills_trends: List[Dict]) -> Dict[str, Any]:
        """Calculate market demand for skills."""
        total_demand = sum(item['count'] for item in skills_trends)
        
        return {
            'total_demand': total_demand,
            'high_demand_skills': [item for item in skills_trends if item['count'] > total_demand * 0.1],
            'growing_skills': [item for item in skills_trends if item['trend'] == 'increasing']
        }
    
    def _calculate_industry_growth(self, role_trends: List[Dict]) -> Dict[str, Any]:
        """Calculate industry growth based on role trends."""
        total_roles = sum(item['count'] for item in role_trends)
        
        return {
            'total_roles': total_roles,
            'growing_roles': [item for item in role_trends if item['trend'] == 'growing'],
            'declining_roles': [item for item in role_trends if item['trend'] == 'declining']
        }
    
    def _get_required_skills_for_role(self, role: str) -> List[str]:
        """Get required skills for a specific role."""
        role_skills = {
            'Senior Developer': ['Python', 'React', 'AWS', 'Docker', 'CI/CD'],
            'Tech Lead': ['Python', 'React', 'AWS', 'Leadership', 'Architecture'],
            'Engineering Manager': ['Leadership', 'Project Management', 'Python', 'AWS', 'Team Building'],
            'Principal Engineer': ['Python', 'Architecture', 'AWS', 'Microservices', 'Design Patterns'],
            'Architect': ['Architecture', 'Python', 'AWS', 'Microservices', 'System Design']
        }
        
        return role_skills.get(role, [])
    
    def _get_default_skills_gap(self) -> Dict[str, Any]:
        """Return default skills gap analysis."""
        return {
            'current_skills': [],
            'trending_skills': [],
            'missing_skills': [],
            'existing_skills': [],
            'skill_relevance_scores': {},
            'gap_percentage': 0,
            'recommendations': []
        }
    
    def _get_default_career_trajectory(self) -> Dict[str, Any]:
        """Return default career trajectory."""
        return {
            'work_experiences': [],
            'career_progression': [],
            'future_predictions': [],
            'current_level': 'Unknown',
            'next_roles': [],
            'skill_growth': []
        }
    
    def _get_default_industry_trends(self) -> Dict[str, Any]:
        """Return default industry trends."""
        return {
            'skills_trends': [],
            'role_trends': [],
            'experience_trends': [],
            'salary_trends': [],
            'market_demand': {},
            'industry_growth': {}
        }
    
    def _get_default_salary_insights(self) -> Dict[str, Any]:
        """Return default salary insights."""
        return {
            'current_experience': 0,
            'current_skills': [],
            'salary_benchmarks': [],
            'market_value': {},
            'skill_impact': {},
            'experience_impact': {},
            'recommendations': []

### Information Gathered:
- **Current Features**: The existing dashboard provides real-time statistics, advanced filtering, and search functionality. It also supports bulk operations and exports.
- **Models**: The `Resume`, `ParsedResume`, `JobDescription`, and `MatchResult` models are in place, which will be useful for analytics.
- **Services**: The `ResumeParserService` includes methods for parsing resumes and calculating match scores, which can be leveraged for analytics.
- **Views**: The `ResumeViewSet` and `MatchResultViewSet` provide endpoints for managing resumes and calculating match scores.

### Plan for Phase 2: Advanced Analytics & Insights
1. **Skills Gap Analysis**:
   - Create a new endpoint in `views.py` to analyze the skills gap based on parsed resumes and job descriptions.
   - Implement logic to compare skills in parsed resumes against job descriptions and return insights.

2. **Career Trajectory Visualization**:
   - Extend the existing dashboard to include a new section for visualizing career trajectories based on work experience data.
   - Use charts to represent the progression of roles over time.

3. **Industry Trend Matching**:
   - Create a new service method to analyze industry trends based on job descriptions and parsed resumes.
   - Implement a new endpoint to return trend data for the dashboard.

4. **Salary Insights Based on Experience**:
   - Add a new endpoint to fetch salary insights based on the experience levels extracted from resumes.
   - Integrate this data into the dashboard for visualization.

### Dependent Files to be Edited:
- `api/views.py`: Add new endpoints for analytics.
- `api/services.py`: Implement new methods for analytics.
- `frontend/src/components/EnhancedDashboardFinal.js`: Update the dashboard to visualize new analytics data.

### Follow-up Steps:
- Implement the new features in the backend.
- Update the frontend to display the new analytics.
- Test the new features to ensure they work as expected.

<ask_followup_question>
<question>Please confirm if I can proceed with this plan or if you have any feedback or additional requirements.</question>
</ask_followup_question>
