# 📜 RESTRICCIONES ARQUITECTÓNICAS - SISTEMA IACT

## PARTE 2/3: ARQUITECTURA, BASE DE DATOS Y PERFORMANCE

---

## 📋 INFORMACIÓN DEL DOCUMENTO

| Atributo | Valor |
|---|---|
| **Versión** | 1.0.0 - DEFINITIVA |
| **Fecha** | 19 Enero 2026 |
| **Proyecto** | Sistema IACT - IVR Analytics & Customer Tracking |
| **Parte** | 2/3 - Arquitectura, Base de Datos y Performance |
| **Continuación de** | PARTE 1/3 - Restricciones Críticas y Seguridad |

---

## 📋 CONTENIDO DE ESTA PARTE

**SECCIÓN 3: RESTRICCIONES DE ARQUITECTURA**
- 3.1 Antipatrones Prohibidos
- 3.2 Patrones Permitidos
- 3.3 Principios SOLID

**SECCIÓN 4: RESTRICCIONES DE BASE DE DATOS**
- 4.1 Estructura de BD IVR (Readonly)
- 4.2 BD Analytics (Write)
- 4.3 ETL

**SECCIÓN 5: RESTRICCIONES FUNCIONALES (SRS v2.0)**
- 5.1 Autenticación y Usuarios
- 5.2 Roles y Permisos (RBAC)
- 5.3 Reportes
- 5.4 Dashboard y Visualización
- 5.5 Alertas

**SECCIÓN 6: RESTRICCIONES DE PERFORMANCE (SLA)**
- 6.1 Tiempos de Respuesta
- 6.2 Límites de Datos

**SECCIÓN 7: RESTRICCIONES DE INFRAESTRUCTURA** ⭐ CORREGIDA
- 7.1 Despliegue On-Premise
- 7.2 Servidor Tradicional (NO Docker/Kubernetes)
- 7.3 Alternativas Permitidas
- 7.4 Justificación

---

## 🏗️ 3. RESTRICCIONES DE ARQUITECTURA

> ⚠️ **IMPORTANTE:** Estas restricciones definen los patrones arquitectónicos permitidos y prohibidos en el proyecto.

---

### 3.1 Antipatrones Prohibidos

**Código:** CNST-015 (implícito)

```yaml
❌ ANTIPATRÓN 1: GOD CLASS
  - Clases con más de 300 líneas
  - Clases con más de 15 métodos públicos
  - Clases que hacen "todo"
  - Ejemplo: User que maneja auth, permisos, reportes, etc

❌ ANTIPATRÓN 2: SPAGHETTI CODE
  - Código sin estructura clara
  - Dependencias circulares
  - Imports cruzados entre apps
  - Lógica de negocio en views

❌ ANTIPATRÓN 3: COPY-PASTE PROGRAMMING
  - Duplicación de código
  - Mismo código en múltiples archivos
  - Sin extracción a funciones/clases

❌ ANTIPATRÓN 4: MAGIC NUMBERS/STRINGS
  - Números/strings sin constantes
  - "Active", "Inactive" hardcoded
  - Status codes sin enum

❌ ANTIPATRÓN 5: HARDCODED CONFIGURATION
  - URLs hardcoded
  - Credentials en código
  - Configuración sin .env

❌ ANTIPATRÓN 6: PREMATURE OPTIMIZATION
  - Optimización sin métricas
  - Over-engineering
  - Código complejo innecesario

❌ ANTIPATRÓN 7: CALLBACK HELL
  - Callbacks anidados
  - Promesas sin async/await
  - Código no legible

❌ ANTIPATRÓN 8: FEATURE ENVY
  - Método usa más datos de otra clase
  - Violación de encapsulamiento
  - Método mal ubicado

❌ ANTIPATRÓN 9: PRIMITIVE OBSESSION
  - Usar primitivos en lugar de objetos
  - String para estados complejos
  - Dict en lugar de dataclass

❌ ANTIPATRÓN 10: SHOTGUN SURGERY
  - Cambio requiere tocar 10+ archivos
  - Lógica dispersa
  - Sin cohesión
```

**Ejemplo GOD CLASS (❌ PROHIBIDO):**
```python
# ❌ PROHIBIDO - God Class

class User(models.Model):
    """Clase que hace TODO."""
    
    # Datos de usuario
    username = models.CharField(max_length=150)
    email = models.EmailField()
    
    # Métodos de autenticación
    def authenticate(self, password):
        pass
    
    def generate_token(self):
        pass
    
    def refresh_token(self):
        pass
    
    # Métodos de permisos
    def has_permission(self, perm):
        pass
    
    def assign_role(self, role):
        pass
    
    def revoke_role(self, role):
        pass
    
    # Métodos de reportes
    def generate_report(self, type):
        pass
    
    def export_to_excel(self):
        pass
    
    # Métodos de auditoría
    def log_action(self, action):
        pass
    
    def get_audit_trail(self):
        pass
    
    # ... 20 métodos más
    # Total: 500+ líneas
```

**Ejemplo MAGIC NUMBERS (❌ PROHIBIDO):**
```python
# ❌ PROHIBIDO - Magic numbers/strings

def process_call(call):
    if call.status == "A":  # ¿Qué es "A"?
        return 1
    elif call.status == "B":  # ¿Qué es "B"?
        return 2
    
    if call.duration > 300:  # ¿Por qué 300?
        send_alert()
```

**Validación:**
```bash
# Detectar God Classes (>300 líneas)
find . -name "*.py" -exec sh -c 'wc -l "$1" | awk "\$1 > 300 {print \$2}"' _ {} \;

# Detectar duplicación (>5% duplicado)
radon mi -s -i apps/ --threshold=5

# Verificar complejidad ciclomática (>10)
radon cc apps/ -a -nb
```

---

### 3.2 Patrones Permitidos

**Código:** CNST-016 (implícito)

```yaml
✅ PATRÓN 1: SERVICE LAYER
  - Lógica de negocio en services/
  - Views delgados (orquestación)
  - Reutilización de lógica

✅ PATRÓN 2: REPOSITORY
  - Queries complejos en managers/
  - Abstracción de acceso a datos
  - Testeable independientemente

✅ PATRÓN 3: FACTORY
  - Creación de objetos complejos
  - Centralizar lógica de creación
  - Ejemplo: ReportFactory

✅ PATRÓN 4: STRATEGY
  - Algoritmos intercambiables
  - Ejemplo: ExportStrategy (CSV/Excel/PDF)
  - Evitar if/else largos

✅ PATRÓN 5: DECORATOR
  - Añadir funcionalidad sin modificar
  - Ejemplo: @require_function
  - Logging, caching, etc

✅ PATRÓN 6: ADAPTER
  - Integración con sistemas legacy
  - Ejemplo: IVRAdapter
  - Traducción de interfaces

✅ PATRÓN 7: FACADE
  - Interfaz simplificada
  - Ejemplo: ReportFacade
  - Ocultar complejidad
```

