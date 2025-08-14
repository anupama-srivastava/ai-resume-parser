from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Resume, ParsedResume, JobDescription, MatchResult, CareerInsights
from .services_phase3 import Phase3AIService
from .tasks_phase3 import (
    upgrade_resume_parsing_task,
    generate_cover_letter_task,
    analyze_market_trends_task,
    generate_career_recommendations_task
)
import logging

logger = logging.getLogger(__name__)

class Phase3AIViewSet(viewsets.ViewSet):
    """
    Advanced AI features for Phase 3 implementation
    GPT-4 integration, semantic matching, cultural fit, and personalized recommendations
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ai_service = Phase3AIService()
    
    @action(detail=True, methods=['post'])
    def upgrade_parsing(self, request, pk=None):
        """Upgrade resume parsing to GPT-4"""
        try:
            resume = get_object_or_404(Resume, id=pk, user=request.user)
            
            # Trigger background task for GPT-4 parsing
            upgrade_resume_parsing_task.delay(resume.id)
            
            return Response({
                "message": "Resume parsing upgrade to GPT-4 initiated",
                "status": "processing"
            })
            
        except Exception as e:
            logger.error(f"Error upgrading parsing: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def semantic_match(self, request):
        """Advanced semantic job matching"""
        try:
            resume_id = request.data.get('resume_id')
            job_description_id = request.data.get('job_description_id')
            
            if not resume_id or not job_description_id:
                return Response(
                    {"error": "Both resume_id and job_description_id are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check permissions
            resume = get_object_or_404(Resume, id=resume_id, user=request.user)
            job_desc = get_object_or_404(JobDescription, id=job_description_id)
            
            # Perform semantic matching
            match_result = self.ai_service.semantic_job_matching(
                resume_id, 
                job_description_id
            )
            
            # Save enhanced match result
            enhanced_match = MatchResult.objects.create(
                resume=resume,
                job_description=job_desc,
                match_score=match_result.get('overall_score', 0),
                summary=match_result.get('match_explanation', ''),
                cultural_fit_score=match_result.get('cultural_fit', {}).get('overall_cultural_fit', 0)
            )
            
            return Response({
                "match_result": match_result,
                "match_id": enhanced_match.id
            })
            
        except Exception as e:
            logger.error(f"Error in semantic matching: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def cultural_fit_assessment(self, request):
        """Advanced cultural fit assessment"""
        try:
            resume_id = request.data.get('resume_id')
            job_description_id = request.data.get('job_description_id')
            
            if not resume_id or not job_description_id:
                return Response(
                    {"error": "Both resume_id and job_description_id are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check permissions
            resume = get_object_or_404(Resume, id=resume_id, user=request.user)
            job_desc = get_object_or_404(JobDescription, id=job_description_id)
            
            # Perform cultural fit assessment
            cultural_fit = self.ai_service.cultural_fit_assessment(
                resume_id,
                job_description_id
            )
            
            return Response(cultural_fit)
            
        except Exception as e:
            logger.error(f"Error in cultural fit assessment: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_cover_letter(self, request):
        """Generate personalized cover letter"""
        try:
            resume_id = request.data.get('resume_id')
            job_description_id = request.data.get('job_description_id')
            
            if not resume_id or not job_description_id:
                return Response(
                    {"error": "Both resume_id and job_description_id are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check permissions
            resume = get_object_or_404(Resume, id=resume_id, user=request.user)
            job_desc = get_object_or_404(JobDescription, id=job_description_id)
            
            # Trigger background task for cover letter generation
            generate_cover_letter_task.delay(resume_id, job_description_id)
            
            return Response({
                "message": "Cover letter generation initiated",
                "status": "processing"
            })
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def automated_improvement(self, request, pk=None):
        """AI-powered resume improvement suggestions"""
        try:
            resume = get_object_or_404(Resume, id=pk, user=request.user)
            
            # Generate improvement suggestions
            improvements = self.ai_service.automated_resume_improvement(resume.id)
            
            # Save insights
            for recommendation in improvements.get('priority_recommendations', []):
                CareerInsights.objects.create(
                    user=request.user,
                    resume=resume,
                    insight_type='skill_recommendation',
                    title=recommendation.get('title', 'Resume Improvement'),
                    description=recommendation.get('description', ''),
                    data=improvements,
                    confidence_score=improvements.get('current_score', 0.8)
                )
            
            return Response(improvements)
            
        except Exception as e:
            logger.error(f"Error in resume improvement: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def market_analysis(self, request):
        """Real-time job market analysis"""
        try:
            skills = request.data.get('skills', [])
            location = request.data.get('location', '')
            
            if not skills:
                return Response(
                    {"error": "Skills parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Perform market analysis
            market_data = self.ai_service.real_time_job_market_analysis(skills, location)
            
            # Trigger background analysis task
            analyze_market_trends_task.delay(request.user.id, skills, location)
            
            return Response(market_data)
            
        except Exception as e:
            logger.error(f"Error in market analysis: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def career_recommendations(self, request):
        """Get personalized career recommendations"""
        try:
            # Generate career recommendations
            recommendations = self.ai_service.personalized_career_recommendations(
                request.user.id
            )
            
            # Save recommendations
            for rec in recommendations:
                CareerInsights.objects.create(
                    user=request.user,
                    insight_type='career_path',
                    title=rec.get('title', 'Career Recommendation'),
                    description=rec.get('description', ''),
                    data=rec,
                    confidence_score=rec.get('confidence_score', 0.8)
                )
            
            return Response({
                "recommendations": recommendations,
                "count": len(recommendations)
            })
            
        except Exception as e:
            logger.error(f"Error generating career recommendations: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def cover_letter_history(self, request):
        """Get cover letter generation history"""
        try:
            # Get user's cover letter history
            cover_letters = CareerInsights.objects.filter(
                user=request.user,
                insight_type='cover_letter'
            ).order_by('-created_at')
            
            return Response({
                "cover_letters": [
                    {
                        "id": cl.id,
                        "title": cl.title,
                        "description": cl.description,
                        "created_at": cl.created_at,
                        "data": cl.data
                    }
                    for cl in cover_letters
                ],
                "count": cover_letters.count()
            })
            
        except Exception as e:
            logger.error(f"Error fetching cover letter history: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def ai_insights_summary(self, request):
        """Get comprehensive AI insights summary"""
        try:
            user = request.user
            
            # Get all AI-generated insights
            insights = CareerInsights.objects.filter(
                user=user
            ).order_by('-created_at')[:10]
            
            # Get recent AI activities
            recent_matches = MatchResult.objects.filter(
                resume__user=user
            ).order_by('-created_at')[:5]
            
            # Calculate AI usage statistics
            stats = {
                "total_insights": CareerInsights.objects.filter(user=user).count(),
                "total_matches": MatchResult.objects.filter(resume__user=user).count(),
                "recent_activity": [
                    {
                        "type": "insight",
                        "title": insight.title,
                        "created_at": insight.created_at
                    }
                    for insight in insights
                ] + [
                    {
                        "type": "match",
                        "score": match.match_score,
                        "created_at": match.created_at
                    }
                    for match in recent_matches
                ]
            }
            
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Error fetching AI insights: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def batch_semantic_match(self, request):
        """Batch semantic matching for multiple resumes"""
        try:
            resume_ids = request.data.get('resume_ids', [])
            job_description_id = request.data.get('job_description_id')
            
            if not resume_ids or not job_description_id:
                return Response(
                    {"error": "resume_ids and job_description_id are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            job_desc = get_object_or_404(JobDescription, id=job_description_id)
            
            # Check permissions for all resumes
            resumes = Resume.objects.filter(
                id__in=resume_ids,
                user=request.user
            )
            
            results = []
            for resume in resumes:
                match_result = self.ai_service.semantic_job_matching(
                    resume.id,
                    job_description_id
                )
                results.append({
                    "resume_id": resume.id,
                    "resume_name": resume.original_filename,
                    "match_result": match_result
                })
            
            return Response({
                "batch_results": results,
                "count": len(results)
            })
            
        except Exception as e:
            logger.error(f"Error in batch semantic matching: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def optimize_resume_for_job(self, request):
        """Optimize resume for specific job using AI"""
        try:
            resume_id = request.data.get('resume_id')
            job_description_id = request.data.get('job_description_id')
            
            if not resume_id or not job_description_id:
                return Response(
                    {"error": "Both resume_id and job_description_id are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            resume = get_object_or_404(Resume, id=resume_id, user=request.user)
            job_desc = get_object_or_404(JobDescription, id=job_description_id)
            
            # Get optimization suggestions
            improvements = self.ai_service.automated_resume_improvement(resume.id)
            
            # Filter for job-specific optimizations
            job_specific_optimizations = self._filter_job_specific_optimizations(
                improvements,
                job_desc
            )
            
            return Response({
                "optimizations": job_specific_optimizations,
                "resume_id": resume_id,
                "job_id": job_description_id
            })
            
        except Exception as e:
            logger.error(f"Error optimizing resume: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _filter_job_specific_optimizations(self, improvements: Dict, job_desc) -> Dict[str, Any]:
        """Filter optimizations specific to the job"""
        # Filter recommendations based on job requirements
        job_keywords = set(job_desc.skills_required + job_desc.requirements)
        
        filtered_optimizations = {
            "keyword_optimization": [
                opt for opt in improvements.get('keyword_optimization', [])
                if any(keyword.lower() in str(opt).lower() for keyword in job_keywords)
            ],
            "skills_enhancement": [
                skill for skill in improvements.get('skills_enhancement', [])
                if skill.lower() in [kw.lower() for kw in job_keywords]
            ]
        }
        
        return filtered_optimizations
