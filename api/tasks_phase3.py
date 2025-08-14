from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Resume, ParsedResume, JobDescription, MatchResult, CareerInsights
from .services_phase3 import Phase3AIService
import logging

logger = logging.getLogger(__name__)

@shared_task
def upgrade_resume_parsing_task(resume_id):
    """Upgrade resume parsing to GPT-4"""
    try:
        from .services_phase3 import Phase3AIService
        
        ai_service = Phase3AIService()
        resume = Resume.objects.get(id=resume_id)
        
        # Get resume text
        resume_text = resume.extracted_text
        
        if not resume_text:
            logger.error(f"No extracted text found for resume {resume_id}")
            return False
        
        # Parse with GPT-4
        enhanced_data = ai_service.upgrade_to_gpt4_parsing(resume_text)
        
        # Update parsed resume with enhanced data
        parsed_resume, created = ParsedResume.objects.get_or_create(
            resume=resume,
            defaults={
                'personal_info': enhanced_data.get('personal_info', {}),
                'work_experience': enhanced_data.get('work_experience', []),
                'education': enhanced_data.get('education', []),
                'skills': enhanced_data.get('skills', {}),
                'certifications': enhanced_data.get('certifications', []),
                'projects': enhanced_data.get('projects', []),
                'summary': enhanced_data.get('summary', ''),
                'contact_info': enhanced_data.get('contact_info', {})
            }
        )
        
        if not created:
            # Update existing parsed resume
            parsed_resume.personal_info = enhanced_data.get('personal_info', {})
            parsed_resume.work_experience = enhanced_data.get('work_experience', [])
            parsed_resume.education = enhanced_data.get('education', [])
            parsed_resume.skills = enhanced_data.get('skills', {})
            parsed_resume.certifications = enhanced_data.get('certifications', [])
            parsed_resume.projects = enhanced_data.get('projects', [])
            parsed_resume.summary = enhanced_data.get('summary', '')
            parsed_resume.contact_info = enhanced_data.get('contact_info', {})
            parsed_resume.save()
        
        logger.info(f"Resume {resume_id} upgraded to GPT-4 parsing")
        return True
        
    except Exception as e:
        logger.error(f"Error upgrading resume parsing: {str(e)}")
        return False

@shared_task
def generate_cover_letter_task(resume_id, job_description_id):
    """Generate personalized cover letter in background"""
    try:
        from .services_phase3 import Phase3AIService
        
        ai_service = Phase3AIService()
        
        # Generate cover letter
        cover_letter_data = ai_service.generate_cover_letter(resume_id, job_description_id)
        
        if 'error' in cover_letter_data:
            logger.error(f"Error generating cover letter: {cover_letter_data['error']}")
            return False
        
        # Save cover letter as career insight
        resume = Resume.objects.get(id=resume_id)
        job_desc = JobDescription.objects.get(id=job_description_id)
        
        CareerInsights.objects.create(
            user=resume.user,
            resume=resume,
            insight_type='cover_letter',
            title=f"Cover Letter for {job_desc.title}",
            description=cover_letter_data.get('cover_letter', ''),
            data=cover_letter_data,
            confidence_score=cover_letter_data.get('personalization_score', 0.8)
        )
        
        logger.info(f"Cover letter generated for resume {resume_id} and job {job_description_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating cover letter: {str(e)}")
        return False

@shared_task
def analyze_market_trends_task(user_id, skills, location=None):
    """Analyze market trends in background"""
    try:
        from .services_phase3 import Phase3AIService
        
        ai_service = Phase3AIService()
        user = User.objects.get(id=user_id)
        
        # Analyze market trends
        market_data = ai_service.real_time_job_market_analysis(skills, location)
        
        # Save market insights
        CareerInsights.objects.create(
            user=user,
            insight_type='market_analysis',
            title=f"Market Analysis for {', '.join(skills[:3])}",
            description=f"Real-time market insights for skills: {', '.join(skills)}",
            data=market_data,
            confidence_score=0.9
        )
        
        logger.info(f"Market analysis completed for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error analyzing market trends: {str(e)}")
        return False

@shared_task
def generate_career_recommendations_task(user_id):
    """Generate personalized career recommendations"""
    try:
        from .services_phase3 import Phase3AIService
        
        ai_service = Phase3AIService()
        user = User.objects.get(id=user_id)
        
        # Generate recommendations
        recommendations = ai_service.personalized_career_recommendations(user_id)
        
        # Save recommendations
        for rec in recommendations:
            CareerInsights.objects.create(
                user=user,
                insight_type='career_path',
                title=rec.get('title', 'Career Recommendation'),
                description=rec.get('description', ''),
                data=rec,
                confidence_score=rec.get('confidence_score', 0.8)
            )
        
        logger.info(f"Career recommendations generated for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating career recommendations: {str(e)}")
        return False

