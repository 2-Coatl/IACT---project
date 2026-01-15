from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password


class SecurityQuestion(models.Model):
    """
    Pregunta de seguridad para recuperacion contraseña.
    
    CNST-001: NO usar email para recuperacion.
    Sistema de 3 preguntas de seguridad.
    """
    
    question = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Pregunta',
        help_text='Pregunta de seguridad',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa',
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_questions'
        verbose_name = 'Pregunta Seguridad'
        verbose_name_plural = 'Preguntas Seguridad'
        ordering = ['question']
    
    def __str__(self):
        return self.question


class UserSecurityAnswer(models.Model):
    """
    Respuesta de usuario a pregunta de seguridad.
    
    Las respuestas se almacenan hasheadas (como passwords).
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='security_answers',
        verbose_name='Usuario',
    )
    question = models.ForeignKey(
        SecurityQuestion,
        on_delete=models.CASCADE,
        verbose_name='Pregunta',
    )
    answer_hash = models.CharField(
        max_length=128,
        verbose_name='Respuesta (hash)',
        help_text='Respuesta hasheada',
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_security_answers'
        unique_together = [['user', 'question']]
        verbose_name = 'Respuesta Seguridad'
        verbose_name_plural = 'Respuestas Seguridad'
    
    def __str__(self):
        return f"{self.user.username} - {self.question.question}"
    
    def set_answer(self, raw_answer: str):
        """
        Guardar respuesta hasheada.
        
        Args:
            raw_answer: Respuesta en texto plano
        """
        # Normalizar: lowercase + strip
        normalized = raw_answer.lower().strip()
        self.answer_hash = make_password(normalized)
    
    def check_answer(self, raw_answer: str) -> bool:
        """
        Verificar respuesta.
        
        Args:
            raw_answer: Respuesta a verificar
            
        Returns:
            True si coincide, False si no
        """
        normalized = raw_answer.lower().strip()
        return check_password(normalized, self.answer_hash)
