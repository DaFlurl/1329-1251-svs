# -*- coding: utf-8 -*-
"""
Notification Service for AgentDaf1.1
"""

import logging
from datetime import datetime
from typing import Dict, List, Any

class NotificationService:
    def __init__(self):
        self.notifications = []
        self.logger = logging.getLogger(__name__)
    
    def send_notification(self, title: str, message: str, level: str = "info") -> bool:
        notification = {
            "id": len(self.notifications) + 1,
            "title": title,
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat(),
            "read": False
        }
        self.notifications.append(notification)
        self.logger.info(f"Notification: {title}")
        return True
    
    def get_notifications(self, limit: int = 50) -> List[Dict]:
        return self.notifications[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_notifications": len(self.notifications),
            "unread_notifications": len([n for n in self.notifications if not n["read"]])
        }

notification_service = NotificationService()
