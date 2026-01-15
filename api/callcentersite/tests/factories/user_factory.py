"""
Factory para User model.
"""
import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    """Factory User básico."""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override para usar create_user (hashea password)."""
        password = kwargs.pop('password', 'defaultpass123')
        user = model_class.objects.create_user(*args, **kwargs)
        user.set_password(password)
        user.save()
        return user


class AdminUserFactory(UserFactory):
    """Factory User admin."""
    
    username = factory.Sequence(lambda n: f'admin{n}')
    is_staff = True
    is_superuser = True
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Crear superuser."""
        password = kwargs.pop('password', 'admin123')
        
        return model_class.objects.create_superuser(
            username=kwargs.get('username'),
            email=kwargs.get('email'),
            password=password,
            first_name=kwargs.get('first_name', 'Admin'),
            last_name=kwargs.get('last_name', 'User')
        )
