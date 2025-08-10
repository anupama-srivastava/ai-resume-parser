from celery import shared_task
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from .models import Resume, ParsedResume
from .services import ResumeParserService

@shared_task
def parse_resume_task(resume_id):
    """Async task to parse a resume."""
    try:
        resume = get_object_or_404(Resume, id=resume_id)
        parser_service = ResumeParserService()
        
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
        
        # Create parsed resume
        ParsedResume.objects.create(
            resume=resume,
            personal_info=parsed_data.get('personal_info', {}),
            work_experience=parsed_data.get('work_experience', []),
            education=parsed_data.get('education', []),
            skills=parsed_data.get('skills', {}),
            certifications=parsed_data.get('certifications', []),
            projects=parsed_data.get('projects', []),
            summary=parsed_data.get('summary', ''),
            contact_info=parsed_data.get('contact_info', {})
        )
        
        return f"Resume {resume_id} parsed successfully"
        
    except Exception as e:
        resume = get_object_or_404(Resume, id=resume_id)
        resume.processing_status = 'failed'
        resume.save()
        return f"Error parsing resume {resume_id}: {str(e)}"

@shared_task
def calculate_match_score_task(resume_id, job_description_id):
    """Async task to calculate match score."""
    from .models import Resume, JobDescription, MatchResult
    from .services import ResumeParserService
    
    try:
        resume = get_object_or_404(Resume, id=resume_id)
        job_description = get_object_or_404(JobDescription, id=job_description_id)
        
        parser_service = ResumeParserService()
        
        # Get parsed resume data
        parsed_resume = get_object_or_404(ParsedResume, resume=resume)
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
        
        return f"Match calculated for resume {resume_id} and job {job_description_id}"
        
    except Exception as e:
        return f"Error calculating match: {str(e)}"
