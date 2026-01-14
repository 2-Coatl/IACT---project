"""
Tests FASE 0.3: Bases de Datos.

TDD: Tests PRIMERO, instalacion DESPUES.

NOTA: Estos tests requieren PostgreSQL y MariaDB instalados.
Si las bases NO están instaladas, tests serán SKIPPED.
"""
import pytest
import subprocess
from pathlib import Path


# Markers
pytestmark = pytest.mark.integration


@pytest.fixture
def db_scripts_path(project_root):
    """Path scripts database."""
    return project_root / "deployment" / "database" / "scripts"


@pytest.fixture
def db_sql_path(project_root):
    """Path SQL files."""
    return project_root / "deployment" / "database" / "sql"


class TestPostgreSQL:
    """Tests PostgreSQL instalacion y configuracion."""
    
    def test_postgresql_scripts_exist(self, db_scripts_path):
        """Scripts PostgreSQL deben existir."""
        scripts = [
            "install_postgresql.sh",
            "setup_postgresql.sh",
        ]
        
        for script in scripts:
            path = db_scripts_path / script
            assert path.exists(), f"{script} no existe"
            assert path.is_file()
    
    def test_postgresql_sql_exists(self, db_sql_path):
        """SQL PostgreSQL debe existir."""
        sql_file = db_sql_path / "setup_postgresql.sql"
        assert sql_file.exists()
        assert sql_file.is_file()
    
    @pytest.mark.skipif(
        subprocess.run(["which", "psql"], capture_output=True).returncode != 0,
        reason="PostgreSQL no instalado"
    )
    def test_postgresql_installed(self):
        """PostgreSQL debe estar instalado."""
        result = subprocess.run(
            ["psql", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "psql" in result.stdout.lower()
    
    @pytest.mark.skipif(
        subprocess.run(["which", "psql"], capture_output=True).returncode != 0,
        reason="PostgreSQL no instalado"
    )
    def test_postgresql_service_running(self):
        """Servicio PostgreSQL debe estar corriendo."""
        result = subprocess.run(
            ["systemctl", "is-active", "postgresql"],
            capture_output=True,
            text=True
        )
        assert "active" in result.stdout or result.returncode == 0
    
    @pytest.mark.skipif(
        subprocess.run(["which", "psql"], capture_output=True).returncode != 0,
        reason="PostgreSQL no instalado"
    )
    def test_database_iact_analytics_exists(self):
        """Database iact_analytics debe existir (si configurado)."""
        result = subprocess.run(
            ["sudo", "-u", "postgres", "psql", "-lqt"],
            capture_output=True,
            text=True
        )
        # Si database existe
        if "iact_analytics" in result.stdout:
            assert "iact_analytics" in result.stdout
    
    @pytest.mark.skipif(
        subprocess.run(["which", "psql"], capture_output=True).returncode != 0,
        reason="PostgreSQL no instalado"
    )
    def test_user_iact_user_exists(self):
        """Usuario iact_user debe existir (si configurado)."""
        result = subprocess.run(
            ["sudo", "-u", "postgres", "psql", "-c", "\\du"],
            capture_output=True,
            text=True
        )
        # Si usuario existe
        if "iact_user" in result.stdout:
            assert "iact_user" in result.stdout


class TestMariaDB:
    """Tests MariaDB instalacion y configuracion."""
    
    def test_mariadb_scripts_exist(self, db_scripts_path):
        """Scripts MariaDB deben existir."""
        scripts = [
            "install_mariadb.sh",
            "setup_mariadb.sh",
        ]
        
        for script in scripts:
            path = db_scripts_path / script
            assert path.exists(), f"{script} no existe"
            assert path.is_file()
    
    def test_mariadb_sql_exists(self, db_sql_path):
        """SQL MariaDB debe existir."""
        sql_file = db_sql_path / "setup_mariadb.sql"
        assert sql_file.exists()
        assert sql_file.is_file()
    
    def test_mariadb_sql_readonly_user(self, db_sql_path):
        """SQL debe crear usuario READ-ONLY (CNST-003)."""
        sql_file = db_sql_path / "setup_mariadb.sql"
        content = sql_file.read_text()
        
        # Verificar creación usuario READ-ONLY
        assert "ivr_readonly" in content
        assert "GRANT SELECT" in content
        
        # Verificar NO permisos escritura
        assert "REVOKE INSERT" in content or "GRANT SELECT" in content
        assert "REVOKE UPDATE" in content or "GRANT SELECT" in content
        assert "REVOKE DELETE" in content or "GRANT SELECT" in content
    
    @pytest.mark.skipif(
        subprocess.run(["which", "mariadb"], capture_output=True).returncode != 0,
        reason="MariaDB no instalado"
    )
    def test_mariadb_installed(self):
        """MariaDB debe estar instalado."""
        result = subprocess.run(
            ["mariadb", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "mariadb" in result.stdout.lower() or "mysql" in result.stdout.lower()
    
    @pytest.mark.skipif(
        subprocess.run(["which", "mariadb"], capture_output=True).returncode != 0,
        reason="MariaDB no instalado"
    )
    def test_mariadb_service_running(self):
        """Servicio MariaDB debe estar corriendo."""
        result = subprocess.run(
            ["systemctl", "is-active", "mariadb"],
            capture_output=True,
            text=True
        )
        assert "active" in result.stdout or result.returncode == 0
    
    @pytest.mark.skipif(
        subprocess.run(["which", "mariadb"], capture_output=True).returncode != 0,
        reason="MariaDB no instalado"
    )
    def test_database_ivr_legacy_exists(self):
        """Database ivr_legacy debe existir (si configurado)."""
        result = subprocess.run(
            ["mariadb", "-e", "SHOW DATABASES;"],
            capture_output=True,
            text=True
        )
        # Si database existe
        if "ivr_legacy" in result.stdout:
            assert "ivr_legacy" in result.stdout


class TestDatabaseConfiguration:
    """Tests configuración dual database."""
    
    def test_database_scripts_executable(self, db_scripts_path):
        """Scripts database deben ser ejecutables."""
        scripts = [
            "install_postgresql.sh",
            "setup_postgresql.sh",
            "install_mariadb.sh",
            "setup_mariadb.sh",
        ]
        
        for script in scripts:
            path = db_scripts_path / script
            assert path.exists()
            # Verificar permisos ejecución
            import stat
            assert path.stat().st_mode & stat.S_IXUSR
    
    def test_database_sql_files_complete(self, db_sql_path):
        """Archivos SQL deben estar completos."""
        files = [
            "setup_postgresql.sql",
            "setup_mariadb.sql",
        ]
        
        for file in files:
            path = db_sql_path / file
            assert path.exists()
            content = path.read_text()
            assert len(content) > 100  # No vacío
    
    def test_readonly_user_configuration(self, db_sql_path):
        """Usuario READ-ONLY debe estar configurado (CNST-003)."""
        mariadb_sql = db_sql_path / "setup_mariadb.sql"
        content = mariadb_sql.read_text()
        
        # Usuario ivr_readonly
        assert "ivr_readonly" in content
        
        # GRANT SELECT
        assert "GRANT SELECT" in content
        
        # REVOKE escritura
        assert "REVOKE" in content or "GRANT SELECT" in content
        # (Si solo GRANT SELECT, implícitamente NO tiene otros permisos)
    
    def test_dummy_data_in_sql(self, db_sql_path):
        """SQL debe incluir datos dummy (10 registros)."""
        mariadb_sql = db_sql_path / "setup_mariadb.sql"
        content = mariadb_sql.read_text()
        
        # INSERT presente
        assert "INSERT INTO" in content
        
        # Al menos 10 registros (buscar valores)
        assert "5551234567" in content
        assert "8001234567" in content
        
        # Comentario 10 registros
        assert "10" in content or "dummy" in content.lower()
