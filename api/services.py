import os
import io
import json
import logging
from typing import Dict, List, Any
import openai
from django.conf import settings
from PyPDF2 import PdfReader
import docx
import pytesseract
from PIL import Image
import spacy

logger = logging.getLogger(__name__)

class ResumeParserService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.nlp = spacy.load("en_core_web_sm")
        
    def extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """Extract text from resume file based on file type."""
        try:
            if file_type.lower() == 'pdf':
                return self._extract_text_from_pdf(file_path)
            elif file_type.lower() == 'docx':
                return self._extract_text_from_docx(file_path)
            elif file_type.lower() == 'txt':
                return self._extract_text_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Error extracting text from file: {str(e)}")
            raise
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            return ""
    
    def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {str(e)}")
            return ""
    
    def parse_resume_with_openai(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume text using OpenAI GPT."""
        try:
            prompt = self._build_resume_parsing_prompt(resume_text)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional resume parser. Extract structured information from the given resume text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            parsed_data = response.choices[0].message.content
            return json.loads(parsed_data)
            
        except Exception as e:
            logger.error(f"Error parsing resume with OpenAI: {str(e)}")
            return self._get_default_parsed_data()
    
    def _build_resume_parsing_prompt(self, resume_text: str) -> str:
        """Build prompt for OpenAI resume parsing."""
        return f"""
        Parse the following resume and extract structured information in JSON format:
        
        Resume Text:
        {resume_text}
        
        Extract the following information:
        {{
            "personal_info": {{
                "full_name": "",
                "email": "",
                "phone": "",
                "location": "",
                "linkedin": "",
                "website": ""
            }},
            "summary": "",
            "work_experience": [
                {{
                    "company": "",
                    "position": "",
                    "duration": "",
                    "description": "",
                    "achievements": []
                }}
            ],
            "education": [
                {{
                    "degree": "",
                    "institution": "",
                    "graduation_year": "",
                    "gpa": ""
                }}
            ],
            "skills": {{
                "technical": [],
                "soft": [],
                "languages": []
            }},
            "certifications": [],
            "projects": [
                {{
                    "name": "",
                    "description": "",
                    "technologies": [],
                    "duration": ""
                }}
            ],
            "contact_info": {{
                "email": "",
                "phone": "",
                "address": ""
            }}
        }}
        
        Return only valid JSON without any additional text or formatting.
        """
    
    def _get_default_parsed_data(self) -> Dict[str, Any]:
        """Return default parsed data structure when parsing fails."""
        return {
            "personal_info": {},
            "summary": "",
            "work_experience": [],
            "education": [],
            "skills": {"technical": [], "soft": [], "languages": []},
            "certifications": [],
            "projects": [],
            "contact_info": {}
        }
    
    def calculate_match_score(self, resume_data: Dict[str, Any], job_description: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate match score between resume and job description."""
        try:
            resume_skills = set(resume_data.get('skills', {}).get('technical', []))
            job_skills = set(job_description.get('skills_required', []))
            
            matched_skills = list(resume_skills.intersection(job_skills))
            missing_skills = list(job_skills.difference(resume_skills))
            
            # Calculate skill match percentage
            skill_match_percentage = (len(matched_skills) / len(job_skills)) * 100 if job_skills else 0
            
            # Check experience match
            resume_experience = self._calculate_total_experience(resume_data)
            required_experience = job_description.get('experience_required', '')
            
            return {
                'match_score': round(skill_match_percentage, 2),
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'experience_match': {
                    'resume_experience': resume_experience,
                    'required_experience': required_experience,
                    'match': self._check_experience_match(resume_experience, required_experience)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating match score: {str(e)}")
            return {
                'match_score': 0,
                'matched_skills': [],
                'missing_skills': [],
                'experience_match': {'resume_experience': 0, 'required_experience': '', 'match': False}
            }
    
    def _calculate_total_experience(self, resume_data: Dict[str, Any]) -> int:
        """Calculate total years of experience from resume."""
        try:
            work_experience = resume_data.get('work_experience', [])
            total_months = 0
            
            for job in work_experience:
                duration = job.get('duration', '')
                # Simple parsing - can be enhanced
                if 'year' in duration.lower():
                    years = int(''.join(filter(str.isdigit, duration)))
                    total_months += years * 12
            
            return total_months // 12
        except:
            return 0
    
    def _check_experience_match(self, resume_experience: int, required_experience: str) -> bool:
        """Check if resume experience matches job requirements."""
        try:
            if not required_experience:
                return True
            
            # Extract years from required experience
            required_years = int(''.join(filter(str.isdigit, required_experience)))
            return resume_experience >= required_years
            
        except:
            return False
