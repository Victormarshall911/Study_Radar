from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification, NotificationDelivery, AlertRule, DeliveryChannel
from .serializers import NotificationSerializer, NotificationDeliverySerializer, AlertRuleSerializer
from .services import NotificationDispatcher

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all().select_related('opportunity', 'alert_rule').prefetch_related('deliveries').order_by('-created_at')
    serializer_class = NotificationSerializer

    @action(detail=False, methods=['post'], url_path='test')
    def test_notification(self, request):
        """Allows testing notification delivery locally without real credentials."""
        channel = request.data.get('channel', 'local_log')
        dispatcher = NotificationDispatcher()

        title = "TEST NOTIFICATION: Study Radar Alert Engine"
        body = (
            "This is a verified test alert from Study Radar.\n"
            "Channel: " + channel + "\n"
            "Timestamp: " + request.data.get('timestamp', 'now')
        )

        if channel == DeliveryChannel.TELEGRAM:
            res = dispatcher.telegram.send(title, body)
        elif channel == DeliveryChannel.EMAIL:
            recipient = request.data.get('recipient', 'test@example.com')
            res = dispatcher.email.send(title, body, recipient=recipient)
        else:
            res = dispatcher.local_log.send(title, body)

        return Response({
            'status': 'test_dispatched',
            'channel': channel,
            'result': res
        }, status=status.HTTP_200_OK)

class AlertRuleViewSet(viewsets.ModelViewSet):
    queryset = AlertRule.objects.all().order_by('-created_at')
    serializer_class = AlertRuleSerializer
