"""Serializers para buzon interno."""

from __future__ import annotations

from rest_framework import serializers

from .models import InternalMessage


class InternalMessageSerializer(serializers.ModelSerializer):
    """Serializer para mensajes internos."""

    sender_username = serializers.CharField(source="sender.username", read_only=True, allow_null=True)
    recipient_username = serializers.CharField(source="recipient.username", read_only=True)

    class Meta:
        model = InternalMessage
        fields = [
            "id",
            "sender",
            "sender_username",
            "recipient",
            "recipient_username",
            "subject",
            "body",
            "message_type",
            "priority",
            "is_read",
            "read_at",
            "created_at",
            "expires_at",
            "created_by_system",
            "metadata",
        ]
        read_only_fields = ["id", "created_at", "read_at", "is_read"]


class CreateMessageSerializer(serializers.Serializer):
    """Serializer para crear mensaje."""

    recipient_id = serializers.IntegerField()
    subject = serializers.CharField(max_length=255)
    body = serializers.CharField(style={'base_template': 'textarea.html'})
    message_type = serializers.ChoiceField(
        choices=["info", "warning", "alert", "system"], default="info"
    )
    priority = serializers.ChoiceField(
        choices=["low", "medium", "high", "critical"], default="medium"
    )
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    metadata = serializers.JSONField(required=False, default=dict)
