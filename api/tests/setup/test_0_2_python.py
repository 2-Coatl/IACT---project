"""
Tests FASE 0.2: Ambiente Python.

TDD: Tests PRIMERO.
"""
import pytest
from pathlib import Path


class TestVirtualenv:
    """Tests virtualenv."""
    
    def test_venv_directory_exists(self, callcentersite_path):
        """venv/ debe existir."""
        venv = callcentersite_path / "venv"
        assert venv.exists()
        assert venv.is_dir()
    
    def test_venv_bin_directory(self, callcentersite_path):
        """venv/bin/ debe existir."""
        venv_bin = callcentersite_path / "venv" / "bin"
        assert venv_bin.exists()
        assert venv_bin.is_dir()
    
    def test_venv_python_executable(self, callcentersite_path):
        """Python ejecutable en venv."""
        python = callcentersite_path / "venv" / "bin" / "python"
        assert python.exists() or (callcentersite_path / "venv" / "bin" / "python3").exists()
    
    def test_venv_pip_executable(self, callcentersite_path):
        """pip ejecutable en venv."""
        pip = callcentersite_path / "venv" / "bin" / "pip"
        assert pip.exists()
        assert pip.is_file()


class TestRequirements:
    """Tests requirements files."""
    
    def test_requirements_files_exist(self, project_root):
        """Archivos requirements/ deben existir."""
        req_dir = project_root / "requirements"
        
        files = [
            "base.txt",
            "development.txt",
            "testing.txt",
            "production.txt",
        ]
        
        for file in files:
            path = req_dir / file
            assert path.exists(), f"{file} no existe"
            assert path.is_file()
    
    def test_base_txt_no_sentry(self, project_root):
        """base.txt NO debe incluir sentry."""
        base = project_root / "requirements" / "base.txt"
        content = base.read_text()
        
        assert "sentry" not in content.lower()
        assert "sentry-sdk" not in content
    
    def test_base_txt_no_redis(self, project_root):
        """base.txt NO debe incluir redis."""
        base = project_root / "requirements" / "base.txt"
        content = base.read_text()
        
        assert "redis" not in content.lower() or "# NO redis" in content
        assert "django-redis" not in content
    
    def test_base_txt_no_celery(self, project_root):
        """base.txt NO debe incluir celery."""
        base = project_root / "requirements" / "base.txt"
        content = base.read_text()
        
        assert "celery" not in content.lower() or "NO Celery" in content
    
    def test_base_txt_includes_django(self, project_root):
        """base.txt DEBE incluir Django."""
        base = project_root / "requirements" / "base.txt"
        content = base.read_text()
        
        assert "Django==" in content
        assert "djangorestframework==" in content
    
    def test_production_txt_no_sentry(self, project_root):
        """production.txt NO debe incluir sentry."""
        prod = project_root / "requirements" / "production.txt"
        content = prod.read_text()
        
        assert "sentry-sdk" not in content
        assert "# NOTA: NO sentry-sdk" in content
