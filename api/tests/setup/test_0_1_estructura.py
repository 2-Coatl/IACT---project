"""
Tests FASE 0.1: Estructura Directorios.

TDD: Tests PRIMERO, codigo DESPUES.
"""
import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Path raiz proyecto."""
    return Path("/tmp/iact-project")


@pytest.fixture
def callcentersite_path(project_root):
    """Path callcentersite/."""
    return project_root / "callcentersite"


class TestEstructuraRaiz:
    """Tests estructura raiz proyecto."""
    
    def test_project_directory_exists(self, project_root):
        """Directorio proyecto debe existir."""
        assert project_root.exists()
        assert project_root.is_dir()
    
    def test_git_initialized(self, project_root):
        """Git debe estar inicializado."""
        git_dir = project_root / ".git"
        assert git_dir.exists()
        assert git_dir.is_dir()


class TestEstructuraDocs:
    """Tests estructura docs/."""
    
    def test_docs_directory_exists(self, project_root):
        """docs/ debe existir."""
        docs = project_root / "docs"
        assert docs.exists()
        assert docs.is_dir()
    
    def test_docs_subdirectories(self, project_root):
        """Subdirectorios docs/ deben existir."""
        docs = project_root / "docs"
        
        # Subdirectorios requeridos
        subdirs = [
            "architecture/diagrams",
            "architecture/decisions",
            "reference/modules",
            "reference/api",
            "use-cases/flows",
            "use-cases/examples",
            "planning/sprints",
            "planning/risks",
            "conventions",
        ]
        
        for subdir in subdirs:
            path = docs / subdir
            assert path.exists(), f"{subdir} no existe"
            assert path.is_dir(), f"{subdir} no es directorio"
    
    def test_docs_readme_files(self, project_root):
        """README.md en secciones principales."""
        docs = project_root / "docs"
        
        readmes = [
            "architecture/README.md",
            "reference/README.md",
            "use-cases/README.md",
            "planning/README.md",
            "conventions/README.md",
        ]
        
        for readme in readmes:
            path = docs / readme
            assert path.exists(), f"{readme} no existe"
            assert path.is_file(), f"{readme} no es archivo"


class TestEstructuraCallcentersite:
    """Tests estructura callcentersite/."""
    
    def test_callcentersite_exists(self, callcentersite_path):
        """callcentersite/ debe existir."""
        assert callcentersite_path.exists()
        assert callcentersite_path.is_dir()
    
    def test_callcentersite_subdirs(self, callcentersite_path):
        """Subdirectorios callcentersite/."""
        subdirs = [
            "config/settings",
            "apps",
            "templates",
            "static/css",
            "static/js",
            "static/images",
            "media",
            "locale",
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            "tests/fixtures",
            "tests/factories",
        ]
        
        for subdir in subdirs:
            path = callcentersite_path / subdir
            assert path.exists(), f"{subdir} no existe"
            assert path.is_dir()
    
    def test_callcentersite_tests_init(self, callcentersite_path):
        """__init__.py en tests/."""
        tests = callcentersite_path / "tests"
        
        init_files = [
            "__init__.py",
            "unit/__init__.py",
            "integration/__init__.py",
            "e2e/__init__.py",
            "fixtures/__init__.py",
            "factories/__init__.py",
        ]
        
        for init in init_files:
            path = tests / init
            assert path.exists(), f"{init} no existe"
            assert path.is_file()


class TestEstructuraDeployment:
    """Tests estructura deployment/."""
    
    def test_deployment_exists(self, project_root):
        """deployment/ debe existir."""
        deploy = project_root / "deployment"
        assert deploy.exists()
        assert deploy.is_dir()
    
    def test_deployment_subdirs(self, project_root):
        """Subdirectorios deployment/."""
        deploy = project_root / "deployment"
        
        subdirs = ["apache", "docker", "nginx", "systemd", "scripts"]
        
        for subdir in subdirs:
            path = deploy / subdir
            assert path.exists(), f"{subdir} no existe"
    
    def test_requirements_directory(self, project_root):
        """requirements/ debe existir."""
        req = project_root / "requirements"
        assert req.exists()
        assert req.is_dir()
    
    def test_scripts_directory(self, project_root):
        """scripts/ con subdirectorios."""
        scripts = project_root / "scripts"
        assert scripts.exists()
        
        for subdir in ["dev", "prod"]:
            path = scripts / subdir
            assert path.exists()
    
    def test_logs_directory(self, project_root):
        """logs/ debe existir."""
        logs = project_root / "logs"
        assert logs.exists()
        assert logs.is_dir()


class TestGitkeepFiles:
    """Tests .gitkeep en directorios vacios."""
    
    def test_gitkeep_files_exist(self, project_root, callcentersite_path):
        """Archivos .gitkeep deben existir."""
        gitkeeps = [
            callcentersite_path / "media/.gitkeep",
            callcentersite_path / "locale/.gitkeep",
            project_root / "logs/.gitkeep",
        ]
        
        for gitkeep in gitkeeps:
            assert gitkeep.exists(), f"{gitkeep} no existe"
            assert gitkeep.is_file()