**Ejemplo SERVICE LAYER (✅ PERMITIDO):**
```python
# ✅ CORRECTO - Service Layer

# apps/reports/services.py
class ReportService:
    """Service para lógica de negocio de reportes."""
    
    @staticmethod
    def generate_abandoned_calls_report(start_date, end_date, format='excel'):
        """
        Genera reporte de llamadas abandonadas.
        
        Lógica de negocio:
        1. Validar fechas
        2. Extraer datos de BD IVR
        3. Aplicar transformaciones
        4. Generar archivo según formato
        5. Registrar en auditoría
        """
        # Validar
        if start_date > end_date:
            raise ValidationError("Fecha inicio > fecha fin")
        
        # Extraer datos
        calls = CallRecord.objects.filter(
            dFecha__range=(start_date, end_date),
            cEstado='Abandoned'
        ).values('dFecha', 'cMenu', 'iDuracion')
        
        # Transformar
        data = ReportTransformer.transform_abandoned_calls(calls)
        
        # Generar archivo
        file = ExportStrategy.get_strategy(format).export(data)
        
        # Auditar
        AuditService.log_report_generation(
            report_type='abandoned_calls',
            records=len(data)
        )
        
        return file

# apps/reports/views.py
class AbandonedCallsViewSet(viewsets.ViewSet):
    """View delgado - solo orquestación."""
    
    @require_function('RPT-001')
    def generate(self, request):
        # Solo orquestación, lógica en service
        try:
            file = ReportService.generate_abandoned_calls_report(
                start_date=request.data['start_date'],
                end_date=request.data['end_date'],
                format=request.data.get('format', 'excel')
            )
            return Response({'file_url': file.url})
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
```

**Ejemplo STRATEGY PATTERN (✅ PERMITIDO):**
```python
# ✅ CORRECTO - Strategy Pattern

# apps/reports/strategies.py
from abc import ABC, abstractmethod

class ExportStrategy(ABC):
    """Estrategia base de exportación."""
    
    @abstractmethod
    def export(self, data: list) -> File:
        pass
    
    @staticmethod
    def get_strategy(format: str):
        strategies = {
            'csv': CSVExportStrategy(),
            'excel': ExcelExportStrategy(),
            'pdf': PDFExportStrategy(),
        }
        return strategies.get(format)

class ExcelExportStrategy(ExportStrategy):
    """Exportación a Excel."""
    
    def export(self, data: list) -> File:
        workbook = Workbook()
        worksheet = workbook.active
        
        # Headers
        headers = ['Fecha', 'Menú', 'Duración']
        worksheet.append(headers)
        
        # Data
        for row in data:
            worksheet.append([row['fecha'], row['menu'], row['duracion']])
        
        # Save
        filename = f'report_{uuid.uuid4()}.xlsx'
        filepath = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
        workbook.save(filepath)
        
        return File(open(filepath, 'rb'))

# Uso
strategy = ExportStrategy.get_strategy('excel')
file = strategy.export(data)
```

**Ejemplo FACTORY PATTERN (✅ PERMITIDO):**
```python
# ✅ CORRECTO - Factory Pattern

# apps/reports/factories.py
class ReportFactory:
    """Factory para crear reportes según tipo."""
    
    @staticmethod
    def create_report(report_type: str, **params):
        """
        Crea reporte según tipo.
        
        Centraliza lógica de creación compleja.
        """
        reports = {
            'abandoned_calls': AbandonedCallsReport,
            'quarterly_metrics': QuarterlyMetricsReport,
            'customer_analysis': CustomerAnalysisReport,
        }
        
        report_class = reports.get(report_type)
        if not report_class:
            raise ValueError(f"Tipo de reporte inválido: {report_type}")
        
        # Crear con parámetros
        return report_class(**params)

# Uso
report = ReportFactory.create_report(
    report_type='abandoned_calls',
    start_date='2026-01-01',
    end_date='2026-01-31'
)
```

---

### 3.3 Principios SOLID

**Código:** CNST-017 (implícito)

```yaml
✅ S - SINGLE RESPONSIBILITY PRINCIPLE
  - Una clase = una responsabilidad
  - Una función = una tarea
  - Separación clara de concerns

✅ O - OPEN/CLOSED PRINCIPLE
  - Abierto a extensión
  - Cerrado a modificación
  - Usar herencia/composición

✅ L - LISKOV SUBSTITUTION PRINCIPLE
  - Subclases sustituibles
  - Contratos respetados
  - Sin sorpresas

✅ I - INTERFACE SEGREGATION PRINCIPLE
  - Interfaces específicas
  - No obligar a implementar innecesario
  - Clientes solo lo que necesitan

✅ D - DEPENDENCY INVERSION PRINCIPLE
  - Depender de abstracciones
  - No depender de implementaciones
  - Inyección de dependencias
```

**Ejemplo SINGLE RESPONSIBILITY (✅):**
```python
# ✅ CORRECTO - SRP

# Una clase = una responsabilidad

class User(models.Model):
    """Modelo de usuario - solo datos."""
    username = models.CharField(max_length=150)
    email = models.EmailField()

class AuthenticationService:
    """Servicio de autenticación - solo autenticar."""
    
    @staticmethod
    def authenticate(username, password):
        user = User.objects.get(username=username)
        if check_password(password, user.password):
            return user
        return None

class PermissionService:
    """Servicio de permisos - solo permisos."""
    
    @staticmethod
    def has_function(user, function_code):
        return UserFunctionAssignment.objects.filter(
            user=user,
            function__code=function_code,
            is_active=True
        ).exists()

class AuditService:
    """Servicio de auditoría - solo auditar."""
    
    @staticmethod
    def log_action(user, action, details):
        AuditLog.objects.create(
            user=user,
            action=action,
            details=details,
            ip_address=get_client_ip()
        )
```

**Ejemplo OPEN/CLOSED (✅):**
```python
# ✅ CORRECTO - Open/Closed

# Base abstracta - cerrada a modificación
class BaseReport(ABC):
    """Reporte base - no se modifica."""
    
    def generate(self):
        data = self.extract_data()
        transformed = self.transform_data(data)
        file = self.export_data(transformed)
        return file
    
    @abstractmethod
    def extract_data(self):
        pass
    
    @abstractmethod
    def transform_data(self, data):
        pass
    
    @abstractmethod
    def export_data(self, data):
        pass

# Extensión - abierto a extensión
class AbandonedCallsReport(BaseReport):
    """Reporte específico - extiende sin modificar base."""
    
    def extract_data(self):
        return CallRecord.objects.filter(cEstado='Abandoned')
    
    def transform_data(self, data):
        return [
            {
                'fecha': call.dFecha,
                'menu': call.cMenu,
                'duracion': call.iDuracion
            }
            for call in data
        ]
    
    def export_data(self, data):
        return ExcelExportStrategy().export(data)
```

