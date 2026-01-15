import pytest
from django.contrib.auth.models import User
from apps.authentication.models import SecurityQuestion, UserSecurityAnswer


@pytest.mark.unit
@pytest.mark.django_db
class TestSecurityQuestion:
    """
    Tests para modelo SecurityQuestion.
    
    CNST-001: Recuperacion password SIN email.
    """
    
    def test_create_security_question(self):
        """Crear pregunta de seguridad."""
        question = SecurityQuestion.objects.create(
            question='Cual es tu color favorito?',
            is_active=True,
        )
        
        assert question.id is not None
        assert question.question == 'Cual es tu color favorito?'
        assert question.is_active is True
    
    def test_security_question_str(self):
        """__str__ devuelve la pregunta."""
        question = SecurityQuestion.objects.create(
            question='Nombre de tu mascota?'
        )
        
        assert str(question) == 'Nombre de tu mascota?'
    
    def test_security_question_unique(self):
        """Pregunta debe ser unica."""
        SecurityQuestion.objects.create(question='Test?')
        
        with pytest.raises(Exception):  # IntegrityError
            SecurityQuestion.objects.create(question='Test?')


@pytest.mark.unit
@pytest.mark.django_db
class TestUserSecurityAnswer:
    """Tests para modelo UserSecurityAnswer."""
    
    def test_user_security_answer_creation(self):
        """Usuario responde 3 preguntas seguridad."""
        user = User.objects.create_user('testuser', password='test123')
        
        q1 = SecurityQuestion.objects.create(question='Color favorito?')
        q2 = SecurityQuestion.objects.create(question='Ciudad natal?')
        q3 = SecurityQuestion.objects.create(question='Mascota?')
        
        ans1 = UserSecurityAnswer.objects.create(
            user=user, question=q1, answer_hash='azul_hash'
        )
        ans2 = UserSecurityAnswer.objects.create(
            user=user, question=q2, answer_hash='cdmx_hash'
        )
        ans3 = UserSecurityAnswer.objects.create(
            user=user, question=q3, answer_hash='perro_hash'
        )
        
        assert user.security_answers.count() == 3
        assert ans1.answer_hash == 'azul_hash'
    
    def test_set_answer_hashes_password(self):
        """set_answer() debe hashear la respuesta."""
        user = User.objects.create_user('testuser')
        question = SecurityQuestion.objects.create(question='Test?')
        
        answer = UserSecurityAnswer(user=user, question=question)
        answer.set_answer('Mi Respuesta')
        answer.save()
        
        # Hash debe ser diferente del texto plano
        assert answer.answer_hash != 'Mi Respuesta'
        assert answer.answer_hash != 'mi respuesta'
        
        # Debe estar hasheado (contiene $ separadores del formato Django)
        assert '$' in answer.answer_hash
        assert len(answer.answer_hash) > 20  # Hashes son largos
    
    def test_check_answer_validates_correctly(self):
        """check_answer() valida respuestas correctamente."""
        user = User.objects.create_user('testuser')
        question = SecurityQuestion.objects.create(question='Test?')
        
        answer = UserSecurityAnswer(user=user, question=question)
        answer.set_answer('Azul')
        answer.save()
        
        # Correcta (case-insensitive, strip spaces)
        assert answer.check_answer('azul') is True
        assert answer.check_answer('AZUL') is True
        assert answer.check_answer('  azul  ') is True
        
        # Incorrecta
        assert answer.check_answer('rojo') is False
