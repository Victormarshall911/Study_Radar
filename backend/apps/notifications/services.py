import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import requests
from django.conf import settings
from django.core.mail import send_mail
from apps.opportunities.models import Opportunity
from apps.notifications.models import (
    Notification,
    NotificationDelivery,
    AlertRule,
    DeliveryChannel,
    DeliveryStatus,
)

logger = logging.getLogger(__name__)

class BaseNotificationProvider:
    channel_name = 'base'

    def send(self, title: str, body: str, recipient: str) -> Dict[str, Any]:
        raise NotImplementedError

class TelegramNotificationProvider(BaseNotificationProvider):
    channel_name = DeliveryChannel.TELEGRAM

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        self.chat_id = chat_id or getattr(settings, 'TELEGRAM_CHAT_ID', '')
        self.enabled = getattr(settings, 'TELEGRAM_ENABLED', False)

    def send(self, title: str, body: str, recipient: Optional[str] = None) -> Dict[str, Any]:
        target_chat = recipient or self.chat_id
        if not self.enabled or not self.bot_token or not target_chat:
            logger.info("Telegram sending skipped (disabled or missing token/chat_id).")
            return {'status': 'skipped', 'reason': 'telegram_not_configured_or_disabled'}

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        message_text = f"*{title}*\n\n{body}"
        payload = {
            'chat_id': target_chat,
            'text': message_text,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': False
        }

        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                return {'status': 'success', 'telegram_response': resp.json()}
            else:
                return {'status': 'failed', 'error': resp.text, 'status_code': resp.status_code}
        except Exception as e:
            logger.error(f"Telegram dispatch failed: {str(e)}")
            return {'status': 'failed', 'error': str(e)}

class EmailNotificationProvider(BaseNotificationProvider):
    channel_name = DeliveryChannel.EMAIL

    def __init__(self):
        self.enabled = getattr(settings, 'EMAIL_NOTIFICATION_ENABLED', False)
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'alerts@studyradar.local')

    def send(self, title: str, body: str, recipient: str) -> Dict[str, Any]:
        if not self.enabled:
            logger.info("Email notification skipped (disabled in settings).")
            return {'status': 'skipped', 'reason': 'email_disabled'}

        try:
            send_mail(
                subject=f"[Study Radar] {title}",
                message=body,
                from_email=self.from_email,
                recipient_list=[recipient],
                fail_silently=False
            )
            return {'status': 'success'}
        except Exception as e:
            logger.error(f"Email dispatch error: {str(e)}")
            return {'status': 'failed', 'error': str(e)}

class LocalAuditLogProvider(BaseNotificationProvider):
    channel_name = DeliveryChannel.LOCAL_LOG

    def send(self, title: str, body: str, recipient: str = 'local_audit_log') -> Dict[str, Any]:
        log_path = getattr(settings, 'NOTIFICATION_LOG_PATH', None)
        if log_path:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*70}\n")
                f.write(f"TIMESTAMP: {datetime.now(timezone.utc).isoformat()}\n")
                f.write(f"TITLE: {title}\n")
                f.write(f"RECIPIENT: {recipient}\n\n")
                f.write(f"{body}\n")
                f.write(f"{'='*70}\n")
        return {'status': 'success', 'logged_to': str(log_path)}

