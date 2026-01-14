"""Vistas DRF para autenticación y gestión de tokens."""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import AuthenticationService, TokenService


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username", "")
        password = request.data.get("password", "")

        try:
            tokens = AuthenticationService.login(username=username, password=password, request=request)
            return Response(tokens, status=status.HTTP_200_OK)
        except Exception as exc:  # pragma: no cover - comportamiento validado en tests de servicios
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh = request.data.get("refresh", "")
        if not refresh:
            return Response({"detail": "Refresh token requerido"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tokens = TokenService.refresh_access_token(refresh)
        except Exception as exc:  # pragma: no cover - verificado vía tests unitarios
            return Response({"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(tokens, status=status.HTTP_200_OK)

