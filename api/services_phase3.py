import json
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q
from django.contrib.auth.models import User
from .models import Resume, ParsedResume, JobDescription, MatchResult, CareerInsights
import openai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from textblob import TextBlob
import requests
from collections import defaultdict

logger = logging.getLogger(__name__)

class Phase3AIService:
    """
    Advanced AI services for Phase 3 implementation
    GPT-4 integration, semantic matching, cultural fit, and personalized recommendations
    """
    
    def __init__(self):
        self.client = openai.OpenAI()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
    def upgrade_to_gpt4_parsing(self, resume_text: str) -> Dict[str, Any]:
        """Enhanced resume parsing using GPT-4 with better accuracy"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert resume parser. Extract structured data from resumes with high accuracy.
                        Focus on:
                        1. Technical skills with proficiency levels
                        2. Soft skills and leadership qualities
                        3. Quantifiable achievements with metrics
                        4. Industry-specific keywords
                        5. Career progression indicators
                        6. Cultural fit indicators
                        7. Salary expectations if mentioned
                        
                        Return JSON with enhanced structure including confidence scores."""
                    },
                    {
                        "role": "user",
                        "content": f"Parse this resume and extract comprehensive structured data:\n\n{resume_text}"
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            parsed_data = json.loads(response.choices[0].message.content)
            
            # Enhance with additional AI analysis
            enhanced_data = self._enhance_parsed_data(parsed_data, resume_text)
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error in GPT-4 parsing: {str(e)}")
            return self._fallback_parsing(resume_text)
    
    def semantic_job_matching(self, resume_id: str, job_description_id: str) -> Dict[str, Any]:
        """Advanced semantic matching beyond keyword matching"""
        try:
            resume = Resume.objects.get(id=resume_id)
            job_desc = JobDescription.objects.get(id=job_description_id)
            
            parsed_resume = resume.parsedresume
            if not parsed_resume:
                return {"error": "Resume not parsed yet"}
            
            # Extract comprehensive text for semantic analysis
            resume_text = self._extract_comprehensive_resume_text(parsed_resume)
            job_text = self._extract_comprehensive_job_text(job_desc)
            
            # Semantic similarity using embeddings
            resume_embedding = self._get_text_embedding(resume_text)
            job_embedding = self._get_text_embedding(job_text)
            
            semantic_score = cosine_similarity(
                [resume_embedding], 
                [job_embedding]
            )[0][0] * 100
            
            # Analyze skill relevance
            skill_relevance = self._analyze_skill_relevance(
                parsed_resume.skills.get('technical', []),
                job_desc.skills_required
            )
            
            # Experience relevance
            experience_relevance = self._analyze_experience_relevance(
                parsed_resume.work_experience,
                job_desc.requirements
            )
            
            # Cultural fit analysis
            cultural_fit = self._analyze_cultural_fit(resume_text, job_text)
            
            # Career trajectory alignment
            trajectory_alignment = self._analyze_career_alignment(
                parsed_resume.work_experience,
                job_desc.title,
                job_desc.description
            )
            
            # Salary alignment
            salary_alignment = self._analyze_salary_alignment(
                parsed_resume,
                job_desc.salary_range
            )
            
            # Generate detailed match explanation
            match_explanation = self._generate_match_explanation(
                semantic_score,
                skill_relevance,
                experience_relevance,
                cultural_fit,
                trajectory_alignment,
                salary_alignment
            )
            
            return {
                "overall_score": round(semantic_score, 2),
                "semantic_similarity": round(semantic_score, 2),
                "skill_relevance": skill_relevance,
                "experience_relevance": experience_relevance,
                "cultural_fit": cultural_fit,
                "trajectory_alignment": trajectory_alignment,
                "salary_alignment": salary_alignment,
                "match_explanation": match_explanation,
                "recommendations": self._generate_match_recommendations(
                    semantic_score, skill_relevance, cultural_fit
                ),
                "confidence_score": self._calculate_confidence_score(
                    semantic_score, skill_relevance, experience_relevance
                )
            }
            
        except Exception as e:
            logger.error(f"Error in semantic matching: {str(e)}")
            return {"error": str(e)}
    
    def cultural_fit_assessment(self, resume_id: str, job_description_id: str) -> Dict[str, Any]:
        """Advanced cultural fit assessment using AI"""
        try:
            resume = Resume.objects.get(id=resume_id)
            job_desc = JobDescription.objects.get(id=job_description_id)
            
            parsed_resume = resume.parsedresume
            if not parsed_resume:
                return {"error": "Resume not parsed yet"}
            
            # Extract cultural indicators
            resume_cultural_indicators = self._extract_cultural_indicators(
                parsed_resume.work_experience,
                parsed_resume.projects or []
            )
            
            job_cultural_indicators = self._extract_job_cultural_indicators(
                job_desc.description,
                job_desc.requirements
            )
            
            # Analyze values alignment
            values_alignment = self._analyze_values_alignment(
                resume_cultural_indicators,
                job_cultural_indicators
            )
            
            # Work style compatibility
            work_style_compatibility = self._analyze_work_style_compatibility(
                resume_cultural_indicators,
                job_cultural_indicators
            )
            
            # Team dynamics assessment
            team_dynamics = self._analyze_team_dynamics(
                resume_cultural_indicators,
                job_cultural_indicators
            )
            
            # Communication style analysis
            communication_style = self._analyze_communication_style(
                parsed_resume.summary or "",
                job_desc.description
            )
            
            # Growth mindset assessment
            growth_mindset = self._analyze_growth_mindset(
                parsed_resume.work_experience,
                parsed_resume.certifications or []
            )
            
            overall_cultural_fit = (
                values_alignment * 0.25 +
                work_style_compatibility * 0.20 +
                team_dynamics * 0.20 +
                communication_style * 0.20 +
                growth_mindset * 0.15
            ) * 100
            
            return {
                "overall_cultural_fit": round(overall_cultural_fit, 2),
                "values_alignment": round(values_alignment * 100, 2),
                "work_style_compatibility": round(work_style_compatibility * 100, 2),
                "team_dynamics": round(team_dynamics * 100, 2),
                "communication_style": round(communication_style * 100, 2),
                "growth_mindset": round(growth_mindset * 100, 2),
                "detailed_analysis": {
                    "values_alignment_details": self._get_values_alignment_details(
                        resume_cultural_indicators, job_cultural_indicators
                    ),
                    "work_style_details": self._get_work_style_details(
                        resume_cultural_indicators, job_cultural_indicators
                    ),
                    "team_dynamics_details": self._get_team_dynamics_details(
                        resume_cultural_indicators, job_cultural_indicators
                    )
                },
                "recommendations": self._generate_cultural_fit_recommendations(
                    overall_cultural_fit, values_alignment, work_style_compatibility
                )
            }
            
        except Exception as e:
            logger.error(f"Error in cultural fit assessment: {str(e)}")
            return {"error": str(e)}
    
    def generate_cover_letter(self, resume_id: str, job_description_id: str) -> Dict[str, Any]:
        """Generate personalized cover letter using GPT-4"""
        try:
            resume = Resume.objects.get(id=resume_id)
            job_desc = JobDescription.objects.get(id=job_description_id)
            
            parsed_resume = resume.parsedresume
            if not parsed_resume:
                return {"error": "Resume not parsed yet"}
            
            # Extract key information
            personal_info = parsed_resume.personal_info or {}
            work_experience = parsed_resume.work_experience or []
            skills = parsed_resume.skills or {}
            
            # Generate tailored cover letter
            prompt = f"""
            Create a compelling, personalized cover letter for:
            
            Candidate: {personal_info.get('full_name', 'Candidate')}
            Position: {job_desc.title}
            Company: Extract from job description
            
            Resume Summary:
            - Experience: {len(work_experience)} positions
            - Key Skills: {', '.join(skills.get('technical', [])[:5])}
            - Recent Role: {work_experience[0].get('position', 'N/A') if work_experience else 'N/A'}
            
            Job Requirements:
            {job_desc.requirements}
            
            Generate a cover letter that:
            1. Highlights relevant experience and achievements
            2. Addresses specific job requirements
            3. Shows enthusiasm for the role and company
            4. Includes quantifiable achievements
            5. Has a professional yet engaging tone
            6. Is 250-400 words
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career coach and professional writer. Create compelling, tailored cover letters that stand out."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=600
            )
            
            cover_letter = response.choices[0].message.content
            
            # Generate variations
            variations = self._generate_cover_letter_variations(
                cover_letter, job_desc.title, parsed_resume
            )
            
            return {
                "cover_letter": cover_letter,
                "variations": variations,
                "tone_analysis": self._analyze_cover_letter_tone(cover_letter),
                "keyword_optimization": self._analyze_keyword_optimization(
                    cover_letter, job_desc.skills_required
                ),
                "length_score": self._evaluate_cover_letter_length(cover_letter),
                "personalization_score": self._evaluate_personalization(
                    cover_letter, parsed_resume, job_desc
                )
            }
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {str(e)}")
            return {"error": str(e)}
    
    def automated_resume_improvement(self, resume_id: str) -> Dict[str, Any]:
        """AI-powered resume improvement suggestions"""
        try:
            resume = Resume.objects.get(id=resume_id)
            parsed_resume = resume.parsedresume
            if not parsed_resume:
                return {"error": "Resume not parsed yet"}
            
            # Analyze current resume
            analysis = self._comprehensive_resume_analysis(parsed_resume)
            
            # Generate improvement suggestions
            improvements = {
                "content_improvements": self._generate_content_improvements(parsed_resume),
                "formatting_suggestions": self._generate_formatting_suggestions(parsed_resume),
                "keyword_optimization": self._generate_keyword_optimization(parsed_resume),
                "achievement_quantification": self._generate_achievement_quantification(parsed_resume),
                "skills_enhancement": self._generate_skills_enhancement(parsed_resume),
                "ats_optimization": self._generate_ats_optimization(parsed_resume),
                "industry_specific_improvements": self._generate_industry_improvements(parsed_resume)
            }
            
            # Calculate improvement impact
            impact_scores = self._calculate_improvement_impact(improvements)
            
            # Generate action plan
            action_plan = self._generate_improvement_action_plan(improvements, impact_scores)
            
            return {
                "current_score": analysis.get("overall_score", 0),
                "improvements": improvements,
                "impact_scores": impact_scores,
                "action_plan": action_plan,
                "priority_recommendations": self._get_priority_recommendations(improvements, impact_scores),
                "estimated_impact": self._estimate_improvement_impact(improvements)
            }
            
        except Exception as e:
            logger.error(f"Error in resume improvement: {str(e)}")
            return {"error": str(e)}
    
    def real_time_job_market_analysis(self, skills: List[str], location: str = None) -> Dict[str, Any]:
        """Real-time job market analysis using AI and market data"""
        try:
            # Get market data from multiple sources
            market_data = self._fetch_real_time_market_data(skills, location)
            
            # Analyze demand trends
            demand_analysis = self._analyze_demand_trends(market_data)
            
            # Salary trend analysis
            salary_trends = self._analyze_salary_trends(market_data)
            
            # Emerging skills identification
            emerging_skills = self._identify_emerging_skills(market_data)
            
            # Job market predictions
            market_predictions = self._generate_market_predictions(market_data)
            
            # Location-based insights
            location_insights = self._analyze_location_insights(market_data, location)
            
            # Industry growth analysis
            industry_growth = self._analyze_industry_growth(market_data)
            
            return {
                "market_overview": market_data.get("overview", {}),
                "demand_analysis": demand_analysis,
                "salary_trends": salary_trends,
                "emerging_skills": emerging_skills,
                "market_predictions": market_predictions,
                "location_insights": location_insights,
                "industry_growth": industry_growth,
                "competitive_landscape": self._analyze_competitive_landscape(market_data),
                "opportunity_score": self._calculate_opportunity_score(market_data, skills),
                "recommendations": self._generate_market_recommendations(market_data, skills)
            }
            
        except Exception as e:
            logger.error(f"Error in market analysis: {str(e)}")
            return {"error": str(e)}
    
    def personalized_career_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """Generate personalized career recommendations using AI"""
        try:
            user = User.objects.get(id=user_id)
            user_resumes = ParsedResume.objects.filter(resume__user=user)
            
            if not user_resumes.exists():
                return []
            
            # Analyze user's career trajectory
            career_analysis = self._analyze_user_career(user_resumes)
            
            # Get market opportunities
            market_opportunities = self._get_personalized_opportunities(career_analysis)
            
            # Generate recommendations
            recommendations = []
            
            for opportunity in market_opportunities[:5]:
                recommendation = {
                    "type": opportunity.get("type", "career_opportunity"),
                    "title": opportunity.get("title", "Career Opportunity"),
                    "description": opportunity.get("description", ""),
                    "rationale": self._generate_recommendation_rationale(
                        career_analysis, opportunity
                    ),
                    "expected_outcomes": self._generate_expected_outcomes(opportunity),
                    "action_steps": self._generate_action_steps(opportunity),
                    "timeline": opportunity.get("timeline", "3-6 months"),
                    "confidence_score": opportunity.get("confidence", 0.8),
                    "market_demand": opportunity.get("demand_score", 0.7),
                    "salary_potential": opportunity.get("salary_potential", {})
                }
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating career recommendations: {str(e)}")
            return []
    
    # Helper methods for the above services
    def _get_text_embedding(self, text: str) -> List[float]:
        """Get text embedding using OpenAI"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            return [0] * 1536
    
    def _enhance_parsed_data(self, parsed_data: Dict[str, Any], resume_text: str) -> Dict[str, Any]:
        """Enhance parsed data with additional AI insights"""
        # Add confidence scores
        enhanced_data = parsed_data.copy()
        
        # Extract additional insights
        enhanced_data['confidence_scores'] = self._calculate_confidence_scores(parsed_data)
        enhanced_data['industry_keywords'] = self._extract_industry_keywords(resume_text)
        enhanced_data['leadership_indicators'] = self._extract_leadership_indicators(resume_text)
        enhanced_data['quantifiable_achievements'] = self._extract_quantifiable_achievements(resume_text)
        
        return enhanced_data
    
    def _fallback_parsing(self, resume_text: str) -> Dict[str, Any]:
        """Fallback parsing method if GPT-4 fails"""
        return {
            "error": "GPT-4 parsing failed",
            "fallback_used": True,
            "basic_extraction": {
                "skills": self._basic_skill_extraction(resume_text),
                "experience": self._basic_experience_extraction(resume_text)
            }
        }
    
    def _extract_comprehensive_resume_text(self, parsed_resume) -> str:
        """Extract comprehensive text from parsed resume"""
        text_parts = []
        
        if parsed_resume.summary:
            text_parts.append(parsed_resume.summary)
        
        for exp in parsed_resume.work_experience:
            text_parts.append(f"{exp.get('position', '')} at {exp.get('company', '')}")
            text_parts.append(exp.get('description', ''))
        
        for edu in parsed_resume.education:
            text_parts.append(f"{edu.get('degree', '')} from {edu.get('institution', '')}")
        
        skills = parsed_resume.skills or {}
        all_skills = skills.get('technical', []) + skills.get('soft', [])
        text_parts.append("Skills: " + ", ".join(all_skills))
        
        return " ".join(text_parts)
    
    def _extract_comprehensive_job_text(self, job_desc) -> str:
        """Extract comprehensive text from job description"""
        text_parts = [
            job_desc.title,
            job_desc.description,
            "Requirements: " + " ".join(job_desc.requirements),
            "Skills: " + " ".join(job_desc.skills_required)
        ]
        
        return " ".join(text_parts)
    
    def _analyze_skill_relevance(self, resume_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
        """Analyze skill relevance between resume and job"""
        resume_set = set(skill.lower() for skill in resume_skills)
        job_set = set(skill.lower() for skill in job_skills)
        
        exact_matches = resume_set.intersection(job_set)
        related_matches = self._find_related_skills(resume_set, job_set)
        
        missing_skills = job_set - resume_set - set(related_matches.keys())
        
        return {
            "exact_matches": list(exact_matches),
            "related_matches": related_matches,
            "missing_skills": list(missing_skills),
            "relevance_score": len(exact_matches) / max(len(job_set), 1) * 100
        }
    
    def _find_related_skills(self, resume_skills: set, job_skills: set) -> Dict[str, List[str]]:
        """Find related skills using semantic similarity"""
        related = {}
        
        # Simple related skill mapping (would use embeddings in production)
        skill_relationships = {
            "python": ["django", "flask", "pandas", "numpy"],
            "javascript": ["react", "node.js", "vue.js", "angular"],
            "aws": ["cloud", "docker", "kubernetes", "devops"]
        }
        
        for job_skill in job_skills:
            for resume_skill in resume_skills:
                if job_skill in skill_relationships:
                    related_skills = skill_relationships[job_skill]
                    if resume_skill in related_skills:
                        related[job_skill] = related.get(job_skill, []) + [resume_skill]
        
        return related
    
    def _analyze_experience_relevance(self, work_experience: List[Dict], requirements: List[str]) -> Dict[str, Any]:
        """Analyze experience relevance to job requirements"""
        relevant_experience = []
        total_months = 0
        
        for exp in work_experience:
            exp_text = f"{exp.get('position', '')} {exp.get('description', '')}"
            relevance_score = self._calculate_requirement_relevance(exp_text, requirements)
            
            if relevance_score > 0.3:
                relevant_experience.append({
                    "position": exp.get('position', ''),
                    "relevance_score": relevance_score,
                    "duration": exp.get('duration', '')
                })
                
                # Calculate months of experience
                months = self._parse_duration_months(exp.get('duration', ''))
                total_months += months
        
        return {
            "relevant_experience": relevant_experience,
            "total_relevant_months": total_months,
            "relevance_score": len(relevant_experience) / max(len(work_experience), 1) * 100
        }
    
    def _calculate_requirement_relevance(self, text: str, requirements: List[str]) -> float:
        """Calculate relevance score for requirements"""
        text_lower = text.lower()
        matches = 0
        
        for req in requirements:
            if any(word.lower() in text_lower for word in req.split()):
                matches += 1
        
        return matches / max(len(requirements), 1)
    
    def _parse_duration_months(self, duration: str) -> int:
        """Parse duration string to months"""
        if not duration:
            return 0
        
        # Handle various formats
        years_match = re.search(r'(\d+(?:\.\d+)?)\s*year', duration.lower())
        if years_match:
            return int(float(years_match.group(1)) * 12)
        
        months_match = re.search(r'(\d+)\s*month', duration.lower())
        if months_match:
            return int(months_match.group(1))
        
        return 12  # Default
    
    def _analyze_cultural_fit(self, resume_text: str, job_text: str) -> Dict[str, Any]:
        """Analyze cultural fit between resume and job"""
        # Use sentiment analysis and keyword matching
        resume_sentiment = TextBlob(resume_text).sentiment
        job_sentiment = TextBlob(job_text).sentiment
        
        # Cultural keywords
        cultural_keywords = {
            "collaborative": ["team", "collaborate", "together", "group"],
            "innovative": ["innovate", "creative", "new", "cutting-edge"],
            "fast-paced": ["fast", "quick", "rapid", "agile"],
            "leadership": ["lead", "manage", "direct", "mentor"],
            "learning": ["learn", "grow", "develop", "improve"]
        }
        
        fit_scores = {}
        for culture_type, keywords in cultural_keywords.items():
            resume_score = sum(1 for keyword in keywords if keyword in resume_text.lower())
            job_score = sum(1 for keyword in keywords if keyword in job_text.lower())
            
            if job_score > 0:
                fit_scores[culture_type] = min(resume_score / job_score, 1.0)
        
        return {
            "overall_fit": sum(fit_scores.values()) / max(len(fit_scores), 1),
            "cultural_indicators": fit_scores,
            "sentiment_alignment": abs(resume_sentiment.polarity - job_sentiment.polarity) < 0.3
        }
    
    def _analyze_career_alignment(self, work_experience: List[Dict], job_title: str, job_description: str) -> Dict[str, Any]:
        """Analyze career trajectory alignment with job"""
        if not work_experience:
            return {"alignment_score": 0, "reasoning": "No experience found"}
        
        # Analyze progression
        positions = [exp.get('position', '').lower() for exp in work_experience]
        job_title_lower = job_title.lower()
        
        # Check for natural progression
        progression_indicators = {
            "junior_to_senior": any("junior" in pos for pos in positions) and "senior" in job_title_lower,
            "developer_to_lead": any("developer" in pos for pos in positions) and "lead" in job_title_lower,
            "individual_to_manager": any("developer" in pos or "engineer" in pos for pos in positions) and "manager" in job_title_lower
        }
        
        # Calculate alignment
        alignment_score = 0
        for indicator, matches in progression_indicators.items():
            if matches:
                alignment_score += 0.33
        
        return {
            "alignment_score": alignment_score,
            "progression_indicators": progression_indicators,
            "career_stage": self._determine_career_stage(work_experience),
            "next_logical_step": self._determine_next_step(work_experience)
        }
    
    def _determine_career_stage(self, work_experience: List[Dict]) -> str:
        """Determine career stage based on experience"""
        total_months = sum(self._parse_duration_months(exp.get('duration', '')) for exp in work_experience)
        years = total_months / 12
        
        if years < 2:
            return "entry"
        elif years < 5:
            return "mid"
        elif years < 10:
            return "senior"
        else:
            return "principal"
    
    def _determine_next_step(self, work_experience: List[Dict]) -> str:
        """Determine next logical career step"""
        if not work_experience:
            return "entry-level position"
        
        latest_position = work_experience[0].get('position', '').lower()
        
        if "junior" in latest_position:
            return "mid-level developer"
        elif "developer" in latest_position and "senior" not in latest_position:
            return "senior developer"
        elif "senior" in latest_position:
            return "lead developer or architect"
        else:
            return "next level position"
    
    def _analyze_salary_alignment(self, parsed_resume, salary_range: Dict) -> Dict[str, Any]:
        """Analyze salary expectations alignment"""
        # Extract salary expectations from resume
        resume_text = str(parsed_resume.__dict__)
        salary_matches = re.findall(r'\$?(\d{4,6})', resume_text)
        
        expected_salary = None
        if salary_matches:
            expected_salary = int(salary_matches[0])
        
        # Analyze salary range
        min_salary = salary_range.get('min', 0)
        max_salary = salary_range.get('max', 0)
        
        alignment = "aligned"
        if expected_salary:
            if expected_salary < min_salary:
                alignment = "below_range"
            elif expected_salary > max_salary:
                alignment = "above_range"
        
        return {
            "alignment": alignment,
            "expected_salary": expected_salary,
            "range_min": min_salary,
            "range_max": max_salary,
            "fit_percentage": self._calculate_salary_fit(expected_salary, min_salary, max_salary)
        }
    
    def _calculate_salary_fit(self, expected: int, min_sal: int, max_sal: int) -> float:
        """Calculate salary fit percentage"""
        if not expected:
            return 100  # No expectation, assume fit
        
        if expected >= min_sal and expected <= max_sal:
            return 100
        
        if expected < min_sal:
            return (expected / min_sal) * 100
        
        # Expected > max_sal
        return (max_sal / expected) * 100
    
    def _generate_match_explanation(self, semantic_score: float, skill_relevance: Dict, 
                                  experience_relevance: Dict, cultural_fit: Dict, 
                                  trajectory_alignment: Dict, salary_alignment: Dict) -> str:
        """Generate detailed match explanation"""
        explanations = []
        
        if semantic_score > 80:
            explanations.append("Strong semantic alignment between your profile and job requirements")
        elif semantic_score > 60:
            explanations.append("Good overall alignment with room for improvement")
        else:
            explanations.append("Limited alignment, consider skill development")
        
        if skill_relevance.get('relevance_score', 0) > 70:
            explanations.append("Excellent skill match for this role")
        
        if experience_relevance.get('total_relevant_months', 0) > 24:
            explanations.append("Substantial relevant experience")
        
        return " ".join(explanations)
    
    def _generate_match_recommendations(self, semantic_score: float, skill_relevance: Dict, 
                                      cultural_fit: Dict) -> List[str]:
        """Generate match improvement recommendations"""
        recommendations = []
        
        if semantic_score < 70:
            recommendations.append("Consider tailoring your resume to better match job keywords")
        
        if skill_relevance.get('missing_skills'):
            recommendations.append(f"Learn these skills: {', '.join(skill_relevance['missing_skills'][:3])}")
        
        if cultural_fit.get('overall_fit', 0) < 0.5:
            recommendations.append("Highlight cultural alignment in your application")
        
        return recommendations
    
    def _calculate_confidence_score(self, semantic_score: float, skill_relevance: Dict, 
                                  experience_relevance: Dict) -> float:
        """Calculate overall confidence score"""
        weights = {
            'semantic': 0.4,
            'skills': 0.3,
            'experience': 0.3
        }
        
        confidence = (
            semantic_score * weights['semantic'] +
            skill_relevance.get('relevance_score', 0) * weights['skills'] +
            experience_relevance.get('relevance_score', 0) * weights['experience']
        )
        
        return min(confidence, 100)
    
    def _extract_cultural_indicators(self, work_experience: List[Dict], projects: List[Dict]) -> Dict[str, Any]:
        """Extract cultural indicators from resume"""
        indicators = {
            "collaboration": 0,
            "leadership": 0,
            "innovation": 0,
            "learning": 0,
            "autonomy": 0
        }
        
        all_text = " ".join([
            exp.get('description', '') for exp in work_experience
        ] + [
            proj.get('description', '') for proj in projects
        ]).lower()
        
        # Count cultural keywords
        cultural_keywords = {
            "collaboration": ["team", "collaborate", "together", "group", "peer"],
            "leadership": ["lead", "manage", "mentor", "guide", "direct"],
            "innovation": ["innovate", "create", "new", "improve", "optimize"],
            "learning": ["learn", "train", "certification", "course", "skill"],
            "autonomy": ["independent", "self-directed", "initiative", "ownership"]
        }
        
        for indicator, keywords in cultural_keywords.items():
            count = sum(all_text.count(keyword) for keyword in keywords)
            indicators[indicator] = count
        
        return indicators
    
    def _extract_job_cultural_indicators(self, description: str, requirements: List[str]) -> Dict[str, Any]:
        """Extract cultural indicators from job description"""
        all_text = (description + " " + " ".join(requirements)).lower()
        
        indicators = {
            "collaborative": "collaborative" in all_text or "team" in all_text,
            "innovative": "innovative" in all_text or "creative" in all_text,
            "fast_paced": "fast-paced" in all_text or "dynamic" in all_text,
            "structured": "structured" in all_text or "process" in all_text,
            "growth_oriented": "growth" in all_text or "learning" in all_text
        }
        
        return indicators
    
    def _generate_cover_letter_variations(self, base_letter: str, job_title: str, parsed_resume) -> List[Dict[str, str]]:
        """Generate cover letter variations"""
        variations = [
            {
                "type": "enthusiastic",
                "tone": "High energy and passion",
                "content": self._adjust_tone(base_letter, "enthusiastic")
            },
            {
                "type": "professional",
                "tone": "Formal and polished",
                "content": self._adjust_tone(base_letter, "professional")
            },
            {
                "type": "confident",
                "tone": "Assertive and self-assured",
                "content": self._adjust_tone(base_letter, "confident")
            }
        ]
        
        return variations
    
    def _adjust_tone(self, text: str, tone: str) -> str:
        """Adjust tone of the text"""
        # Simplified tone adjustment
        tone_modifiers = {
            "enthusiastic": text.replace("I am", "I'm thrilled to be").replace("interested", "passionate"),
            "professional": text,
            "confident": text.replace("I believe", "I know").replace("hope", "will")
        }
        
        return tone_modifiers.get(tone, text)
    
    def _comprehensive_resume_analysis(self, parsed_resume) -> Dict[str, Any]:
        """Comprehensive resume analysis for improvements"""
        analysis = {
            "content_score": 0,
            "formatting_score": 0,
            "keyword_score": 0,
            "achievement_score": 0,
            "ats_score": 0
        }
        
        # Analyze each aspect
        analysis["content_score"] = self._analyze_content_quality(parsed_resume)
        analysis["formatting_score"] = self._analyze_formatting(parsed_resume)
        analysis["keyword_score"] = self._analyze_keyword_usage(parsed_resume)
        analysis["achievement_score"] = self._analyze_achievements(parsed_resume)
        analysis["ats_score"] = self._analyze_ats_compatibility(parsed_resume)
        
        analysis["overall_score"] = sum(analysis.values()) / len(analysis)
        
        return analysis
    
    def _fetch_real_time_market_data(self, skills: List[str], location: str) -> Dict[str, Any]:
        """Fetch real-time market data (mock implementation)"""
        # In production, this would integrate with job APIs
        return {
            "overview": {
                "total_jobs": 1250,
                "average_salary": 95000,
                "growth_rate": 0.12
            },
            "skills_demand": {skill: np.random.randint(100, 1000) for skill in skills},
            "location_data": {
                location or "national": {
                    "average_salary": 95000,
                    "job_count": 1250
                }
            }
        }
    
    def _analyze_user_career(self, user_resumes) -> Dict[str, Any]:
        """Analyze user's career trajectory"""
        # Extract career information
        career_data = {
            "total_experience": 0,
            "skills": [],
            "industries": [],
            "positions": []
        }
        
        for resume in user_resumes:
            # Analyze each resume
            work_exp = resume.work_experience or []
            for exp in work_exp:
                career_data["positions"].append(exp.get('position', ''))
                months = self._parse_duration_months(exp.get('duration', ''))
                career_data["total_experience"] += months
        
        career_data["total_experience"] = career_data["total_experience"] // 12
        
        return career_data