**Ejemplo DEPENDENCY INVERSION (✅):**
```python
# ✅ CORRECTO - Dependency Inversion

# Abstracción
class IReportExporter(ABC):
    @abstractmethod
    def export(self, data: list) -> File:
        pass

# Implementaciones
class ExcelExporter(IReportExporter):
    def export(self, data: list) -> File:
        # Implementación Excel
        pass

class CSVExporter(IReportExporter):
    def export(self, data: list) -> File:
        # Implementación CSV
        pass

# Servicio depende de abstracción, no implementación
class ReportService:
    def __init__(self, exporter: IReportExporter):
        self.exporter = exporter  # Inyección de dependencia
    
    def generate(self, data):
        return self.exporter.export(data)

# Uso - inyectar dependencia
service = ReportService(exporter=ExcelExporter())
file = service.generate(data)
```

---

## 💾 4. RESTRICCIONES DE BASE DE DATOS

> ⚠️ **IMPORTANTE:** El proyecto usa arquitectura dual de bases de datos.

---

### 4.1 Estructura de BD IVR (Readonly)

**Código:** CNST-002 (ya documentado en PARTE 1)

```yaml
❌ PROHIBIDO:
  - Modificar estructura de tablas IVR
  - Crear índices en BD IVR
  - Crear triggers
  - Stored procedures que escriban
  - Cualquier DDL (CREATE/ALTER/DROP)

✅ OBLIGATORIO:
  - Solo SELECT queries
  - Usuario readonly: ivr_readonly
  - Conexión: 'ivr_legacy' en settings
  - Modelos Django con managed=False
  - Database router que bloquee writes

📋 TABLAS IVR LEGACY:
  - tbl_historico (CallRecord)
  - tbl_menus (MenuOption)
  - tbl_dids (DIDNumber)
  - Esquema latin1, charset legacy
```

**Modelos Django IVR:**
```python
# apps/ivr/models.py

class CallRecord(models.Model):
    """
    Registro de llamadas IVR.
    
    CRÍTICO: managed=False, readonly.
    """
    
    id = models.BigAutoField(primary_key=True, db_column='id')
    dFecha = models.DateTimeField(db_column='dFecha')
    cDID = models.CharField(max_length=20, db_column='cDID')
    cMenu = models.CharField(max_length=50, db_column='cMenu')
    cEstado = models.CharField(max_length=20, db_column='cEstado')
    iDuracion = models.IntegerField(db_column='iDuracion')
    
    class Meta:
        managed = False  # ✅ NO migraciones
        db_table = 'tbl_historico'
        ordering = ['-dFecha']
    
    def save(self, *args, **kwargs):
        """Bloquea saves accidentales."""
        raise NotImplementedError(
            "CallRecord es readonly. No se puede guardar."
        )

class MenuOption(models.Model):
    """Opción de menú IVR."""
    
    id = models.AutoField(primary_key=True, db_column='id')
    cMenu = models.CharField(max_length=50, db_column='cMenu')
    cDescripcion = models.CharField(max_length=200, db_column='cDescripcion')
    
    class Meta:
        managed = False
        db_table = 'tbl_menus'
```

**Database Router (ya documentado en PARTE 1):**
```python
# apps/ivr/router.py

class IVRRouter:
    """
    Router que protege BD IVR.
    
    CRÍTICO: Bloquea cualquier escritura a BD IVR.
    """
    
    ivr_apps = {'ivr'}
    
    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.ivr_apps:
            return 'ivr_legacy'
        return 'default'
    
    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.ivr_apps:
            return None  # ✅ Bloquea writes
        return 'default'
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.ivr_apps:
            return False  # ✅ No migraciones
        return db == 'default'
```

**Validación:**
```bash
# Verificar permisos en BD IVR
mysql -h ivr-server -u ivr_readonly -p -e "
SHOW GRANTS FOR 'ivr_readonly'@'%';
"
# Debe mostrar SOLO SELECT

# Verificar modelos managed=False
python manage.py shell -c "
from apps.ivr.models import CallRecord
assert CallRecord._meta.managed == False, 'Error: managed=True'
print('✅ Modelos IVR readonly')
"

# Intentar save (debe fallar)
python manage.py shell -c "
from apps.ivr.models import CallRecord
try:
    call = CallRecord(dFecha='2026-01-19', cDID='19020084')
    call.save()
    print('❌ ERROR: Save no bloqueado')
except NotImplementedError:
    print('✅ Save bloqueado correctamente')
"
```

---

### 4.2 BD Analytics (Write)

**Código:** CNST-018 (implícito)

```yaml
✅ PERMITIDO:
  - Permisos completos (SELECT/INSERT/UPDATE/DELETE)
  - Migraciones Django normales
  - Índices personalizados
  - Stored procedures de ETL
  - Triggers si necesario

✅ OBLIGATORIO:
  - Conexión 'default' en settings
  - Usuario: iact_app
  - Todas las apps excepto 'ivr'
  - Naming conventions según CLEAN_CODE v3.0.1

📋 ESQUEMA ANALYTICS:
  Database: iact_analytics
  Charset: utf8mb4
  Collation: utf8mb4_unicode_ci
  Engine: InnoDB
```

**Modelos Django Analytics:**
```python
# apps/analytics/models.py

from apps.core.models import TimeStampedModel, SoftDeleteMixin

class QuarterlyReport(TimeStampedModel, SoftDeleteMixin):
    """
    Reporte trimestral consolidado.
    
    Base de datos: iact_analytics (default)
    Permisos: Full (read/write)
    """
    
    quarter = models.CharField(max_length=10)  # Q1, Q2, Q3, Q4
    year = models.IntegerField()
    did = models.CharField(max_length=20)
    total_calls = models.IntegerField()
    abandoned_calls = models.IntegerField()
    avg_duration = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'quarterly_reports'
        managed = True  # ✅ Migraciones permitidas
        indexes = [
            models.Index(fields=['quarter', 'year']),
            models.Index(fields=['did']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['quarter', 'year', 'did'],
                name='unique_quarterly_report'
            )
        ]
    
    def __str__(self):
        return f"{self.quarter}-{self.year} - {self.did}"

class CustomerSegment(TimeStampedModel, SoftDeleteMixin):
    """Segmento de clientes (análisis)."""
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    criteria = models.JSONField()  # Criterios de segmentación
    
    class Meta:
        db_table = 'customer_segments'
        managed = True
```

