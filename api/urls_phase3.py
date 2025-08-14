from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_phase3 import Phase3AIViewSet

router = DefaultRouter()
router.register(r'ai', Phase3AIViewSet, basename='ai')

urlpatterns = [
    path('', include(router.urls)),
]
