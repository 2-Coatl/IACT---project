"""
Tests FASE 0.3: Bases de Datos (Versión Multiplataforma).
TDD: Tests PRIMERO, instalacion DESPUES.
"""
import pytest
import subprocess
import shutil
import socket
import sys
from pathlib import Path

# Markers
pytestmark = pytest.mark.integration

def check_port(host, port):
    """Verifica si un puerto está abierto (funciona en Windows y Linux)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) == 0

@pytest.fixture
def db_scripts_path(project_root):
    """Path scripts database."""
    return project_root / "deployment" / "database" / "scripts"

@pytest.fixture
def db_sql_path(project_root):
    """Path SQL files."""
    return project_root / "deployment" / "database" / "sql"

class TestPostgreSQL:
    """Tests PostgreSQL instalacion y configuracion de forma agnóstica."""
    
    def test_postgresql_scripts_exist(self, db_scripts_path):
        """Scripts PostgreSQL deben existir."""
        scripts = ["install_postgresql.sh", "setup_postgresql.sh"]
        for script in scripts:
            path = db_scripts_path / script
            assert path.exists(), f"{script} no existe"
    
    def test_postgresql_sql_exists(self, db_sql_path):
        """SQL PostgreSQL debe existir."""
        sql_file = db_sql_path / "setup_postgresql.sql"
        assert sql_file.exists()

    @pytest.mark.skipif(shutil.which("psql") is None, reason="Cliente psql no encontrado en el PATH")
    def test_postgresql_installed(self):
        """Verifica la instalación del cliente psql."""
        # shell=True es necesario en Windows para resolver el PATH correctamente
        result = subprocess.run(
            ["psql", "--version"],
            capture_output=True,
            text=True,
            shell=True if sys.platform == "win32" else False
        )
        assert result.returncode == 0
        assert "psql" in result.stdout.lower()
    
    def test_postgresql_service_reachable(self):
        """Verifica si el servicio PostgreSQL responde (reemplaza systemctl)."""
        assert check_port('localhost', 5432), "El servicio PostgreSQL no es accesible en el puerto 5432"

class TestMariaDB:
    """Tests MariaDB instalacion y configuracion de forma agnóstica."""
    
    def test_mariadb_scripts_exist(self, db_scripts_path):
        """Scripts MariaDB deben existir."""
        scripts = ["install_mariadb.sh", "setup_mariadb.sh"]
        for script in scripts:
            path = db_scripts_path / script
            assert path.exists()
    
    def test_mariadb_sql_exists(self, db_sql_path):
        """SQL MariaDB debe existir."""
        sql_file = db_sql_path / "setup_mariadb.sql"
        assert sql_file.exists()

    @pytest.mark.skipif(
        shutil.which("mariadb") is None and shutil.which("mysql") is None,
        reason="Cliente MariaDB/MySQL no encontrado"
    )
    def test_mariadb_installed(self):
        """Verifica la instalación del cliente MariaDB/MySQL."""
        cmd = "mariadb" if shutil.which("mariadb") else "mysql"
        result = subprocess.run(
            [cmd, "--version"],
            capture_output=True,
            text=True,
            shell=True if sys.platform == "win32" else False
        )
        assert result.returncode == 0
    
    def test_mariadb_service_reachable(self):
        """Verifica si el servicio MariaDB responde (reemplaza systemctl)."""
        assert check_port('localhost', 3306), "El servicio MariaDB no es accesible en el puerto 3306"

class TestDatabaseConfiguration:
    """Tests configuración dual database y permisos SQL."""
    
    def test_database_scripts_present(self, db_scripts_path):
        """Verifica presencia de scripts de despliegue."""
        scripts = [
            "install_postgresql.sh",
            "setup_postgresql.sh",
            "install_mariadb.sh",
            "setup_mariadb.sh",
        ]
        for script in scripts:
            assert (db_scripts_path / script).exists()

    def test_readonly_user_configuration(self, db_sql_path):
        """Usuario READ-ONLY debe estar definido en el SQL (CNST-003)."""
        mariadb_sql = db_sql_path / "setup_mariadb.sql"
        if mariadb_sql.exists():
            content = mariadb_sql.read_text()
            assert "ivr_readonly" in content
            assert "GRANT SELECT" in content
            # Verificamos que no tenga permisos de escritura amplios
            assert "GRANT ALL" not in content or "TO 'ivr_readonly'" not in content

    def test_dummy_data_in_sql(self, db_sql_path):
        """SQL debe incluir datos de prueba (10 registros)."""
        mariadb_sql = db_sql_path / "setup_mariadb.sql"
        if mariadb_sql.exists():
            content = mariadb_sql.read_text()
            assert "INSERT INTO" in content
            # Verificación básica de presencia de datos
            assert any(x in content for x in ["5551234567", "8001234567"])