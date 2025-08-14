from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_enhanced import (
    AnalyticsViewSet,
    OrganizationViewSet,
    TeamMemberViewSet,
    CareerInsightsViewSet
)

# Router for enhanced API endpoints
router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organizations')
router.register(r'team-members', TeamMemberViewSet, basename='team-members')
router.register(r'career-insights', CareerInsightsViewSet, basename='career-insights')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

# Enhanced API endpoints
urlpatterns = [
    path('api/v2/', include(router.urls)),
    
    # Enhanced analytics endpoints
    path('api/v2/analytics/skills-gap/', AnalyticsViewSet.as_view({'get': 'skills_gap'})),
    path('api/v2/analytics/career-trajectory/', AnalyticsViewSet.as_view({'get': 'career_trajectory'})),
    path('api/v2/analytics/industry-trends/', AnalyticsViewSet.as_view({'get': 'industry_trends'})),
    path('api/v2/analytics/salary-insights/', AnalyticsViewSet.as_view({'get': 'salary_insights'})),
    path('api/v2/analytics/comprehensive/', AnalyticsViewSet.as_view({'get': 'comprehensive_analytics'})),
    
    # Team collaboration endpoints
    path('api/v2/organizations/<uuid:pk>/dashboard/', OrganizationViewSet.as_view({'get': 'dashboard'})),
    path('api/v2/team-members/invite/', TeamMemberViewSet.as_view({'post': 'invite_member'})),
    path('api/v2/career-insights/mark-read/', CareerInsightsViewSet.as_view({'post': 'mark_read'}))
]
