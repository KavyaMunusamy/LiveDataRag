import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
import json
from datetime import datetime
from ...config.settings import settings
from ...monitoring.logger import get_logger

logger = get_logger(__name__)

class AlertSystem:
    """Alert system for sending notifications through various channels"""
    
    def __init__(self):
        self.smtp_config = {
            'host': settings.SMTP_HOST or 'smtp.gmail.com',
            'port': settings.SMTP_PORT or 587,
            'username': settings.SMTP_USERNAME,
            'password': settings.SMTP_PASSWORD,
            'use_tls': True
        }
        
        # Webhook configurations
        self.webhooks = {
            'slack': settings.SLACK_WEBHOOK_URL,
            'discord': settings.DISCORD_WEBHOOK_URL,
            'teams': settings.TEAMS_WEBHOOK_URL
        }
    
    async def send_alert(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Send alert through specified channel"""
        channel = parameters.get('channel', 'email')
        message = self._format_message(parameters.get('message', ''), context)
        priority = parameters.get('priority', 'medium')
        
        try:
            if channel == 'email':
                result = await self._send_email(parameters, message)
            elif channel == 'slack':
                result = await self._send_slack(message, priority)
            elif channel == 'sms':
                result = await self._send_sms(parameters, message)
            elif channel == 'in_app':
                result = await self._send_in_app_notification(parameters, message)
            elif channel == 'webhook':
                result = await self._send_webhook(parameters, message)
            else:
                raise ValueError(f"Unsupported alert channel: {channel}")
            
            logger.info(f"Alert sent via {channel}: {result}")
            return {
                "status": "success",
                "channel": channel,
                "message_id": result.get('message_id'),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send alert via {channel}: {e}")
            raise
    
    async def _send_email(self, parameters: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Send email alert"""
        if not all([self.smtp_config['username'], self.smtp_config['password']]):
            raise ValueError("SMTP credentials not configured")
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = parameters.get('subject', 'Live Data RAG Alert')
        msg['From'] = self.smtp_config['username']
        msg['To'] = parameters.get('recipient', settings.ALERT_EMAIL)
        
        # Create HTML content
        html_content = self._create_email_template(message, parameters)
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
            if self.smtp_config['use_tls']:
                server.starttls()
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.send_message(msg)
        
        return {"message_id": f"email_{datetime.utcnow().timestamp()}"}
    
    async def _send_slack(self, message: str, priority: str) -> Dict[str, Any]:
        """Send Slack notification"""
        webhook_url = self.webhooks.get('slack')
        if not webhook_url:
            raise ValueError("Slack webhook URL not configured")
        
        # Determine color based on priority
        color_map = {
            'critical': '#ff0000',
            'high': '#ff6600',
            'medium': '#ffcc00',
            'low': '#00cc00'
        }
        
        payload = {
            "attachments": [{
                "color": color_map.get(priority, '#cccccc'),
                "title": "Live Data RAG Alert",
                "text": message,
                "fields": [
                    {
                        "title": "Priority",
                        "value": priority.upper(),
                        "short": True
                    },
                    {
                        "title": "Time",
                        "value": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
                        "short": True
                    }
                ],
                "footer": "Live Data RAG System",
                "ts": datetime.utcnow().timestamp()
            }]
        }
        
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        
        return {"message_id": f"slack_{datetime.utcnow().timestamp()}"}
    
    async def _send_sms(self, parameters: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Send SMS alert (Twilio integration example)"""
        # This is a template - implement based on your SMS provider
        phone_number = parameters.get('phone_number')
        if not phone_number:
            raise ValueError("Phone number required for SMS alert")
        
        # Example using Twilio (uncomment and configure)
        # from twilio.rest import Client
        # client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
        # message = client.messages.create(
        #     body=message[:160],  # SMS length limit
        #     from_=settings.TWILIO_PHONE,
        #     to=phone_number
        # )
        
        # For now, return mock response
        logger.info(f"Mock SMS sent to {phone_number}: {message[:50]}...")
        return {
            "message_id": f"sms_{datetime.utcnow().timestamp()}",
            "recipient": phone_number
        }
    
    async def _send_in_app_notification(self, parameters: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Send in-app notification (store in database for frontend)"""
        from ...models.notification import Notification
        from ...database import SessionLocal
        
        db = SessionLocal()
        try:
            notification = Notification(
                user_id=parameters.get('user_id', 'system'),
                title=parameters.get('title', 'System Alert'),
                message=message,
                priority=parameters.get('priority', 'medium'),
                category='system_alert',
                metadata={
                    "context": parameters.get('context', {}),
                    "source": "action_engine"
                }
            )
            db.add(notification)
            db.commit()
            
            # Trigger WebSocket update
            await self._broadcast_notification(notification)
            
            return {
                "message_id": str(notification.id),
                "notification": notification.to_dict()
            }
        finally:
            db.close()
    
    async def _send_webhook(self, parameters: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Send alert via custom webhook"""
        webhook_url = parameters.get('webhook_url')
        if not webhook_url:
            raise ValueError("Webhook URL required")
        
        payload = {
            "event": "rag_alert",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "message": message,
                "priority": parameters.get('priority'),
                "context": parameters.get('context', {}),
                "parameters": parameters
            }
        }
        
        headers = parameters.get('headers', {'Content-Type': 'application/json'})
        
        response = requests.post(webhook_url, json=payload, headers=headers)
        response.raise_for_status()
        
        return {
            "message_id": f"webhook_{datetime.utcnow().timestamp()}",
            "status_code": response.status_code
        }
    
    def _format_message(self, template: str, context: Dict[str, Any]) -> str:
        """Format message template with context"""
        try:
            # Simple template formatting
            formatted = template
            for key, value in context.items():
                if isinstance(value, dict):
                    value = json.dumps(value, indent=2)
                placeholder = f"{{{key}}}"
                if placeholder in formatted:
                    formatted = formatted.replace(placeholder, str(value))
            
            # Add timestamp
            formatted += f"\n\nGenerated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
            return formatted
            
        except Exception as e:
            logger.error(f"Failed to format message: {e}")
            return template
    
    def _create_email_template(self, message: str, parameters: Dict[str, Any]) -> str:
        """Create HTML email template"""
        priority = parameters.get('priority', 'medium')
        priority_colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745'
        }
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ 
                    background-color: {priority_colors.get(priority, '#007bff')}; 
                    color: white; 
                    padding: 15px; 
                    border-radius: 5px; 
                }}
                .content {{ 
                    background-color: #f8f9fa; 
                    padding: 20px; 
                    border-radius: 5px; 
                    margin-top: 20px; 
                }}
                .footer {{ 
                    margin-top: 20px; 
                    font-size: 12px; 
                    color: #6c757d; 
                    text-align: center; 
                }}
                .priority-badge {{
                    display: inline-block;
                    padding: 3px 10px;
                    border-radius: 20px;
                    background-color: {priority_colors.get(priority, '#6c757d')};
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🚨 Live Data RAG Alert</h2>
                    <span class="priority-badge">{priority.upper()}</span>
                </div>
                <div class="content">
                    <p>{message.replace('\n', '<br>')}</p>
                </div>
                <div class="footer">
                    <p>This is an automated alert from the Live Data RAG with Actions system.</p>
                    <p>Generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def _broadcast_notification(self, notification):
        """Broadcast notification via WebSocket"""
        # This would be implemented in your WebSocket manager
        pass