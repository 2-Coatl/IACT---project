"""
Tests FASE 0.4: Proyecto Django.

TDD: Tests PRIMERO, settings DESPUES.

NOTA: Estos tests validan configuracion Django
sin necesidad de bases de datos instaladas.
"""
import pytest
from pathlib import Path
import importlib


@pytest.fixture
def project_root():
    """Path raiz proyecto."""
    return Path("/tmp/iact-project")


@pytest.fixture
def callcentersite_path(project_root):
    """Path callcentersite/."""
    return project_root / "callcentersite"


class TestDjangoProject:
    """Tests proyecto Django creado."""
    
    def test_manage_py_exists(self, callcentersite_path):
        """manage.py debe existir."""
        manage = callcentersite_path / "manage.py"
        assert manage.exists()
        assert manage.is_file()
    
    def test_manage_py_executable(self, callcentersite_path):
        """manage.py debe ser ejecutable."""
        manage = callcentersite_path / "manage.py"
        import stat
        assert manage.stat().st_mode & stat.S_IXUSR
    
    def test_config_package_exists(self, callcentersite_path):
        """Paquete config/ debe existir."""
        config = callcentersite_path / "config"
        assert config.exists()
        assert config.is_dir()
        assert (config / "__init__.py").exists()
    
    def test_settings_package_exists(self, callcentersite_path):
        """Paquete config/settings/ debe existir."""
        settings = callcentersite_path / "config" / "settings"
        assert settings.exists()
        assert settings.is_dir()
        assert (settings / "__init__.py").exists()


class TestSettingsFiles:
    """Tests archivos settings existentes."""
    
    def test_base_settings_exists(self, callcentersite_path):
        """settings/base.py debe existir."""
        base = callcentersite_path / "config" / "settings" / "base.py"
        assert base.exists()
        assert base.is_file()
    
    def test_development_settings_exists(self, callcentersite_path):
        """settings/development.py debe existir."""
        dev = callcentersite_path / "config" / "settings" / "development.py"
        assert dev.exists()
        assert dev.is_file()
    
    def test_testing_settings_exists(self, callcentersite_path):
        """settings/testing.py debe existir."""
        test = callcentersite_path / "config" / "settings" / "testing.py"
        assert test.exists()
        assert test.is_file()
    
    def test_production_settings_exists(self, callcentersite_path):
        """settings/production.py debe existir."""
        prod = callcentersite_path / "config" / "settings" / "production.py"
        assert prod.exists()
        assert prod.is_file()


class TestSettingsContent:
    """Tests contenido settings."""
    
    def test_base_settings_size(self, callcentersite_path):
        """base.py debe ser ~600 lineas."""
        base = callcentersite_path / "config" / "settings" / "base.py"
        lines = len(base.read_text().split('\n'))
        assert lines >= 500, f"base.py solo tiene {lines} lineas, esperado ~600"
    
    def test_base_settings_dual_database(self, callcentersite_path):
        """base.py debe configurar dual database."""
        base = callcentersite_path / "config" / "settings" / "base.py"
        content = base.read_text()
        
        assert "DATABASES" in content
        assert "'default'" in content
        assert "'ivr_legacy'" in content
        assert "postgresql" in content.lower()
        assert "mysql" in content.lower()
    
    def test_base_settings_session_db(self, callcentersite_path):
        """base.py debe configurar SESSION_ENGINE = db (CNST-002)."""
        base = callcentersite_path / "config" / "settings" / "base.py"
        content = base.read_text()
        
        assert "SESSION_ENGINE" in content
        assert "django.contrib.sessions.backends.db" in content
    
    def test_base_settings_throttling(self, callcentersite_path):
        """base.py debe configurar throttling (CNST-005)."""
        base = callcentersite_path / "config" / "settings" / "base.py"
        content = base.read_text()
        
        assert "DEFAULT_THROTTLE_CLASSES" in content
        assert "DEFAULT_THROTTLE_RATES" in content
    
    def test_base_settings_max_page_size(self, callcentersite_path):
        """base.py debe configurar MAX_PAGE_SIZE (CNST-005)."""
        base = callcentersite_path / "config" / "settings" / "base.py"
        content = base.read_text()
        
        assert "MAX_PAGE_SIZE" in content
        assert "1000" in content or "1_000" in content