**Migraciones:**
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar (solo a BD Analytics)
python manage.py migrate

# Verificar
python manage.py showmigrations
```

**Stored Procedure ETL:**
```sql
-- Stored Procedure en BD Analytics
-- /opt/iact/sql/sp_etl_daily.sql

DELIMITER $$

CREATE PROCEDURE sp_etl_daily()
BEGIN
    DECLARE v_start_date DATE;
    DECLARE v_end_date DATE;
    
    -- Calcular rango (últimas 24h)
    SET v_end_date = CURDATE();
    SET v_start_date = DATE_SUB(v_end_date, INTERVAL 1 DAY);
    
    -- Limpiar datos temporales
    DELETE FROM quarterly_reports_temp;
    
    -- Extraer de BD IVR (SELECT remoto)
    INSERT INTO quarterly_reports_temp (quarter, year, did, total_calls)
    SELECT 
        CONCAT('Q', QUARTER(dFecha)),
        YEAR(dFecha),
        cDID,
        COUNT(*)
    FROM ivr_legacy.tbl_historico
    WHERE dFecha BETWEEN v_start_date AND v_end_date
    GROUP BY QUARTER(dFecha), YEAR(dFecha), cDID;
    
    -- Consolidar en tabla final
    INSERT INTO quarterly_reports (quarter, year, did, total_calls, created_at)
    SELECT quarter, year, did, total_calls, NOW()
    FROM quarterly_reports_temp
    ON DUPLICATE KEY UPDATE
        total_calls = VALUES(total_calls),
        updated_at = NOW();
    
    -- Log
    INSERT INTO job_execution_log (job_name, status, records_processed)
    VALUES ('sp_etl_daily', 'completed', ROW_COUNT());
    
END$$

DELIMITER ;
```

**Validación:**
```bash
# Verificar permisos en BD Analytics
mysql -u iact_app -p -e "
USE iact_analytics;
SHOW GRANTS FOR 'iact_app'@'%';
"
# Debe mostrar ALL PRIVILEGES

# Verificar tablas
python manage.py dbshell -c "
SHOW TABLES;
"

# Verificar migraciones aplicadas
python manage.py showmigrations | grep -v "\[X\]" && echo "⚠️ Migraciones pendientes"
```

---

### 4.3 ETL

**Código:** CNST-019 (implícito)

```yaml
✅ PROCESO ETL:
  - Frecuencia: 6-12 horas (configurable)
  - Scheduler: APScheduler (no Celery)
  - Stored Procedure: sp_etl_daily()
  - Log: job_execution_log

✅ ESTRATEGIA:
  1. Extract: SELECT de BD IVR (readonly)
  2. Transform: Stored Procedure en BD Analytics
  3. Load: INSERT/UPDATE en BD Analytics

⚠️ RESTRICCIONES:
  - Sin impacto en BD IVR (solo lectura)
  - Proceso idempotente (re-ejecutable)
  - Timeout: 30 minutos máximo
  - Rollback automático si falla

❌ PROHIBIDO:
  - ETL real-time
  - Triggers en BD IVR
  - Polling continuo
  - Celery/RabbitMQ (ver CNST-013)
```

**Configuración ETL:**
```python
# apps/pipeline/management/commands/run_etl.py

from django.core.management.base import BaseCommand
from django.db import connection
from apps.pipeline.models import JobExecutionLog
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Ejecuta ETL diario desde stored procedure'
    
    def handle(self, *args, **options):
        """
        Ejecuta sp_etl_daily() en BD Analytics.
        
        Proceso:
        1. Validar última ejecución
        2. Ejecutar stored procedure
        3. Registrar resultado
        4. Notificar si falla
        """
        self.stdout.write('Iniciando ETL...')
        logger.info('ETL iniciado')
        
        # Crear log de ejecución
        job_log = JobExecutionLog.objects.create(
            job_name='etl_daily',
            status='running',
            start_time=timezone.now()
        )
        
        try:
            # Ejecutar stored procedure
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_etl_daily()")
                result = cursor.fetchone()
            
            # Actualizar log
            job_log.status = 'completed'
            job_log.end_time = timezone.now()
            job_log.records_processed = result[0] if result else 0
            job_log.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'ETL completado: {job_log.records_processed} registros'
                )
            )
            logger.info(f'ETL completado: {job_log.records_processed} registros')
            
        except Exception as e:
            # Registrar error
            job_log.status = 'failed'
            job_log.end_time = timezone.now()
            job_log.error_message = str(e)
            job_log.save()
            
            self.stdout.write(
                self.style.ERROR(f'ETL falló: {str(e)}')
            )
            logger.error(f'ETL falló: {str(e)}')
            
            # Notificar (buzón interno, no email)
            from apps.alerts.services import AlertService
            AlertService.send_internal_alert(
                recipients=['admin'],
                subject='ETL Falló',
                body=f'Error en ETL: {str(e)}'
            )
            
            raise
```

**Scheduler ETL:**
```python
# apps/pipeline/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

def run_etl():
    """Ejecuta ETL desde command."""
    logger.info("Scheduler: Iniciando ETL...")
    call_command('run_etl')

# Inicializar scheduler
scheduler = BackgroundScheduler({
    'apscheduler.timezone': 'America/Santiago'
})

# ETL cada 6 horas (00:00, 06:00, 12:00, 18:00)
scheduler.add_job(
    run_etl,
    trigger=CronTrigger(hour='0,6,12,18', minute=0),
    id='etl_job',
    name='ETL IVR → Analytics',
    replace_existing=True,
    max_instances=1,  # Solo una instancia a la vez
    coalesce=True,  # Si se perdió ejecución, ejecutar una sola vez
)

# Iniciar scheduler
scheduler.start()
logger.info("Scheduler ETL iniciado")
```

**Modelo Job Log:**
```python
# apps/pipeline/models.py

from django.db import models
from apps.core.models import TimeStampedModel

