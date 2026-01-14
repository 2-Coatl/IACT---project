"""Views para buzon interno."""

from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import InternalMessage
from .serializers import CreateMessageSerializer, InternalMessageSerializer
from .services import NotificationService


class InternalMessageViewSet(viewsets.ModelViewSet):
    """ViewSet para mensajes internos."""

    queryset = InternalMessage.objects.all()
    serializer_class = InternalMessageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["is_read", "priority", "message_type", "created_by_system"]
    search_fields = ["subject", "body"]
    ordering_fields = ["created_at", "priority", "is_read"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Filtrar mensajes por usuario autenticado."""
        return InternalMessage.objects.filter(recipient=self.request.user)

    def create(self, request):
        """Enviar mensaje interno."""
        serializer = CreateMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mensaje = NotificationService.enviar_mensaje(
            sender_id=request.user.id,
            **serializer.validated_data
        )

        output_serializer = InternalMessageSerializer(mensaje)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Marcar mensaje como leido."""
        mensaje = self.get_object()
        NotificationService.marcar_como_leido(mensaje_id=mensaje.id)
        serializer = self.get_serializer(mensaje)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """Obtener cantidad de mensajes no leidos."""
        count = NotificationService.contar_no_leidos(user_id=request.user.id)
        return Response({"unread_count": count})

    @action(detail=False, methods=["get"])
    def unread(self, request):
        """Listar solo mensajes no leidos."""
        mensajes = InternalMessage.objects.filter(
            recipient=request.user, is_read=False
        ).order_by("-created_at")
        page = self.paginate_queryset(mensajes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(mensajes, many=True)
        return Response(serializer.data)