class TestSettingsCompliance:
    """Tests compliance CNST en settings."""
    
    def test_no_sentry_in_base(self, callcentersite_path):
        """base.py NO debe configurar Sentry (CNST_TECNICAS)."""
        base = callcentersite_path / "config" / "settings" / "base.py"
        content = base.read_text().lower()
        
        # NO debe haber imports de sentry
        assert "import sentry_sdk" not in content
        assert "from sentry_sdk" not in content
    
    def test_no_sentry_in_production(self, callcentersite_path):
        """production.py NO debe configurar Sentry (CNST_TECNICAS)."""
        prod = callcentersite_path / "config" / "settings" / "production.py"
        content = prod.read_text().lower()
        
        assert "import sentry_sdk" not in content
        # Debe tener comentario PROHIBIDO
        assert "prohibido" in content or "sentry" in content
    
    def test_no_redis_in_production(self, callcentersite_path):
        """production.py NO debe usar Redis (CNST_TECNICAS)."""
        prod = callcentersite_path / "config" / "settings" / "production.py"
        content = prod.read_text().lower()
        
        assert "django_redis" not in content
        assert "rediscache" not in content
    
    def test_no_email_smtp_in_development(self, callcentersite_path):
        """development.py NO debe usar SMTP (CNST-001)."""
        dev = callcentersite_path / "config" / "settings" / "development.py"
        content = dev.read_text()
        
        # Debe usar console o dummy, NO smtp
        assert "smtp.EmailBackend" not in content
        assert "console.EmailBackend" in content or "dummy.EmailBackend" in content
    
    def test_no_email_smtp_in_testing(self, callcentersite_path):
        """testing.py NO debe usar SMTP (CNST-001)."""
        test = callcentersite_path / "config" / "settings" / "testing.py"
        content = test.read_text()
        
        assert "smtp.EmailBackend" not in content
        assert "locmem.EmailBackend" in content or "dummy.EmailBackend" in content
    
    def test_no_email_smtp_in_production(self, callcentersite_path):
        """production.py NO debe usar SMTP (CNST-001)."""
        prod = callcentersite_path / "config" / "settings" / "production.py"
        content = prod.read_text()
        
        assert "smtp.EmailBackend" not in content
        assert "dummy.EmailBackend" in content
        # Debe tener comentario PROHIBIDO
        assert "PROHIBIDO" in content or "prohibido" in content.lower()


class TestOtherFiles:
    """Tests otros archivos Django."""
    
    def test_urls_py_exists(self, callcentersite_path):
        """config/urls.py debe existir."""
        urls = callcentersite_path / "config" / "urls.py"
        assert urls.exists()
        assert urls.is_file()
    
    def test_wsgi_py_exists(self, callcentersite_path):
        """config/wsgi.py debe existir."""
        wsgi = callcentersite_path / "config" / "wsgi.py"
        assert wsgi.exists()
        assert wsgi.is_file()
    
    def test_db_router_exists(self, callcentersite_path):
        """config/db_router.py debe existir (CNST-003)."""
        router = callcentersite_path / "config" / "db_router.py"
        assert router.exists()
        assert router.is_file()
    
    def test_env_example_exists(self, callcentersite_path):
        """.env.example debe existir."""
        env = callcentersite_path / ".env.example"
        assert env.exists()
        assert env.is_file()


class TestDatabaseRouter:
    """Tests Database Router (CNST-003)."""
    
    def test_db_router_content(self, callcentersite_path):
        """db_router.py debe tener DatabaseRouter class."""
        router = callcentersite_path / "config" / "db_router.py"
        content = router.read_text()
        
        assert "class DatabaseRouter" in content
        assert "db_for_read" in content
        assert "db_for_write" in content
        assert "allow_migrate" in content
    
    def test_db_router_readonly_enforcement(self, callcentersite_path):
        """db_router.py debe enforcar READ-ONLY (CNST-003)."""
        router = callcentersite_path / "config" / "db_router.py"
        content = router.read_text()
        
        # Debe bloquear writes a ivr_legacy
        assert "ivr_legacy" in content
        assert "READ-ONLY" in content or "read-only" in content.lower()


class TestEnvExample:
    """Tests .env.example."""
    
    def test_env_has_django_settings(self, callcentersite_path):
        """.env.example debe incluir DJANGO_SETTINGS_MODULE."""
        env = callcentersite_path / ".env.example"
        content = env.read_text()
        
        assert "DJANGO_SETTINGS_MODULE" in content
    
    def test_env_has_databases(self, callcentersite_path):
        """.env.example debe incluir config databases."""
        env = callcentersite_path / ".env.example"
        content = env.read_text()
        
        # PostgreSQL
        assert "DB_NAME" in content
        assert "DB_USER" in content
        
        # MariaDB
        assert "IVR_DB_NAME" in content
        assert "IVR_DB_USER" in content
    
    def test_env_no_forbidden_vars(self, callcentersite_path):
        """.env.example NO debe incluir vars prohibidas."""
        env = callcentersite_path / ".env.example"
        content = env.read_text().lower()
        
        # NO email, sentry, redis, celery
        assert "email_" not in content or "prohibido" in content
        assert "sentry_" not in content or "prohibido" in content
        assert "redis_" not in content or "prohibido" in content
        assert "celery_" not in content or "prohibido" in content
