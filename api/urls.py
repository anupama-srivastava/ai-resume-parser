from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResumeViewSet, JobDescriptionViewSet, MatchResultViewSet

router = DefaultRouter()
router.register(r'resumes', ResumeViewSet, basename='resume')
router.register(r'job-descriptions', JobDescriptionViewSet, basename='jobdescription')
router.register(r'matches', MatchResultViewSet, basename='matchresult')

urlpatterns = [
    path('', include(router.urls)),
]