class JobExecutionLog(TimeStampedModel):
    """Log de ejecuciones de jobs (ETL, etc)."""
    
    job_name = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[
            ('running', 'En ejecución'),
            ('completed', 'Completado'),
            ('failed', 'Fallido'),
        ]
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    records_processed = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'job_execution_log'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['job_name', 'status']),
            models.Index(fields=['start_time']),
        ]
    
    def duration(self):
        """Duración en segundos."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
```

**Validación:**
```bash
# Verificar stored procedure
mysql -u iact_app -p iact_analytics -e "
SHOW PROCEDURE STATUS WHERE Name = 'sp_etl_daily';
"

# Verificar scheduler corriendo
python manage.py shell -c "
from apps.pipeline.scheduler import scheduler
jobs = scheduler.get_jobs()
print(f'Jobs programados: {len(jobs)}')
for job in jobs:
    print(f'- {job.name}: {job.next_run_time}')
"

# Ejecutar ETL manualmente (testing)
python manage.py run_etl

# Verificar logs
python manage.py shell -c "
from apps.pipeline.models import JobExecutionLog
last = JobExecutionLog.objects.first()
print(f'Último ETL: {last.status} - {last.records_processed} registros')
"
```

---

## 🎯 5. RESTRICCIONES FUNCIONALES (SRS v2.0)

> ⚠️ **IMPORTANTE:** Estas restricciones están definidas en el SRS v2.0 del proyecto.

---

### 5.1 Autenticación y Usuarios

**Código:** CNST-020 (implícito)

```yaml
✅ AUTENTICACIÓN:
  - Django Authentication System
  - Token-based para API (DRF)
  - Session-based para Admin
  - Password: PBKDF2 con 12+ caracteres

✅ RECUPERACIÓN:
  - 3 preguntas de seguridad
  - NO email (ver CNST-001)
  - Timeout: 24 horas

✅ BLOQUEO:
  - 3 intentos fallidos → bloqueo temporal (15 min)
  - 10 intentos fallidos → bloqueo permanente
  - Desbloqueo manual por admin

❌ PROHIBIDO:
  - OAuth externo (Google/Facebook)
  - Auth0, Okta (ver CNST-012)
  - Recuperación por email
  - CAPTCHA externo
```

**Configuración:**
```python
# settings/base.py

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Session timeout (15 minutos)
SESSION_COOKIE_AGE = 900
SESSION_SAVE_EVERY_REQUEST = True

# Login attempts
MAX_LOGIN_ATTEMPTS = 3
LOGIN_BLOCK_DURATION = 900  # 15 minutos
```

**Modelo Usuario Extendido:**
```python
# apps/users/models.py

from django.contrib.auth.models import AbstractUser
from apps.core.models import TimeStampedModel, SoftDeleteMixin

class User(AbstractUser, TimeStampedModel, SoftDeleteMixin):
    """
    Usuario del sistema IACT.
    
    Extiende AbstractUser con campos adicionales.
    """
    
    # Security questions
    security_question_1 = models.CharField(max_length=200)
    security_answer_1 = models.CharField(max_length=200)
    security_question_2 = models.CharField(max_length=200)
    security_answer_2 = models.CharField(max_length=200)
    security_question_3 = models.CharField(max_length=200)
    security_answer_3 = models.CharField(max_length=200)
    
    # Login attempts
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['username']
    
    def is_locked(self):
        """Verifica si usuario está bloqueado."""
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False
    
    def increment_failed_attempts(self):
        """Incrementa intentos fallidos."""
        self.failed_login_attempts += 1
        
        if self.failed_login_attempts >= 3:
            # Bloquear por 15 minutos
            self.locked_until = timezone.now() + timedelta(minutes=15)
        
        self.save()
    
    def reset_failed_attempts(self):
        """Resetea intentos fallidos."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save()
```

---

### 5.2 Roles y Permisos (RBAC)

**Código:** CNST-021 (implícito)

```yaml
✅ MODELO RBAC:
  - Flat RBAC (sin jerarquías)
  - Basado en funciones (42 funciones)
  - Grupos de funciones (10 agrupadores)
  - Separation of Duties (3 reglas SoD)
  - Ver: MODELO_RBAC_IACT_v6_0_0

✅ FUNCIONES:
  - 42 funciones atómicas
  - 9 módulos (Auth, Users, Access, Pipeline, Reports, Dashboard, Alerts, Audit, Logs)
  - Decorador: @require_function('FUNC-001')

⚠️ RESTRICCIONES:
  - Permisos temporales: máx 6 meses
  - Justificación: mín 20 caracteres
  - Auditoría: todos los cambios
  - SoD obligatorio
```

**Decorador RBAC:**
```python
# apps/access/decorators.py

from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from apps.access.models import UserFunctionAssignment

