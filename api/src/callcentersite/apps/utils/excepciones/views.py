from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Excepcion
from .serializers import ExcepcionSerializer
from .services import ExcepcionService


class ExcepcionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Excepcion.objects.all()
    serializer_class = ExcepcionSerializer
    
    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        try:
            excepcion = ExcepcionService.aprobar_excepcion(pk, request.user.id)
            return Response(ExcepcionSerializer(excepcion).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        try:
            excepcion = ExcepcionService.rechazar_excepcion(pk, request.user.id)
            return Response(ExcepcionSerializer(excepcion).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def exportar(self, request):
        data = ExcepcionService.exportar_excepciones()
        response = HttpResponse(data, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="excepciones.json"'
        return response
