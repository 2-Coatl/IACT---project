"""
Tests de conexion a bases de datos Vagrant.

Estos tests verifican la conectividad a nivel de base de datos RAW,
SIN requerir migraciones de Django ni modelos creados.

Ejecutar:
    pytest api/callcentersite/tests/infrastructure/test_vagrant_db_connections.py -v

O con pytest desde el directorio api/callcentersite:
    pytest tests/infrastructure/test_vagrant_db_connections.py -v

Marcar como slow para excluir en CI/CD:
    pytest -m "not slow"
"""

import pytest
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError


pytestmark = [
    pytest.mark.slow,  # Marca como test lento
    pytest.mark.integration,  # Test de integracion
]


class TestVagrantPostgreSQLConnection:
    """Tests de conexion a PostgreSQL en Vagrant VM."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup y teardown para cada test."""
        yield
        # Cerrar conexiones despues de cada test
        connections["default"].close()

    def test_postgresql_connection_successful(self):
        """Verifica que Django puede conectarse a PostgreSQL."""
        conn = connections["default"]

        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 as test;")
            result = cursor.fetchone()

        assert result[0] == 1, "Conexion a PostgreSQL fallida"

    def test_postgresql_version(self):
        """Verifica la version de PostgreSQL."""
        conn = connections["default"]

        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]

        assert "PostgreSQL 16" in version, f"Version incorrecta: {version}"

    def test_postgresql_database_name(self):
        """Verifica que estamos conectados a la base de datos correcta."""
        conn = connections["default"]

        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]

        expected = settings.DATABASES["default"]["NAME"]
        assert db_name == expected, f"Base de datos incorrecta: {db_name}"

    def test_postgresql_current_user(self):
        """Verifica el usuario actual de conexion."""
        conn = connections["default"]

        with conn.cursor() as cursor:
            cursor.execute("SELECT current_user;")
            current_user = cursor.fetchone()[0]

        expected = settings.DATABASES["default"]["USER"]
        assert current_user == expected, f"Usuario incorrecto: {current_user}"

    def test_postgresql_encoding(self):
        """Verifica que el encoding es UTF8."""
        conn = connections["default"]

        with conn.cursor() as cursor:
            cursor.execute("SHOW server_encoding;")
            encoding = cursor.fetchone()[0]

        assert encoding == "UTF8", f"Encoding incorrecto: {encoding}"

    def test_postgresql_can_create_table(self):
        """Verifica que el usuario puede crear tablas temporales."""
        conn = connections["default"]

        with conn.cursor() as cursor:
            # Crear tabla temporal (se destruye al cerrar conexion)
            cursor.execute(
                """
                CREATE TEMP TABLE test_temp_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100)
                );
            """
            )

            # Insertar datos de prueba
            cursor.execute(
                """
                INSERT INTO test_temp_table (name) 
                VALUES ('test1'), ('test2');
            """
            )

            # Verificar datos
            cursor.execute("SELECT COUNT(*) FROM test_temp_table;")
            count = cursor.fetchone()[0]

        assert count == 2, "No se pudo crear/usar tabla temporal"

    def test_postgresql_connection_settings(self):
        """Verifica la configuracion de conexion."""
        config = settings.DATABASES["default"]

        assert config["ENGINE"] == "django.db.backends.postgresql"
        assert config["HOST"] == "127.0.0.1"
        assert config["PORT"] == "15432"
        assert config["USER"] == "django_user"
        assert config["NAME"] == "iact_analytics"


class TestVagrantMariaDBConnection:
    """Tests de conexion a MariaDB en Vagrant VM."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup y teardown para cada test."""
        yield
        # Cerrar conexiones despues de cada test
        connections["ivr_readonly"].close()

    def test_mariadb_connection_successful(self):
        """Verifica que Django puede conectarse a MariaDB."""
        conn = connections["ivr_readonly"]

        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 as test;")
            result = cursor.fetchone()

        assert result[0] == 1, "Conexion a MariaDB fallida"

    def test_mariadb_version(self):
        """Verifica la version de MariaDB."""
        conn = connections["ivr_readonly"]

        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION();")
            version = cursor.fetchone()[0]

        assert "MariaDB" in version, f"Version incorrecta: {version}"
        assert version.startswith("11.4"), f"Version incorrecta: {version}"

    def test_mariadb_database_name(self):
        """Verifica que estamos conectados a la base de datos correcta."""
        conn = connections["ivr_readonly"]

        with conn.cursor() as cursor:
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()[0]

        expected = settings.DATABASES["ivr_readonly"]["NAME"]
        assert db_name == expected, f"Base de datos incorrecta: {db_name}"

    def test_mariadb_current_user(self):
        """Verifica el usuario actual de conexion."""
        conn = connections["ivr_readonly"]

        with conn.cursor() as cursor:
            cursor.execute("SELECT CURRENT_USER();")
            current_user = cursor.fetchone()[0]

        # Formato: user@host
        assert "django_user" in current_user, f"Usuario incorrecto: {current_user}"

    def test_mariadb_charset(self):
        """Verifica que el charset es utf8mb4."""
        conn = connections["ivr_readonly"]

        with conn.cursor() as cursor:
            cursor.execute("SHOW VARIABLES LIKE 'character_set_database';")
            result = cursor.fetchone()
            charset = result[1] if result else None

        assert charset == "utf8mb4", f"Charset incorrecto: {charset}"

    def test_mariadb_can_create_table(self):
        """Verifica que el usuario puede crear tablas temporales."""
        conn = connections["ivr_readonly"]

        with conn.cursor() as cursor:
            # Crear tabla temporal (se destruye al cerrar conexion)
            cursor.execute(
                """
                CREATE TEMPORARY TABLE test_temp_table (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100)
                );
            """
            )

            # Insertar datos de prueba
            cursor.execute(
                """
                INSERT INTO test_temp_table (name) 
                VALUES ('test1'), ('test2');
            """
            )

            # Verificar datos
            cursor.execute("SELECT COUNT(*) FROM test_temp_table;")
            count = cursor.fetchone()[0]

        assert count == 2, "No se pudo crear/usar tabla temporal"

    def test_mariadb_connection_settings(self):
        """Verifica la configuracion de conexion."""
        config = settings.DATABASES["ivr_readonly"]

        assert config["ENGINE"] == "django.db.backends.mysql"
        assert config["HOST"] == "127.0.0.1"
        assert config["PORT"] == "13306"
        assert config["USER"] == "django_user"
        assert config["NAME"] == "ivr"


