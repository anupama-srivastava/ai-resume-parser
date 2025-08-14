# AI-Powered Resume Parser

A professional-grade Django REST API that uses OpenAI GPT and NLP libraries to parse resumes and extract structured data.

## 🚀 Current Features

### ✅ Core Features
- **AI-Powered Parsing**: Uses OpenAI GPT-3.5-turbo for intelligent resume parsing
- **Multiple File Formats**: Supports PDF, DOCX, and TXT files
- **Structured Output**: Returns JSON with personal info, work experience, skills, etc.
- **Job Matching**: Match resumes against job descriptions with scoring
- **Async Processing**: Background tasks for heavy processing
- **RESTful API**: Clean REST API with Django REST Framework
- **User Authentication**: Secure authentication with Django's built-in system
- **File Upload**: Drag-and-drop file upload support with real-time feedback
- **AWS Deployment Ready**: Configured for AWS Lambda and S3
- **Responsive Design**: Modern React frontend with Material-UI

### ✅ Frontend Features
- **Interactive Dashboard**: Real-time statistics and activity charts
- **Resume Management**: Upload, view, and manage resumes
- **Job Description Management**: Create and manage job postings
- **Matching Interface**: Visual resume-job matching with scores
- **Responsive Design**: Mobile-friendly interface

### ✅ API Features
- **Authentication**: Token-based authentication
- **File Processing**: Async processing with status tracking
- **Comprehensive Endpoints**: Full CRUD operations for all entities
- **Data Validation**: Input validation and error handling

## 🎯 Enhancement Roadmap

### Phase 1: Interactive Web Dashboard (In Progress)
- [ ] **Real-time parsing visualization** - Live progress updates during parsing
- [ ] **Advanced filtering and search** - Multi-criteria search and filtering
- [ ] **Bulk operations support** - Bulk upload, processing, and management
- [ ] **Export functionality** - PDF/Excel export of parsed data
- [ ] **Enhanced dashboard widgets** - More interactive charts and KPIs

### Phase 2: Advanced Analytics & Insights (Planned)
- [ ] **Skills gap analysis** - Visual representation of missing skills
- [ ] **Career trajectory visualization** - Career path analysis and suggestions
- [ ] **Industry trend matching** - Real-time industry skill trends
- [ ] **Salary insights** - Salary recommendations based on experience/skills
- [ ] **Multi-tenant support** - Organization-based user management
- [ ] **Team collaboration tools** - Sharing, comments, and team workflows
- [ ] **White-label options** - Custom branding for clients

### Phase 3: AI Enhancement & Personalization (Future)
- [ ] **GPT-4 integration** - Upgrade to latest OpenAI models
- [ ] **Personalized career recommendations** - AI-driven career suggestions
- [ ] **Automated resume improvement** - AI suggestions for resume enhancement
- [ ] **Cover letter generation** - Automated, tailored cover letters
- [ ] **Semantic job matching** - Advanced NLP-based matching beyond keywords
- [ ] **Cultural fit assessment** - Company culture matching algorithms
- [ ] **Real-time job market analysis** - Live market data and trends

## 📊 Current Architecture

