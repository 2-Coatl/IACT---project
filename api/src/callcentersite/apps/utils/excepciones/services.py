import json
from django.contrib.auth import get_user_model
from .models import Excepcion

User = get_user_model()


class ExcepcionService:
    
    @staticmethod
    def solicitar_excepcion(titulo, justificacion, tipo, solicitado_por_id):
        usuario = User.objects.get(id=solicitado_por_id)
        return Excepcion.objects.create(
            titulo=titulo,
            justificacion=justificacion,
            tipo=tipo,
            solicitado_por=usuario
        )
    
    @staticmethod
    def listar_excepciones(estado=None):
        qs = Excepcion.objects.all()
        if estado:
            qs = qs.filter(estado=estado)
        return list(qs)
    
    @staticmethod
    def aprobar_excepcion(excepcion_id, aprobado_por_id):
        excepcion = Excepcion.objects.get(id=excepcion_id)
        usuario = User.objects.get(id=aprobado_por_id)
        excepcion.estado = 'aprobada'
        excepcion.aprobado_por = usuario
        excepcion.save()
        return excepcion
    
    @staticmethod
    def rechazar_excepcion(excepcion_id, rechazado_por_id):
        excepcion = Excepcion.objects.get(id=excepcion_id)
        usuario = User.objects.get(id=rechazado_por_id)
        excepcion.estado = 'rechazada'
        excepcion.aprobado_por = usuario
        excepcion.save()
        return excepcion
    
    @staticmethod
    def exportar_excepciones():
        excepciones = Excepcion.objects.all()
        data = [
            {
                'id': e.id,
                'titulo': e.titulo,
                'tipo': e.tipo,
                'estado': e.estado
            }
            for e in excepciones
        ]
        return json.dumps(data, indent=2)