def require_function(function_code):
    """
    Decorador RBAC para endpoints.
    
    Verifica que usuario tenga función asignada.
    
    Usage:
        @require_function('RPT-001')
        def list(self, request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            if not user.is_authenticated:
                return Response(
                    {'error': 'No autenticado'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Verificar función
            has_function = UserFunctionAssignment.objects.filter(
                user=user,
                function__code=function_code,
                is_active=True,
                start_date__lte=timezone.now(),
            ).filter(
                models.Q(end_date__isnull=True) |
                models.Q(end_date__gte=timezone.now())
            ).exists()
            
            if not has_function:
                # Auditar
                from apps.audit.services import AuditService
                AuditService.log_unauthorized_access(
                    user=user,
                    function=function_code,
                    endpoint=request.path
                )
                
                return Response(
                    {'error': f'Función {function_code} requerida'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator
```

**Uso en Views:**
```python
# apps/reports/views.py

from apps.access.decorators import require_function

class ReportViewSet(viewsets.ViewSet):
    """ViewSet de reportes con RBAC."""
    
    @require_function('RPT-001')
    def list(self, request):
        """Lista reportes - requiere RPT-001."""
        reports = Report.objects.all()
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)
    
    @require_function('RPT-004')
    def export_csv(self, request, pk=None):
        """Exporta CSV - requiere RPT-004."""
        report = self.get_object()
        file = ReportService.export_csv(report)
        return Response({'file_url': file.url})
```

---

### 5.3 Reportes

**Código:** CNST-022 (implícito)

```yaml
✅ TIPOS DE REPORTES:
  1. Llamadas Abandonadas (UC-017)
  2. Análisis de Clientes (UC-018)
  3. Performance IVR (UC-019)

✅ EXPORTACIÓN:
  - Formatos: CSV, Excel, PDF
  - Límites por formato (ver CNST-007)
  - Throttling por rol
  - Timeout: 90 segundos

⚠️ LÍMITES:
  - CSV: 100,000 registros
  - Excel: 50,000 registros
  - PDF: 10,000 registros
  - Rango máximo: 2 años

❌ PROHIBIDO:
  - Reportes sin filtros (requiere fecha)
  - Exportación sin límites
  - Jobs asíncronos con Celery
```

**Funciones de Reportes:**
```python
# Del MODELO_RBAC_IACT_v6.0.0

RPT-001: ve_reportes          # Ve reportes tabulares
RPT-002: filtra_reportes      # Aplica filtros
RPT-003: exporta_csv          # Exporta CSV (100K)
RPT-004: exporta_excel        # Exporta Excel (50K)
RPT-005: exporta_pdf          # Exporta PDF (10K)
```

**Service Layer:**
```python
# apps/reports/services.py

from openpyxl import Workbook
import csv
from io import StringIO

class ReportService:
    """Service para generación de reportes."""
    
    MAX_RECORDS = {
        'csv': 100000,
        'excel': 50000,
        'pdf': 10000,
    }
    
    @staticmethod
    def generate_abandoned_calls(start_date, end_date, format='excel'):
        """
        Genera reporte de llamadas abandonadas.
        
        Límites:
        - Rango máximo: 2 años
        - Registros según formato
        - Timeout: 90 segundos
        """
        # Validar rango
        if (end_date - start_date).days > 730:  # 2 años
            raise ValidationError("Rango máximo: 2 años")
        
        # Extraer datos (con límite)
        limit = ReportService.MAX_RECORDS[format]
        calls = CallRecord.objects.filter(
            dFecha__range=(start_date, end_date),
            cEstado='Abandoned'
        )[:limit]
        
        # Transformar
        data = [
            {
                'fecha': call.dFecha.strftime('%Y-%m-%d'),
                'menu': call.cMenu,
                'duracion': call.iDuracion,
            }
            for call in calls
        ]
        
        # Exportar según formato
        if format == 'excel':
            return ReportService._export_excel(data, 'abandoned_calls')
        elif format == 'csv':
            return ReportService._export_csv(data, 'abandoned_calls')
        elif format == 'pdf':
            return ReportService._export_pdf(data, 'abandoned_calls')
    
    @staticmethod
    def _export_excel(data, filename):
        """Exporta a Excel."""
        workbook = Workbook()
        worksheet = workbook.active
        
        # Headers
        headers = list(data[0].keys())
        worksheet.append(headers)
        
        # Data
        for row in data:
            worksheet.append(list(row.values()))
        
        # Save
        filepath = os.path.join(
            settings.MEDIA_ROOT,
            'reports',
            f'{filename}_{uuid.uuid4()}.xlsx'
        )
        workbook.save(filepath)
        
        return filepath
```

---

### 5.4 Dashboard y Visualización

**Código:** CNST-023 (implícito)

```yaml
✅ DASHBOARDS:
  1. Métricas Trimestrales (UC-025)
  2. Análisis de Clientes
  3. Performance IVR

✅ WIDGETS:
  - KPIs estáticos
  - Gráficos predefinidos
  - Tablas tabulares
  - Sin real-time (ver CNST-003)

⚠️ ACTUALIZACIÓN:
  - Frecuencia: 6-12 horas (ETL)
  - Usuario debe refrescar (F5)
  - Mostrar timestamp última actualización

❌ PROHIBIDO:
  - Real-time updates
  - WebSockets
  - Auto-refresh
  - Polling continuo
```

**Funciones de Dashboard:**
```python
# Del MODELO_RBAC_IACT_v6.0.0

DSH-001: ve_dashboard         # Ve dashboard principal
DSH-002: ve_kpis              # Ve KPIs estáticos
DSH-003: ve_graficos          # Ve gráficos predefinidos
```

**Service Layer:**
```python
# apps/dashboard/services.py

class DashboardService:
    """Service para dashboards."""
    
    CACHE_TIMEOUT = 300  # 5 minutos (locmem)
    
    @staticmethod
    def get_quarterly_metrics(quarter, year, did=None):
        """
        Obtiene métricas trimestrales.
        
        Datos estáticos (6-12h desfase).
        Cache: 5 minutos en locmem.
        """
        cache_key = f'dashboard:quarterly:{quarter}:{year}:{did}'
        
        # Verificar cache
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Extraer de BD Analytics (NO IVR)
        metrics = QuarterlyReport.objects.filter(
            quarter=quarter,
            year=year
        )
        
        if did:
            metrics = metrics.filter(did=did)
        
        # Agregar
        result = metrics.aggregate(
            total_calls=models.Sum('total_calls'),
            avg_duration=models.Avg('avg_duration'),
        )
        
        # Timestamp última actualización ETL
        last_etl = JobExecutionLog.objects.filter(
            job_name='etl_daily',
            status='completed'
        ).order_by('-end_time').first()
        
        data = {
            'widgets': [
                {
                    'id': 'kpi-total-calls',
                    'type': 'kpi',
                    'label': 'Total Llamadas',
                    'value': result['total_calls'] or 0,
                },
                {
                    'id': 'kpi-avg-duration',
                    'type': 'kpi',
                    'label': 'Duración Promedio',
                    'value': f"{result['avg_duration'] or 0:.2f}s",
                },
            ],
            'last_updated': last_etl.end_time.isoformat() if last_etl else None,
            'next_update': (last_etl.end_time + timedelta(hours=6)).isoformat() if last_etl else None,
            'data_status': 'static',  # ⚠️ Datos estáticos
        }
        
        # Cache
        cache.set(cache_key, data, DashboardService.CACHE_TIMEOUT)
        
        return data
```

---

### 5.5 Alertas

**Código:** CNST-024 (implícito)

```yaml
✅ SISTEMA DE ALERTAS:
  - Buzón interno (NO email)
  - Modelo InternalMessage
  - UC-037: Recibir Notificación
  - UC-036 a UC-040: CRUD alertas

✅ TIPOS:
  - Informativa (baja prioridad)
  - Advertencia (media prioridad)
  - Crítica (alta prioridad)

⚠️ LÍMITES:
  - Máximo 50 destinatarios por alerta
  - Sin spam (throttling)
  - Retención: 90 días

❌ PROHIBIDO:
  - Email (ver CNST-001)
  - SMS (ver CNST-012)
  - Push notifications externas
```

**Funciones de Alertas:**
```python
# Del MODELO_RBAC_IACT_v6.0.0

ALR-001: ve_alertas           # Ve alertas recibidas
ALR-002: configura_alerta     # Configura alertas personales
ALR-003: envia_alerta         # Envía alerta manual
ALR-004: gestiona_suscripciones  # Gestiona suscripciones
ALR-005: marca_leida          # Marca alerta como leída
ALR-006: elimina_alerta       # Elimina alerta
```

**Service Layer:**
```python
# apps/alerts/services.py

from apps.alerts.models import InternalMessage
from apps.users.models import User

class AlertService:
    """Service para sistema de alertas internas."""
    
    MAX_RECIPIENTS = 50
    
    @staticmethod
    def send_internal_alert(recipients, subject, body, priority='medium'):
        """
        Envía alerta interna (buzón).
        
        NO email, NO SMS, NO push externo.
        Solo buzón interno del sistema.
        """
        # Validar destinatarios
        if len(recipients) > AlertService.MAX_RECIPIENTS:
            raise ValidationError(
                f"Máximo {AlertService.MAX_RECIPIENTS} destinatarios"
            )
        
        # Obtener usuarios
        if isinstance(recipients[0], str):
            users = User.objects.filter(username__in=recipients)
        else:
            users = recipients
        
        # Crear mensajes
        messages = []
        for user in users:
            message = InternalMessage.objects.create(
                recipient=user,
                subject=subject,
                body=body,
                priority=priority,
                is_read=False,
            )
            messages.append(message)
        
        return messages
    
    @staticmethod
    def mark_as_read(message_id, user):
        """Marca mensaje como leído."""
        message = InternalMessage.objects.get(
            id=message_id,
            recipient=user
        )
        message.is_read = True
        message.read_at = timezone.now()
        message.save()
```

---

## ⚡ 6. RESTRICCIONES DE PERFORMANCE (SLA)

> ⚠️ **IMPORTANTE:** Estas restricciones definen los SLA del proyecto.

---

### 6.1 Tiempos de Respuesta

**Código:** CNST-025 (implícito)

```yaml
✅ TIEMPOS OBJETIVO (p95):
  - GET endpoints: < 500ms
  - POST endpoints: < 1s
  - Reportes ligeros: < 5s
  - Reportes pesados: < 30s
  - Dashboard: < 2s
  - Login: < 1s

⚠️ TIMEOUTS:
  - Nginx: 90 segundos
  - Gunicorn: 90 segundos
  - Database queries: 60 segundos
  - ETL: 30 minutos

❌ PROHIBIDO:
  - Endpoints sin timeout
  - Queries sin límites
  - N+1 queries
  - Cargar datos completos en memoria
```

**Configuración Timeouts:**
```nginx
# /etc/nginx/sites-available/iact

server {
    # ...
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_read_timeout 90s;  # ✅ Timeout 90s
        proxy_connect_timeout 90s;
        proxy_send_timeout 90s;
    }
}
```

```python
# /opt/iact/config/gunicorn.conf.py

timeout = 90  # ✅ Timeout 90 segundos
graceful_timeout = 30
keepalive = 5
```

```python
# settings/base.py

# Database timeout
DATABASES = {
    'default': {
        # ...
        'OPTIONS': {
            'connect_timeout': 10,
            'read_timeout': 60,  # ✅ Query timeout 60s
            'write_timeout': 60,
        }
    }
}
```

**Optimizaciones Obligatorias:**
```python
# ✅ CORRECTO - select_related (JOINs)
users = User.objects.select_related('profile').all()

# ✅ CORRECTO - prefetch_related (M2M)
users = User.objects.prefetch_related('groups').all()

# ✅ CORRECTO - only() campos necesarios
calls = CallRecord.objects.only('dFecha', 'cMenu').all()

# ❌ INCORRECTO - N+1 queries
for user in users:
    print(user.profile.name)  # Query por cada user
```

**Validación:**
```bash
# Medir tiempos de respuesta
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost/api/v1/reports/"

# Detectar N+1 queries
python manage.py shell
>>> from django.db import connection
>>> from django.test.utils import override_settings
>>> with override_settings(DEBUG=True):
...     users = User.objects.all()
...     for user in users:
...         print(user.profile.name)
...     print(len(connection.queries))
```

---

### 6.2 Límites de Datos

**Código:** CNST-007 (ya documentado en PARTE 1)

```yaml
✅ LÍMITES DE EXPORTACIÓN:
  - CSV: 100,000 registros
  - Excel: 50,000 registros
  - PDF: 10,000 registros

✅ LÍMITES DE CONSULTA:
  - Rango máximo: 2 años
  - Paginación obligatoria
  - Page size: 50-100 registros

✅ THROTTLING:
  - Anónimos: 100 req/hora
  - Autenticados: 1,000 req/hora
  - Exportaciones: según rol
```

**Paginación Obligatoria:**
```python
# apps/utils/pagination.py

from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    """Paginación estándar."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