```
├── Backend (Django + DRF)
│   ├── Models: Resume, ParsedResume, JobDescription, MatchResult
│   ├── Services: ResumeParserService (OpenAI integration)
│   ├── Tasks: Async processing with Celery
│   └── API: RESTful endpoints for all operations
├── Frontend (React)
│   ├── Dashboard: Statistics and overview
│   ├── Resume Management: Upload and parsing
│   ├── Job Management: Job description handling
│   └── Matching: Resume-job matching interface
└── Infrastructure
    ├── AWS Lambda ready
    ├── S3 for file storage
    └── PostgreSQL for data storage
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend)
- OpenAI API key
- AWS credentials (optional)

### Backend Setup
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

### Frontend Setup
1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

## 📖 API Documentation

### Authentication
- `POST /api/auth/token/` - Get authentication token

### Resumes
- `GET /api/resumes/` - List user's resumes
- `POST /api/resumes/` - Upload new resume
- `GET /api/resumes/{id}/` - Get specific resume
- `POST /api/resumes/{id}/parse/` - Parse resume with AI
- `DELETE /api/resumes/{id}/` - Delete resume

### Job Descriptions
- `GET /api/job-descriptions/` - List job descriptions
- `POST /api/job-descriptions/` - Create new job description
- `GET /api/job-descriptions/{id}/` - Get specific job description
- `PUT /api/job-descriptions/{id}/` - Update job description
- `DELETE /api/job-descriptions/{id}/` - Delete job description

### Matching
- `POST /api/matches/calculate-match/` - Calculate match score
- `GET /api/matches/` - List match results

## 📊 Response Formats

### Parsed Resume Response
```json
{
  "personal_info": {
    "full_name": "John Doe",
    "email": "john.doe@email.com",
    "phone": "+1-555-123-4567",
    "location": "San Francisco, CA",
    "linkedin": "linkedin.com/in/johndoe",
    "website": "johndoe.dev"
  },
  "summary": "Experienced software engineer with 5+ years...",
  "work_experience": [
    {
      "company": "Tech Corp",
      "position": "Senior Software Engineer",
      "duration": "2020-2023",
      "description": "Led development of microservices...",
      "achievements": ["Reduced API latency by 40%", "Led team of 5 developers"]
    }
  ],
  "education": [
    {
      "degree": "Bachelor of Science in Computer Science",
      "institution": "Stanford University",
      "graduation_year": "2019",
      "gpa": "3.8"
    }
  ],
  "skills": {
    "technical": ["Python", "Django", "React", "AWS", "Docker"],
    "soft": ["Leadership", "Communication", "Problem-solving"],
    "languages": ["English", "Spanish"]
  },
  "certifications": ["AWS Solutions Architect", "Google Cloud Professional"],
  "projects": [
    {
      "name": "E-commerce Platform",
      "description": "Built scalable e-commerce solution...",
      "technologies": ["Python", "Django", "PostgreSQL"],
      "duration": "6 months"
    }
  ]
}
```

### Match Result Response
```json
{
  "id": "uuid",
  "resume": { "id": "uuid", "original_filename": "john_doe_resume.pdf" },
  "job_description": { "id": "uuid", "title": "Senior Python Developer" },
  "match_score": 85.5,
  "matched_skills": ["Python", "Django", "REST API"],
  "missing_skills": ["Kubernetes", "GraphQL"],
  "experience_match": {
    "resume_experience": 5,
    "required_experience": "4+ years",
    "match": true
  },
  "summary": "Strong match for Python developer position",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## 🔧 Usage Examples

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
    "skills_required": ["Python", "Django", "REST API", "PostgreSQL"],
    "experience_required": "5+ years",
    "requirements": ["5+ years Python experience", "Django REST framework", "AWS experience"]
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

## 🚀 Deployment Options

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

### Traditional Deployment
1. Set up production server (Gunicorn + Nginx)
2. Configure PostgreSQL database
3. Set up S3 for file storage
4. Configure environment variables

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test api.tests

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🤝 Contributing

We welcome contributions! Please see our enhancement roadmap above for areas where help is needed.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Write tests for new features
- Update documentation
- Follow conventional commits

## 📈 Performance Monitoring

### Current Metrics
- Parsing speed: ~2-3 seconds per resume
- API response time: <500ms for most endpoints
- File upload limit: 10MB
- Supported formats: PDF, DOCX, TXT

### Future Optimizations
- Implement caching with Redis
- Add CDN for file storage
- Optimize database queries
- Implement pagination for large datasets

## 🔐 Security Features

- JWT token authentication
- File type validation
- Rate limiting on API endpoints
- Secure file storage with S3
- Input sanitization and validation

## 📞 Support

For support, email support@ai-resume-parser.com or join our Slack channel.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Django and DRF communities
- React ecosystem contributors
- All our amazing contributors