class NotificationDispatcher:
    """
    Coordinates alert generation and dispatches across channels with strict duplicate suppression.
    """

    def __init__(self):
        self.telegram = TelegramNotificationProvider()
        self.email = EmailNotificationProvider()
        self.local_log = LocalAuditLogProvider()

    def format_notification(self, opp: Opportunity) -> tuple[str, str]:
        """Formats concise, high-value notification text conforming to Section 21."""
        title = f"NEW STUDY FOUND: {opp.title}"

        # Location string
        geo_names = [g.geography.city or g.geography.state_province or g.geography.country for g in opp.geographies.all() if g.geography]
        loc_str = ", ".join(geo_names) if geo_names else opp.get_geography_status_display()

        body = (
            f"Title: {opp.title}\n"
            f"Posted: {opp.published_at.strftime('%Y-%m-%d %H:%M UTC') if opp.published_at else 'Recently'}\n"
            f"Location: {loc_str}\n"
            f"Type: {opp.get_study_type_display()}\n"
            f"Reward: {opp.reward_text or ('$' + str(opp.reward_amount) if opp.reward_amount else 'Unspecified')}\n"
            f"Duration: {opp.duration_text or (str(opp.duration_minutes) + ' mins' if opp.duration_minutes else 'Unspecified')}\n\n"
            f"Eligibility:\n{opp.eligibility_text or 'General US/Canada adult participant eligibility.'}\n\n"
            f"Source: {opp.organization or opp.sources.first().source.name if opp.sources.exists() else 'Public Source'}\n"
            f"Apply: {opp.application_url or opp.source_url}"
        )
        return title, body

    def dispatch_for_opportunity(self, opportunity: Opportunity, force: bool = False) -> List[NotificationDelivery]:
        """Evaluates alerting eligibility and dispatches notifications."""
        if not force and not opportunity.is_eligible_for_alert:
            logger.info(f"Opportunity {opportunity.id} is not eligible for alert.")
            return []

        title, body = self.format_notification(opportunity)

        # Get or create active AlertRule
        rule = AlertRule.objects.filter(is_active=True).first()
        if not rule:
            rule = AlertRule.objects.create(name="Default 7-day US/Canada Rule")

        # Record Notification
        notification = Notification.objects.create(
            opportunity=opportunity,
            alert_rule=rule,
            title=title,
            body=body,
            status=DeliveryStatus.PENDING
        )

        deliveries = []
        channels_succeeded = []

        # 1. Local audit log dispatch (always enabled for local observability)
        if getattr(settings, 'NOTIFICATION_LOCAL_LOG_ENABLED', True):
            log_res = self.local_log.send(title, body)
            deliv = NotificationDelivery.objects.create(
                notification=notification,
                channel=DeliveryChannel.LOCAL_LOG,
                recipient='local_audit_log',
                status=DeliveryStatus.SUCCESS if log_res.get('status') == 'success' else DeliveryStatus.FAILED,
                response_payload=log_res,
                sent_at=datetime.now(timezone.utc)
            )
            deliveries.append(deliv)
            channels_succeeded.append(DeliveryChannel.LOCAL_LOG)

        # 2. Telegram dispatch
        if rule.notify_telegram and getattr(settings, 'TELEGRAM_ENABLED', False):
            tg_res = self.telegram.send(title, body)
            deliv = NotificationDelivery.objects.create(
                notification=notification,
                channel=DeliveryChannel.TELEGRAM,
                recipient=self.telegram.chat_id or 'default_chat',
                status=DeliveryStatus.SUCCESS if tg_res.get('status') == 'success' else DeliveryStatus.FAILED,
                error_message=tg_res.get('error', ''),
                response_payload=tg_res,
                sent_at=datetime.now(timezone.utc)
            )
            deliveries.append(deliv)
            if tg_res.get('status') == 'success':
                channels_succeeded.append(DeliveryChannel.TELEGRAM)

        # 3. Email dispatch
        if rule.notify_email and getattr(settings, 'EMAIL_NOTIFICATION_ENABLED', False):
            recipient_email = getattr(settings, 'ALERT_RECIPIENT_EMAIL', 'user@example.com')
            em_res = self.email.send(title, body, recipient=recipient_email)
            deliv = NotificationDelivery.objects.create(
                notification=notification,
                channel=DeliveryChannel.EMAIL,
                recipient=recipient_email,
                status=DeliveryStatus.SUCCESS if em_res.get('status') == 'success' else DeliveryStatus.FAILED,
                error_message=em_res.get('error', ''),
                response_payload=em_res,
                sent_at=datetime.now(timezone.utc)
            )
            deliveries.append(deliv)
            if em_res.get('status') == 'success':
                channels_succeeded.append(DeliveryChannel.EMAIL)

        # Mark opportunity as notified so it is NEVER alerted again (Section 22)
        opportunity.has_been_notified = True
        opportunity.notification_count += 1
        opportunity.notification_sent_at = datetime.now(timezone.utc)
        opportunity.notified_channels = channels_succeeded
        opportunity.save(update_fields=['has_been_notified', 'notification_count', 'notification_sent_at', 'notified_channels'])

        notification.status = DeliveryStatus.SUCCESS if channels_succeeded else DeliveryStatus.FAILED
        notification.save(update_fields=['status'])

        return deliveries
