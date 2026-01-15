# Fixtures de Datos

Fixtures JSON para cargar en tests.

## Uso

```python
@pytest.mark.django_db
def test_with_fixture():
    from django.core.management import call_command
    call_command('loaddata', 'tests/fixtures/sample_data.json')
    # Ahora tienes Center y Service en DB
    
    from apps.core.models import Center, Service
    assert Center.objects.count() == 1
    assert Service.objects.count() == 1
```

## Archivos

- `sample_data.json` - Datos básicos (Center, Service)

## Crear Nuevos Fixtures

```bash
# Desde modelos existentes
python manage.py dumpdata core.Center core.Service --indent=2 > tests/fixtures/new_fixture.json

# Específicos por PK
python manage.py dumpdata core.Center --pks=1,2,3 --indent=2 > tests/fixtures/centers.json
```