@shared_task
def batch_semantic_analysis_task(resume_ids, job_description_id):
    """Batch semantic analysis for multiple resumes"""
    try:
        from .services_phase3 import Phase3AIService
        
        ai_service = Phase3AIService()
        
        results = []
        for resume_id in resume_ids:
            try:
                result = ai_service.semantic_job_matching(resume_id, job_description_id)
                results.append({
                    "resume_id": resume_id,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "resume_id": resume_id,
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"Batch semantic analysis completed for {len(resume_ids)} resumes")
        return results
        
    except Exception as e:
        logger.error(f"Error in batch semantic analysis: {str(e)}")
        return []

@shared_task
def optimize_resume_batch_task(resume_ids, optimization_type='general'):
    """Batch resume optimization"""
    try:
        from .services_phase3 import Phase3AIService
        
        ai_service = Phase3AIService()
        
        results = []
        for resume_id in resume_ids:
            try:
                resume = Resume.objects.get(id=resume_id)
                improvements = ai_service.automated_resume_improvement(resume_id)
                
                # Save optimization results
                CareerInsights.objects.create(
                    user=resume.user,
                    resume=resume,
                    insight_type='resume_optimization',
                    title=f"Resume Optimization - {optimization_type}",
                    description=f"AI-powered optimization for {optimization_type}",
                    data=improvements,
                    confidence_score=improvements.get('current_score', 0.8)
                )
                
                results.append({
                    "resume_id": resume_id,
                    "success": True,
                    "improvements": improvements
                })
            except Exception as e:
                results.append({
                    "resume_id": resume_id,
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"Batch resume optimization completed for {len(resume_ids)} resumes")
        return results
        
    except Exception as e:
        logger.error(f"Error in batch resume optimization: {str(e)}")
        return []

@shared_task
def daily_market_analysis_task():
    """Daily market analysis for all users"""
    try:
        from .services_phase3 import Phase3AIService
        
        ai_service = Phase3AIService()
        
        # Get all users with resumes
        users_with_resumes = User.objects.filter(
            resumes__isnull=False
        ).distinct()
        
        for user in users_with_resumes:
            try:
                # Get user's skills
                user_resumes = Resume.objects.filter(user=user)
                skills = set()
                
                for resume in user_resumes:
                    if hasattr(resume, 'parsedresume'):
                        resume_skills = resume.parsedresume.skills or {}
                        skills.update(resume_skills.get('technical', []))
                
                if skills:
                    # Analyze market for user's skills
                    analyze_market_trends_task.delay(
                        user.id, 
                        list(skills)[:5]  # Top 5 skills
                    )
                    
            except Exception as e:
                logger.error(f"Error processing user {user.id}: {str(e)}")
                continue
        
        logger.info("Daily market analysis completed")
        return True
        
    except Exception as e:
        logger.error(f"Error in daily market analysis: {str(e)}")
        return False

@shared_task
def weekly_career_insights_task():
    """Weekly career insights generation"""
    try:
        from .services_phase3 import Phase3AIService
        
        ai_service = Phase3AIService()
        
        # Get active users
        active_users = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=7)
        )
        
        for user in active_users:
            try:
                # Generate career recommendations
                generate_career_recommendations_task.delay(user.id)
                
            except Exception as e:
                logger.error(f"Error processing user {user.id}: {str(e)}")
                continue
        
        logger.info("Weekly career insights generation completed")
        return True
        
    except Exception as e:
        logger.error(f"Error in weekly career insights: {str(e)}")
        return False

@shared_task
def cleanup_old_ai_insights_task():
    """Clean up old AI insights"""
    try:
        from datetime import timedelta
        
        # Remove insights older than 90 days
        cutoff_date = timezone.now() - timedelta(days=90)
        
        deleted_count = CareerInsights.objects.filter(
            created_at__lt=cutoff_date,
            insight_type__in=['cover_letter', 'market_analysis', 'resume_optimization']
        ).count()
        
        CareerInsights.objects.filter(
            created_at__lt=cutoff_date,
            insight_type__in=['cover_letter', 'market_analysis', 'resume_optimization']
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old AI insights")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up old AI insights: {str(e)}")
        return 0

@shared_task
def process_resume_upgrade_batch_task(resume_ids):
    """Batch process resume upgrades to GPT-4"""
    try:
        from .services_phase3 import Phase3AIService
        
        results = []
        for resume_id in resume_ids:
            try:
                result = upgrade_resume_parsing_task(resume_id)
                results.append({
                    "resume_id": resume_id,
                    "success": result
                })
            except Exception as e:
                results.append({
                    "resume_id": resume_id,
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"Batch resume upgrade completed for {len(resume_ids)} resumes")
        return results
        
    except Exception as e:
        logger.error(f"Error in batch resume upgrade: {str(e)}")
        return []

@shared_task
def generate_cover_letters_batch_task(resume_job_pairs):
    """Batch generate cover letters"""
    try:
        from .services_phase3 import Phase3AIService
        
        results = []
        for pair in resume_job_pairs:
            try:
                resume_id = pair.get('resume_id')
                job_id = pair.get('job_description_id')
                
                result = generate_cover_letter_task(resume_id, job_id)
                results.append({
                    "resume_id": resume_id,
                    "job_id": job_id,
                    "success": result
                })
            except Exception as e:
                results.append({
                    "resume_id": resume_id,
                    "job_id": job_id,
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"Batch cover letter generation completed for {len(resume_job_pairs)} pairs")
        return results
        
    except Exception as e:
        logger.error(f"Error in batch cover letter generation: {str(e)}")
        return []