class LargePagination(PageNumberPagination):
    """Paginación para datasets grandes."""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500

# settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'apps.utils.pagination.StandardPagination',
    'PAGE_SIZE': 50,
}
```

**Throttling:**
```python
# settings/base.py

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    }
}

# Custom throttle para exportaciones
# apps/reports/throttling.py
from rest_framework.throttling import UserRateThrottle

class ExportThrottle(UserRateThrottle):
    """Throttle para exportaciones."""
    scope = 'export'

# settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'export': '10/day',  # 10 exportaciones por día
    }
}
```

---

## 🚀 7. RESTRICCIONES DE INFRAESTRUCTURA

> ⭐ **IMPORTANTE:** Esta sección ha sido COMPLETAMENTE REESCRITA en v1.0.0.  
> **CNST-014 documenta que Docker/Kubernetes están PROHIBIDOS.**

---

### 7.1 Despliegue On-Premise

**Código:** CNST-014 (documentado en PARTE 1)

```yaml
✅ ARQUITECTURA:
  - 100% on-premise en servidores propios
  - VM o bare metal (NO containers)
  - Sistema operativo: Ubuntu Server 24.04 LTS
  - Python 3.11+ con virtualenv
  - Nginx como reverse proxy
  - Gunicorn como application server
  - Supervisor para gestión de procesos

✅ STACK TECNOLÓGICO:
  - OS: Ubuntu 24.04 LTS
  - Python: 3.11+
  - Web Server: Nginx 1.24+
  - App Server: Gunicorn 21+
  - Database: MariaDB 10.11+
  - Process Manager: Supervisor 4.2+
  - Scheduler: APScheduler 3.10+

❌ PROHIBIDO:
  - Docker, Docker Compose
  - Kubernetes, K8s, OpenShift
  - Podman, LXC, LXD
  - Cualquier containerización
  - Cloud providers (AWS/GCP/Azure)
```

---

### 7.2 Servidor Tradicional (NO Docker/Kubernetes)

**Código:** CNST-014 (continuación)

**Estructura de Directorios:**
```bash
/opt/iact/
├── venv/                    # Virtualenv Python 3.11
│   ├── bin/
│   ├── lib/
│   └── ...
│
├── app/                     # Código Django
│   ├── config/             # Settings
│   ├── apps/               # Django apps
│   ├── manage.py
│   └── requirements/
│
├── static/                  # Archivos estáticos (Nginx)
│   ├── css/
│   ├── js/
│   └── img/
│
├── media/                   # Archivos subidos
│   ├── reports/
│   └── uploads/
│
├── logs/                    # Logs del sistema
│   ├── django.log
│   ├── gunicorn-access.log
│   ├── gunicorn-error.log
│   ├── nginx-access.log
│   └── nginx-error.log
│
├── config/                  # Configuración
│   ├── gunicorn.conf.py
│   ├── supervisor.conf
│   └── .env
│
└── scripts/                 # Scripts de deployment
    ├── deploy.sh
    ├── backup.sh
    ├── restart.sh
    └── health_check.sh
