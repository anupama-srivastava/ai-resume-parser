@echo off
echo ========================================
echo AI Resume Parser - GitHub Update Script
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from: https://git-scm.com/
    pause
    exit /b 1
)

REM Check if we're in a git repository
if not exist .git (
    echo Initializing new git repository...
    git init
    git remote add origin https://github.com/anupama-srivastava/ai-resume-parser.git
) else (
    echo Git repository already exists
)

REM Create enhancement branch
echo Creating enhancement branch...
git checkout -b feature/advanced-enhancements 2>nul || (
    echo Branch already exists, switching to it...
    git checkout feature/advanced-enhancements
)

REM Add all changes
echo Adding all changes...
git add .

REM Check if there are changes to commit
git diff --cached --quiet
if %errorlevel% neq 0 (
    echo Committing changes...
    git commit -m "feat: Add advanced enhancements for Phase 1-3 implementation

- Add real-time parsing visualization with WebSocket support
- Implement advanced analytics dashboard
- Add GPT-4 integration capabilities
- Include skills gap analysis and career trajectory features
- Add industry trends and salary insights
- Implement personalized recommendations system
- Add comprehensive enhancement plan documentation"
    
    echo Pushing to GitHub...
    git push -u origin feature/advanced-enhancements
    
    echo.
    echo ========================================
    echo SUCCESS! Changes pushed to GitHub
    echo ========================================
    echo Branch: feature/advanced-enhancements
    echo URL: https://github.com/anupama-srivastava/ai-resume-parser
    echo.
    echo Next steps:
    echo 1. Go to GitHub and create a Pull Request
    echo 2. Review the changes
    echo 3. Merge the PR when ready
) else (
    echo No changes to commit
)

echo.
pause
