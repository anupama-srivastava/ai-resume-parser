from django.urls import re_path
from .consumers import ResumeParsingConsumer

websocket_urlpatterns = [
    re_path(r'ws/parsing/(?P<resume_id>\w+)/$', ResumeParsingConsumer.as_asgi()),
]
