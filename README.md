# AI-Powered Resume Parser

A professional-grade Django REST API that uses OpenAI GPT and NLP libraries to parse resumes and extract structured data.

## Features

- **AI-Powered Parsing**: Uses OpenAI GPT-3.5-turbo for intelligent resume parsing
- **Multiple File Formats**: Supports PDF, DOCX, and TXT files
- **Structured Output**: Returns JSON with personal info, work experience, skills, etc.
- **Job Matching**: Match resumes against job descriptions
- **Async Processing**: Background tasks for heavy processing
- **RESTful API**: Clean REST API with Django REST Framework
- **User Authentication**: Secure authentication with Django's built-in system
- **File Upload**: Drag-and-drop file upload support
- **AWS Deployment Ready**: Configured for AWS Lambda and S3

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- AWS credentials (optional)

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/token/` - Get authentication token

### Resumes
- `GET /api/resumes/` - List user's resumes
- `POST /api/resumes/` - Upload new resume
- `GET /api/resumes/{id}/` - Get specific resume
- `POST /api/resumes/{id}/parse/` - Parse resume with AI

### Job Descriptions
- `GET /api/job-descriptions/` - List job descriptions
- `POST /api/job-descriptions/` - Create new job description
- `GET /api/job-descriptions/{id}/` - Get specific job description

### Matching
- `POST /api/matches/calculate-match/` - Calculate match score

## Usage Examples

### Upload Resume
```bash
curl -X POST http://localhost:8000/api/resumes/ \
  -H "Authorization: Token your-token" \
  -F "file=@resume.pdf"
```

### Parse Resume
```bash
curl -X POST http://localhost:8000/api/resumes/{id}/parse/ \
  -H "Authorization: Token your-token"
```

### Create Job Description
```bash
curl -X POST http://localhost:8000/api/job-descriptions/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "description": "Looking for experienced Python developer...",
    "skills_required": ["Python", "Django", "REST API"],
    "experience_required": "5+ years"
  }'
```

### Calculate Match
```bash
curl -X POST http://localhost:8000/api/matches/calculate-match/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_id": "resume-uuid",
    "job_description_id": "job-uuid"
  }'
```

## Response Format

### Parsed Resume Response
```json
{
  "personal_info": {
    "full_name": "John Doe",
    "email": "john.doe@email.com",
    "phone": "+1-555-123-4567",
    "location": "San Francisco, CA"
  },
  "summary": "Experienced software engineer with 5+ years...",
  "work_experience": [
    {
      "company": "Tech Corp",
      "position": "Senior Software Engineer",
      "duration": "2020-2023",
      "description": "Led development of microservices...",
      "achievements": ["Reduced API latency by 40%"]
    }
  ],
  "skills": {
    "technical": ["Python", "Django", "React", "AWS"],
    "soft": ["Leadership", "Communication"],
    "languages": ["English", "Spanish"]
  }
}
```

## Deployment

### AWS Lambda Deployment

1. Install Zappa:
```bash
pip install zappa
```

2. Initialize Zappa:
```bash
zappa init
```

3. Deploy:
```bash
zappa deploy
```

### Docker Deployment

1. Build image:
```bash
docker build -t ai-resume-parser .
```

2. Run container:
```bash
docker run -p 8000:8000 ai-resume-parser
```

## Testing

Run tests:
```bash
python manage.py test
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
