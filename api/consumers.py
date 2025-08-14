import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Resume, ParsedResume
from .tasks import parse_resume_async
import logging

logger = logging.getLogger(__name__)

class ResumeParsingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = f"user_{self.user.id}"
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'start_parsing':
            await self.start_parsing(data.get('resume_id'))
        elif message_type == 'get_progress':
            await self.get_parsing_progress(data.get('resume_id'))
    
    async def start_parsing(self, resume_id):
        try:
            resume = await self.get_resume(resume_id)
            if resume and resume.user == self.user:
                # Start async parsing
                parse_resume_async.delay(resume_id)
                
                await self.send(text_data=json.dumps({
                    'type': 'parsing_started',
                    'resume_id': resume_id,
                    'status': 'processing'
                }))
        except Exception as e:
            logger.error(f"Error starting parsing: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def get_parsing_progress(self, resume_id):
        try:
            resume = await self.get_resume(resume_id)
            if resume and resume.user == self.user:
                progress = await self.calculate_progress(resume)
                
                await self.send(text_data=json.dumps({
                    'type': 'parsing_progress',
                    'resume_id': resume_id,
                    'progress': progress
                }))
        except Exception as e:
            logger.error(f"Error getting progress: {e}")
    
    @database_sync_to_async
    def get_resume(self, resume_id):
        try:
            return Resume.objects.get(id=resume_id)
        except Resume.DoesNotExist:
            return None
    
    @database_sync_to_async
    def calculate_progress(self, resume):
        # Calculate parsing progress based on processing status
        status_map = {
            'pending': 0,
            'processing': 50,
            'completed': 100,
            'failed': -1
        }
        
        return {
            'percentage': status_map.get(resume.processing_status, 0),
            'status': resume.processing_status,
            'estimated_time_remaining': self.get_estimated_time(resume)
        }
    
    def get_estimated_time_remaining(self, resume):
        # Simple estimation based on file size
        if resume.file_size:
            size_mb = resume.file_size / (1024 * 1024)
            return max(2, int(size_mb * 0.5))  # 0.5 seconds per MB
        return 2

class AnalyticsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = f"analytics_{self.user.id}"
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'subscribe_analytics':
            await self.subscribe_to_analytics()
    
    async def subscribe_to_analytics(self):
        # Send initial analytics data
        analytics_data = await self.get_analytics_data()
        
        await self.send(text_data=json.dumps({
            'type': 'analytics_update',
            'data': analytics_data
        }))
    
    @database_sync_to_async
    def get_analytics_data(self):
        from .services_enhanced import AdvancedAnalyticsService
        service = AdvancedAnalyticsService()
        return service.get_comprehensive_analytics(self.user.id)
    
    async def analytics_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'analytics_update',
            'data': event['data']
        }))
