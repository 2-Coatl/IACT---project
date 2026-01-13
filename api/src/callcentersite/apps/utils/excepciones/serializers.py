from rest_framework import serializers
from .models import Excepcion


class ExcepcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Excepcion
        fields = '__all__'
        read_only_fields = ['solicitado_por', 'aprobado_por', 'created_at', 'updated_at']