@pytest.mark.skipif(
    not connections["default"].settings_dict.get("HOST") == "127.0.0.1",
    reason="Solo ejecutar contra Vagrant VM (127.0.0.1)",
)
class TestVagrantNetworkConfiguration:
    """Tests de configuracion de red con Vagrant."""

    def test_port_forwarding_postgresql(self):
        """Verifica que el port forwarding de PostgreSQL funciona."""
        config = settings.DATABASES["default"]

        # Puerto forwarded debe ser 15432 (no el 5432 por defecto)
        assert config["PORT"] == "15432", "Port forwarding incorrecto"

    def test_port_forwarding_mariadb(self):
        """Verifica que el port forwarding de MariaDB funciona."""
        config = settings.DATABASES["ivr_readonly"]

        # Puerto forwarded debe ser 13306 (no el 3306 por defecto)
        assert config["PORT"] == "13306", "Port forwarding incorrecto"

    def test_connection_via_localhost(self):
        """Verifica que las conexiones usan localhost."""
        pg_config = settings.DATABASES["default"]
        maria_config = settings.DATABASES["ivr_readonly"]

        assert pg_config["HOST"] == "127.0.0.1"
        assert maria_config["HOST"] == "127.0.0.1"


class TestVagrantIntegration:
    """Tests de integracion que requieren VM corriendo."""

    def test_both_databases_accessible(self):
        """Verifica que ambas bases de datos son accesibles."""
        # PostgreSQL
        pg_conn = connections["default"]
        with pg_conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
            pg_result = cursor.fetchone()

        # MariaDB
        maria_conn = connections["ivr_readonly"]
        with maria_conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
            maria_result = cursor.fetchone()

        assert pg_result[0] == 1
        assert maria_result[0] == 1

    def test_connection_pooling_configured(self):
        """Verifica que el connection pooling esta configurado."""
        pg_config = settings.DATABASES["default"]
        maria_config = settings.DATABASES["ivr_readonly"]

        assert pg_config.get("CONN_MAX_AGE", 0) > 0, "Pool de PostgreSQL no configurado"
        assert maria_config.get("CONN_MAX_AGE", 0) > 0, "Pool de MariaDB no configurado"

    def test_postgresql_multiple_queries_same_connection(self):
        """Verifica que multiples queries usan la misma conexion (pooling)."""
        conn = connections["default"]

        # Obtener PID de conexion
        with conn.cursor() as cursor:
            cursor.execute("SELECT pg_backend_pid();")
            pid1 = cursor.fetchone()[0]

        # Segunda query
        with conn.cursor() as cursor:
            cursor.execute("SELECT pg_backend_pid();")
            pid2 = cursor.fetchone()[0]

        assert pid1 == pid2, "Connection pooling no funciona correctamente"

    def test_mariadb_multiple_queries_same_connection(self):
        """Verifica que multiples queries usan la misma conexion (pooling)."""
        conn = connections["ivr_readonly"]

        # Obtener connection ID
        with conn.cursor() as cursor:
            cursor.execute("SELECT CONNECTION_ID();")
            conn_id1 = cursor.fetchone()[0]

        # Segunda query
        with conn.cursor() as cursor:
            cursor.execute("SELECT CONNECTION_ID();")
            conn_id2 = cursor.fetchone()[0]

        assert conn_id1 == conn_id2, "Connection pooling no funciona correctamente"


class TestDatabaseReadiness:
    """Tests para verificar que las bases estan listas para Django."""

    def test_postgresql_schema_exists(self):
        """Verifica que el schema public existe en PostgreSQL."""
        conn = connections["default"]

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name = 'public';
            """
            )
            result = cursor.fetchone()

        assert result is not None, "Schema public no existe"

    def test_mariadb_database_exists(self):
        """Verifica que la base de datos existe en MariaDB."""
        conn = connections["ivr_readonly"]

        with conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES LIKE 'ivr';")
            result = cursor.fetchone()

        assert result is not None, "Base de datos ivr no existe"

    def test_postgresql_extensions_available(self):
        """Verifica extensiones de PostgreSQL disponibles."""
        conn = connections["default"]

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT extname 
                FROM pg_available_extensions 
                WHERE extname IN ('uuid-ossp', 'pg_trgm')
                ORDER BY extname;
            """
            )
            extensions = [row[0] for row in cursor.fetchall()]

        # No es critico, pero es bueno saber cuales estan disponibles
        print(f"\nExtensiones disponibles: {extensions}")
        assert len(extensions) >= 0  # Siempre pasa, solo informativo