```

**Instalación Base:**
```bash
#!/bin/bash
# /opt/iact/scripts/install.sh

set -e

echo "🚀 Instalando IACT (Servidor Tradicional)..."

# 1. Dependencias del sistema
sudo apt-get update
sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    nginx \
    supervisor \
    mariadb-client \
    libmariadb-dev \
    git

# 2. Crear usuario iact
sudo useradd -r -m -d /opt/iact -s /bin/bash iact

# 3. Crear virtualenv
cd /opt/iact
sudo -u iact python3.11 -m venv venv

# 4. Instalar dependencias Python
sudo -u iact /opt/iact/venv/bin/pip install --upgrade pip
sudo -u iact /opt/iact/venv/bin/pip install -r /opt/iact/app/requirements/production.txt

# 5. Crear directorios
sudo -u iact mkdir -p /opt/iact/{static,media,logs}
sudo -u iact mkdir -p /opt/iact/media/{reports,uploads}

# 6. Configurar Nginx
sudo cp /opt/iact/config/nginx.conf /etc/nginx/sites-available/iact
sudo ln -s /etc/nginx/sites-available/iact /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 7. Configurar Supervisor
sudo cp /opt/iact/config/supervisor.conf /etc/supervisor/conf.d/iact.conf
sudo supervisorctl reread
sudo supervisorctl update

# 8. Migraciones
cd /opt/iact/app
sudo -u iact /opt/iact/venv/bin/python manage.py migrate --no-input

# 9. Collectstatic
sudo -u iact /opt/iact/venv/bin/python manage.py collectstatic --no-input

# 10. Crear superuser (interactivo)
sudo -u iact /opt/iact/venv/bin/python manage.py createsuperuser

echo "✅ Instalación completada"
echo "📝 Siguiente: Configurar /opt/iact/config/.env"
```

---

### 7.3 Alternativas Permitidas

**Para Desarrollo Local:**
```yaml
✅ DESARROLLO LOCAL (Equipo):
  - Docker/Docker Compose PERMITIDO
  - Solo en máquinas de desarrolladores
  - NO en servidores (dev/staging/prod)
  
  Razón: Facilita setup local del equipo
  Restricción: NO deployment con Docker
```

**Para CI/CD:**
```yaml
✅ CI/CD:
  - Scripts bash tradicionales
  - GitLab CI (sin Docker runners)
  - SSH deployment
  - rsync para sincronizar archivos
  
❌ PROHIBIDO:
  - Docker en CI/CD
  - Kubernetes en CD
  - Container registries
```

**Ejemplo CI/CD (GitLab):**
```yaml
# .gitlab-ci.yml (SIN Docker)

stages:
  - test
  - deploy

test:
  stage: test
  script:
    - python3.11 -m venv venv
    - source venv/bin/activate
    - pip install -r requirements/test.txt
    - python manage.py test
    - flake8 apps/
    - black --check apps/
  only:
    - branches

deploy_production:
  stage: deploy
  script:
    # SSH deployment tradicional
    - ssh iact@prod-server "/opt/iact/scripts/deploy.sh"
  only:
    - main
  when: manual
```

---

### 7.4 Justificación

**Razones para NO usar Docker/Kubernetes:**

```yaml
POLÍTICA CORPORATIVA:
  - Infraestructura tradicional establecida
  - Equipo de operaciones sin experiencia en containers
  - Servidores legacy sin soporte Docker
  
SEGURIDAD:
  - Containers considerados "menos seguros" por el cliente
  - Política de auditoría requiere instalación tradicional
  - Compliance con estándares internos
  
COMPLEJIDAD:
  - Proyecto no requiere escalado horizontal
  - Usuarios concurrentes: < 100
  - Complejidad de K8s innecesaria para el scope
  
CONTROL:
  - Control total sobre el servidor
  - Debugging más directo
  - Sin overhead de containers
```

**Consecuencias:**
```yaml
✅ VENTAJAS:
  - Stack familiar para el equipo
  - Debugging directo en el servidor
  - Sin overhead de containers
  - Cumple con políticas del cliente
  
⚠️ DESVENTAJAS:
  - Scaling horizontal más complejo
  - Deployment menos automatizado
  - Dependencias del OS
  - Setup más manual
```

---

## 📋 RESUMEN EJECUTIVO - PARTE 2

### Restricciones Documentadas

```
SECCIÓN 3: RESTRICCIONES DE ARQUITECTURA
├─ 3.1 Antipatrones Prohibidos (CNST-015)
├─ 3.2 Patrones Permitidos (CNST-016)
└─ 3.3 Principios SOLID (CNST-017)

SECCIÓN 4: RESTRICCIONES DE BASE DE DATOS
├─ 4.1 BD IVR Readonly (CNST-002)
├─ 4.2 BD Analytics Write (CNST-018)
└─ 4.3 ETL (CNST-019)

SECCIÓN 5: RESTRICCIONES FUNCIONALES
├─ 5.1 Autenticación (CNST-020)
├─ 5.2 RBAC (CNST-021)
├─ 5.3 Reportes (CNST-022)
├─ 5.4 Dashboard (CNST-023)
└─ 5.5 Alertas (CNST-024)

SECCIÓN 6: RESTRICCIONES DE PERFORMANCE
├─ 6.1 Tiempos de Respuesta (CNST-025)
└─ 6.2 Límites de Datos (CNST-007)

SECCIÓN 7: RESTRICCIONES DE INFRAESTRUCTURA ⭐ CORREGIDA
├─ 7.1 Despliegue On-Premise (CNST-014)
├─ 7.2 Servidor Tradicional
├─ 7.3 Alternativas Permitidas
└─ 7.4 Justificación

TOTAL: 14 restricciones adicionales
```

### Cambios Críticos en v1.0.0

```
⭐ SECCIÓN 7 COMPLETAMENTE REESCRITA:
❌ ELIMINADO: Todo sobre Docker/Kubernetes
✅ AGREGADO: Arquitectura on-premise tradicional
✅ AGREGADO: Scripts de instalación/deployment
✅ AGREGADO: Justificación técnica

ALINEACIÓN: CNST-014 (Parte 1) ↔ Sección 7 (Parte 2)
```

---

## 📚 REFERENCIAS

**Documentos Relacionados:**
- PARTE 1/3: Restricciones Críticas y Seguridad
- PARTE 3/3: Desarrollo, Auditoría y Referencias (siguiente)
- MODELO_RBAC_IACT_v6_0_0
- ARQUITECTURA_REAL_ETL_DEFINITIVA_v2_0_0

---

**Documento generado:** 2026-01-19  
**Versión:** 1.0.0  
**Estado:** ✅ DEFINITIVO  
**Parte:** 2/3
