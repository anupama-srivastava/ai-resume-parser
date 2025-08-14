from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_enhanced import (
    AnalyticsViewSet,
    OrganizationViewSet,
    TeamMemberViewSet,
    CareerInsightsViewSet
)
from .views_phase3 import Phase3AIViewSet

# Router for enhanced API endpoints
router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organizations')
router.register(r'team-members', TeamMemberViewSet, basename='team-members')
router.register(r'career-insights', CareerInsightsViewSet, basename='career-insights')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')
router.register(r'ai', Phase3AIViewSet, basename='ai')

# Complete API endpoints including Phase 3
urlpatterns = [
    path('api/v2/', include(router.urls)),
    
    # Enhanced analytics endpoints
    path('api/v2/analytics/skills-gap/', AnalyticsViewSet.as_view({'get': 'skills_gap'})),
    path('api/v2/analytics/career-trajectory/', AnalyticsViewSet.as_view({'get': 'career_trajectory'})),
    path('api/v2/analytics/industry-trends/', AnalyticsViewSet.as_view({'get': 'industry_trends'})),
    path('api/v2/analytics/salary-insights/', AnalyticsViewSet.as_view({'get': 'salary_insights'})),
    path('api/v2/analytics/comprehensive/', AnalyticsViewSet.as_view({'get': 'comprehensive_analytics'})),
    
    # Phase 3 AI endpoints
    path('api/v2/ai/upgrade-parsing/<uuid:pk>/', Phase3AIViewSet.as_view({'post': 'upgrade_parsing'})),
    path('api/v2/ai/semantic-match/', Phase3AIViewSet.as_view({'post': 'semantic_match'})),
    path('api/v2/ai/cultural-fit/', Phase3AIViewSet.as_view({'post': 'cultural_fit_assessment'})),
    path('api/v2/ai/generate-cover-letter/', Phase3AIViewSet.as_view({'post': 'generate_cover_letter'})),
    path('api/v2/ai/automated-improvement/<uuid:pk>/', Phase3AIViewSet.as_view({'post': 'automated_improvement'})),
    path('api/v2/ai/market-analysis/', Phase3AIViewSet.as_view({'post': 'market_analysis'})),
    path('api/v2/ai/career-recommendations/', Phase3AIViewSet.as_view({'get': 'career_recommendations'})),
    path('api/v2/ai/cover-letter-history/', Phase3AIViewSet.as_view({'get': 'cover_letter_history'})),
    path('api/v2/ai/ai-insights-summary/', Phase3AIViewSet.as_view({'get': 'ai_insights_summary'})),
    path('api/v2/ai/batch-semantic-match/', Phase3AIViewSet.as_view({'post': 'batch_semantic_match'})),
    path('api/v2/ai/optimize-resume/', Phase3AIViewSet.as_view({'post': 'optimize_resume_for_job'})),
    
    # Team collaboration endpoints
    path('api/v2/organizations/<uuid:pk>/dashboard/', OrganizationViewSet.as_view({'get': 'dashboard'})),
    path('api/v2/team-members/invite/', TeamMemberViewSet.as_view({'post': 'invite_member'})),
    path('api/v2/career-insights/mark-read/', CareerInsightsViewSet.as_view({'post': 'mark_read'}))
]
