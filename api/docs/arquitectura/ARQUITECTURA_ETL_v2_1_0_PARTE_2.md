---
version: 2.1.0
date: 2026-01-19
project: IACT (Sistema Call Center)
type: Arquitectura Técnica
categoria: arquitectura/diseño
titulo: Arquitectura Real del Sistema ETL - Versión Definitiva
componente: ETL (Extract, Transform, Load)
tecnologias: MariaDB, Django, Stored Procedures, APScheduler
scope: Sistema completo (IVR Legacy → Django → API)
audiencia: Desarrolladores, Arquitectos Técnicos
estado: definitivo
base: Arquitectura Real Implementada + RESTRICCIONES v1.0.0
partes: 2/3
---

# ARQUITECTURA REAL DEL SISTEMA ETL - VERSIÓN DEFINITIVA

**PARTE 2/3: ARQUITECTURA DJANGO Y APIS**

---

## 📋 CONTENIDO DE ESTA PARTE

4. [Arquitectura Django](#4-arquitectura-django)
5. [APIs y Endpoints](#5-apis-y-endpoints)
6. [Flujo de Datos Completo](#6-flujo-de-datos-completo)

---

<a name="4-arquitectura-django"></a>
## 4. ARQUITECTURA DJANGO

### 4.1 Apps y Responsabilidades

#### **4.1.1 Visión General**

```
PROYECTO: iact-call-center/

APPS PRINCIPALES:
├─ apps/ivr/              → Modelos IVR Legacy (readonly)
├─ apps/reports/          → Generación de reportes bajo demanda
├─ apps/dashboard/        → Visualización con widgets tiempo real
├─ apps/pipeline/         → Monitoreo estado ETL
├─ apps/access/           → Control de acceso RBAC
├─ apps/authentication/   → Autenticación de usuarios
└─ apps/users/            → Gestión de usuarios

APPS DE SOPORTE:
├─ apps/core/             → Modelos abstractos y mixins ViewSet
├─ apps/utils/            → Funciones helper y utilidades
└─ apps/audit/            → Auditoría de acciones
```

---

#### **4.1.2 Tabla de Responsabilidades**

```
┌────────────────┬────────────────────────────────────────────────────┐
│ App            │ Responsabilidad                                    │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/ivr/      │ - Modelos Django (managed=False)                   │
│                │ - Lectura readonly de MariaDB                      │
│                │ - Mapeo de tablas IVR Legacy                       │
│                │ - NO escribe, NO migraciones                       │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/reports/  │ - API endpoints de reportes (POST)                 │
│                │ - Generación bajo demanda (síncrona)               │
│                │ - Exportación (Excel, CSV)                         │
│                │ - Timeout: 90s máx (CNST-025)                      │
│                │ - RBAC: reports.view, reports.export.*             │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/dashboard/│ - API endpoints de dashboards (GET)                │
│                │ - Visualización tiempo real                        │
│                │ - Widgets (KPI, Charts, Tables)                    │
│                │ - Datos en vivo desde MariaDB                      │
│                │ - RBAC: dashboard.view, dashboard.export.*         │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/pipeline/ │ - Monitoreo ETL                                    │
│                │ - Consulta job_execution_log                       │
│                │ - API: GET /pipeline/status/                       │
│                │ - RBAC: pipeline.monitor                           │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/access/   │ - RBAC (Functions, Agrupadores)                    │
│                │ - Decorador @require_function                      │
│                │ - Middleware de auditoría                          │
│                │ - API: GET /access/functions/                      │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/users/    │ - Gestión de usuarios                              │
│                │ - Perfiles, preferencias                           │
│                │ - API CRUD de usuarios                             │
│                │ - RBAC: users.view, users.create, users.update     │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/core/     │ - TimeStampedModel (modelo abstracto)              │
│                │ - SoftDeleteMixin (modelo abstracto)               │
│                │ - SoftDeleteManager (manager)                      │
│                │ - SoftDeleteQuerySet (queryset)                    │
│                │ - SoftDeleteViewSetMixin (mixin ViewSet)           │
├────────────────┼────────────────────────────────────────────────────┤
│ apps/utils/    │ - StandardPagination (clase helper)                │
│                │ - LargePagination (clase helper)                   │
│                │ - custom_exception_handler() (función)             │
│                │ - get_client_ip() (función)                        │
│                │ - Helpers compartidos                              │
│                │ - NO tiene API                                     │
└────────────────┴────────────────────────────────────────────────────┘
```

---

#### **4.1.3 Separación Reports vs Dashboard**

```yaml
DECISIÓN: Apps separadas (no juntas)

Razón:
  reports/:
    - Generación BAJO DEMANDA (POST)
    - Proceso asíncrono (job en background)
    - Resultado: Archivo descargable (Excel/CSV)
    - Usuario solicita → Sistema genera → Usuario descarga
    - RBAC separado: reports.view, reports.export.excel
  
  dashboard/:
    - Visualización TIEMPO REAL (GET)
    - Proceso síncrono (respuesta inmediata)
    - Resultado: JSON con datos en vivo
    - Usuario consulta → Sistema retorna datos → Frontend renderiza
    - RBAC separado: dashboard.view, dashboard.export.excel

Alternativa considerada:
  - Todo en reports/ con param ?type=dashboard
  
Rechazada:
  - Mezcla responsabilidades
  - RBAC complejo
  - Difícil escalar

Estado: Definitivo
```

---

### 4.2 Modelos Django (managed=False)

#### **4.2.1 Patrón Base: Modelos IVR**

```python
# apps/ivr/models.py

from django.db import models


class BaseIVRModel(models.Model):
    """
    Modelo base abstracto para tablas IVR.
    
    CARACTERÍSTICAS:
    - managed=False → Django NO gestiona schema
    - db_table → Nombre EXACTO en MariaDB
    - app_label = 'ivr' → Database router usa 'ivr_legacy'
    
    IMPORTANTE:
    Todos los modelos IVR heredan de este base.
    """
    
    class Meta:
        abstract = True
        app_label = 'ivr'
        managed = False
```

---

#### **4.2.2 Modelo Completo: CallRecord**

```python
# apps/ivr/models.py

class CallRecord(BaseIVRModel):
    """
    Histórico de llamadas Q1 (Enero-Marzo) 2025.
    
    Tabla fuente: tbl_historico_t1_2025 (MariaDB)
    Django: READONLY (managed=False)
    
    Nomenclatura húngara del dominio IVR:
    - d* = date (fecha/hora)
    - c* = código/char (texto)
    - n* = numérico
    
    Esta nomenclatura NO es notación húngara moderna.
    Es la convención ORIGINAL del IVR Legacy que se MANTIENE.
    """
    
    # Primary key
    id = models.BigAutoField(primary_key=True)
    
    # Fecha/Hora
    dFecha = models.DateField(
        verbose_name="Fecha",
        help_text="Fecha de la llamada"
    )
    dHora = models.TimeField(
        verbose_name="Hora",
        help_text="Hora de la llamada"
    )
    dFechaHora = models.DateTimeField(
        verbose_name="Fecha y Hora",
        help_text="Timestamp completo"
    )
    
    # Identificación
    cDID_800Transfer = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_index=True,  # Índice para filtros por DID
        verbose_name="DID",
        help_text="DID que recibió la llamada (ej: 19020084 = Puebla)"
    )
    cTelefono_Origen = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_index=True,  # Índice para búsquedas por teléfono
        verbose_name="Teléfono Origen",
        help_text="Número del cliente llamante"
    )
    cMenu = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,  # Índice para filtros por menú
        verbose_name="Menú",
        help_text="Menú IVR seleccionado (ej: CREDITOS, SALDOS, OTROS)"
    )
    cOpcion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Opción",
        help_text="Opción dentro del menú (ej: 1, 2, 3)"
    )
    cSubOpcion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Sub-opción",
        help_text="Sub-opción si existe (ej: 1.1, 1.2)"
    )
    
    # Clasificación
    cTipoLlamada = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Tipo de Llamada",
        help_text="ENTRANTE, SALIENTE, INTERNA"
    )
    cEstado = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_index=True,  # Índice para filtros por estado
        verbose_name="Estado",
        help_text="COMPLETADA, ABANDONADA, TRANSFERIDA"
    )
    cResultado = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Resultado",
        help_text="Resultado final de la llamada"
    )
    
    # Métricas numéricas
    nDuracionSegundos = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Duración (seg)",
        help_text="Duración total de la llamada en segundos"
    )
    nTiempoEsperaSegundos = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Tiempo Espera (seg)",
        help_text="Tiempo en cola de espera"
    )
    nTiempoConversacionSegundos = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Tiempo Conversación (seg)",
        help_text="Tiempo hablando con agente"
    )
    
    # Agente
    cAgenteID = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="ID Agente",
        help_text="Identificador único del agente"
    )
    cAgenteName = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nombre Agente",
        help_text="Nombre completo del agente"
    )
    cCola = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cola",
        help_text="Cola de atención asignada"
    )
    
    # Ubicación
    cCiudad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ciudad",
        help_text="Ciudad del llamante"
    )
    cEstado = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Estado",
        help_text="Estado/Provincia del llamante"
    )
    
    # Metadatos
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado en",
        help_text="Timestamp de inserción en la tabla"
    )
    
    class Meta:
        app_label = 'ivr'
        managed = False  # ← CRÍTICO
        db_table = 'tbl_historico_t1_2025'  # ← Nombre EXACTO
        verbose_name = 'Histórico T1 2025'
        verbose_name_plural = 'Históricos T1 2025'
        ordering = ['-dFechaHora']
        indexes = [
            models.Index(fields=['dFecha'], name='idx_t1_fecha'),
            models.Index(fields=['cDID_800Transfer'], name='idx_t1_did'),
            models.Index(fields=['cMenu'], name='idx_t1_menu'),
            models.Index(fields=['cEstado'], name='idx_t1_estado'),
        ]
    
    def __str__(self):
        """Representación string."""
        return f"{self.cTelefono_Origen} - {self.dFechaHora} - {self.cMenu}"
    
    @property
    def duracion_minutos(self):
        """Duración en minutos (helper)."""
        if self.nDuracionSegundos:
            return round(self.nDuracionSegundos / 60, 2)
        return 0
    
    @property
    def fue_abandonada(self):
        """Verifica si la llamada fue abandonada."""
        return self.cEstado == 'ABANDONADA'
    
    @property
    def fue_completada(self):
        """Verifica si la llamada fue completada."""
        return self.cEstado == 'COMPLETADA'
```

---

#### **4.2.3 Modelos de Reportes Agregados**

```python
# apps/ivr/models.py

class QuarterlyReport(BaseIVRModel):
    """
    Reporte trimestral agregado.
    
    Generado por: Stored Procedure ETL (sp_etl_daily)
    Fuente: tbl_historico_t1/t2/t3_2025
    Django: READONLY (managed=False)
    
    Actualización: Diaria (acumulativa por trimestre)
    """
    
    id = models.BigAutoField(primary_key=True)
    
    # Dimensiones
    trimestre = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name="Trimestre",
        help_text="Q1, Q2, Q3"
    )
    anio = models.IntegerField(
        db_index=True,
        verbose_name="Año",
        help_text="Año del reporte (ej: 2025)"
    )
    fecha = models.DateField(
        db_index=True,
        verbose_name="Fecha",
        help_text="Fecha específica del dato agregado"
    )
    servicio_800 = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Servicio 800",
        help_text="Nombre del DID (Puebla, Nacional A, etc.)"
    )
    
    # Métricas de llamadas
    total_llamadas = models.IntegerField(
        default=0,
        verbose_name="Total Llamadas",
        help_text="Cantidad total de llamadas"
    )
    llamadas_completadas = models.IntegerField(
        default=0,
        verbose_name="Completadas",
        help_text="Llamadas finalizadas exitosamente"
    )
    llamadas_abandonadas = models.IntegerField(
        default=0,
        verbose_name="Abandonadas",
        help_text="Llamadas abandonadas por el cliente"
    )
    llamadas_transferidas = models.IntegerField(
        default=0,
        verbose_name="Transferidas",
        help_text="Llamadas transferidas a agente"
    )
    
    # Métricas de clientes
    clientes_unicos = models.IntegerField(
        default=0,
        verbose_name="Clientes Únicos",
        help_text="Cantidad de teléfonos únicos"
    )
    
    # Tiempos promedio (en segundos)
    duracion_promedio_seg = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Duración Promedio (seg)",
        help_text="Duración promedio de llamadas"
    )
    tiempo_espera_promedio_seg = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Espera Promedio (seg)",
        help_text="Tiempo promedio en cola"
    )
    tiempo_conversacion_promedio_seg = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Conversación Promedio (seg)",
        help_text="Tiempo promedio hablando con agente"
    )
    
    # Tasa calculada
    tasa_abandono = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Tasa Abandono (%)",
        help_text="Porcentaje de llamadas abandonadas"
    )
    
    # Metadatos
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado",
        help_text="Timestamp de creación del registro"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizado",
        help_text="Timestamp de última actualización"
    )
    
    class Meta:
        app_label = 'ivr'
        managed = False
        db_table = 'tbl_reporte_trimestral'
        verbose_name = 'Reporte Trimestral'
        verbose_name_plural = 'Reportes Trimestrales'
        ordering = ['-fecha', 'servicio_800']
        unique_together = [
            ('trimestre', 'anio', 'fecha', 'servicio_800')
        ]
    
    def __str__(self):
        return f"{self.trimestre} {self.anio} - {self.servicio_800} - {self.fecha}"
    
    @property
    def tasa_completadas(self):
        """Calcula tasa de llamadas completadas."""
        if self.total_llamadas > 0:
            return round(
                (self.llamadas_completadas / self.total_llamadas) * 100,
                2
            )
        return 0
    
    @property
    def promedio_llamadas_por_cliente(self):
        """Calcula promedio de llamadas por cliente único."""
        if self.clientes_unicos > 0:
            return round(self.total_llamadas / self.clientes_unicos, 2)
        return 0


class AbandonedCall(BaseIVRModel):
    """
    Reporte de llamadas abandonadas (RPT-TR-021).
    
    Generado por: q_REPTRIM021_LLAMADAS_ABDANDONADAS.sql
    Fuente: tbl_historico_t*/
    Django: READONLY (managed=False)
    """
    
    id = models.BigAutoField(primary_key=True)
    
    # Dimensiones
    trimestre = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name="Trimestre"
    )
    fecha = models.DateField(
        db_index=True,
        verbose_name="Fecha"
    )
    did = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="DID"
    )
    menu = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Menú"
    )
    
    # Métricas
    total_abandonadas = models.IntegerField(
        default=0,
        verbose_name="Total Abandonadas"
    )
    tiempo_espera_promedio_seg = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Espera Promedio (seg)"
    )
    
    # Clasificación por tiempo de espera
    abandonadas_antes_30seg = models.IntegerField(
        default=0,
        verbose_name="Abandonadas < 30seg",
        help_text="Abandonadas antes de 30 segundos"
    )
    abandonadas_30_60seg = models.IntegerField(
        default=0,
        verbose_name="Abandonadas 30-60seg",
        help_text="Abandonadas entre 30 y 60 segundos"
    )
    abandonadas_mas_60seg = models.IntegerField(
        default=0,
        verbose_name="Abandonadas > 60seg",
        help_text="Abandonadas después de 60 segundos"
    )
    
    # Tasa
    tasa_abandono = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Tasa Abandono (%)"
    )
    
    # Metadatos
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado"
    )
    
    class Meta:
        app_label = 'ivr'
        managed = False
        db_table = 'tbl_reporte_llamadas_abandonadas'
        verbose_name = 'Reporte Llamadas Abandonadas'
        verbose_name_plural = 'Reportes Llamadas Abandonadas'
        ordering = ['-fecha', 'menu']
    
    def __str__(self):
        return f"{self.trimestre} - {self.menu} - {self.total_abandonadas}"
    
    @property
    def porcentaje_abandono_rapido(self):
        """Porcentaje de abandonos antes de 30 seg."""
        if self.total_abandonadas > 0:
            return round(
                (self.abandonadas_antes_30seg / self.total_abandonadas) * 100,
                2
            )
        return 0
```

---

### 4.3 Database Router (IVR_LEGACY vs DEFAULT)

#### **4.3.1 Router Completo**

```python
# config/routers.py

class IVRRouter:
    """
    Database Router para separar IVR_LEGACY (MariaDB) de DEFAULT (PostgreSQL).
    
    REGLAS:
    1. apps/ivr/ → 'ivr_legacy' (MariaDB) para LECTURA
    2. apps/ivr/ → PROHIBIDO escritura (managed=False lo previene)
    3. Resto de apps → 'default' (PostgreSQL) para lectura/escritura
    4. apps/ivr/ → NO permite migraciones
    
    FUNCIONAMIENTO:
    - db_for_read(): Determina qué DB usar para SELECT
    - db_for_write(): Determina qué DB usar para INSERT/UPDATE/DELETE
    - allow_migrate(): Determina si permitir migraciones
    
    IMPORTANTE:
    Este router es CRÍTICO para la arquitectura.
    Sin él, Django intentaría leer/escribir apps/ivr/ en PostgreSQL.
    """
    
    # Apps que usan IVR_LEGACY (MariaDB)
    ivr_app_labels = {'ivr'}
    
    def db_for_read(self, model, **hints):
        """
        Determina qué database usar para lectura.
        
        Args:
            model: Modelo Django a leer
            **hints: Hints adicionales (instance, etc.)
        
        Returns:
            'ivr_legacy' si modelo está en apps/ivr/
            'default' para el resto
        """
        if model._meta.app_label in self.ivr_app_labels:
            return 'ivr_legacy'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """
        Determina qué database usar para escritura.
        
        IMPORTANTE:
        apps/ivr/ tiene managed=False, entonces Django NUNCA
        debería intentar escribir. Pero si lo intenta, forzamos
        a 'default' para evitar errores en MariaDB.
        
        Args:
            model: Modelo Django a escribir
            **hints: Hints adicionales
        
        Returns:
            'default' SIEMPRE (apps/ivr/ no escribe)
        """
        # apps/ivr/ NO escribe (managed=False)
        # Si por algún error se intenta, enviarlo a default
        if model._meta.app_label in self.ivr_app_labels:
            # Esto NO debería pasar (managed=False lo previene)
            # Pero si pasa, loggear advertencia
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Intento de escritura en modelo IVR: {model.__name__}. "
                "Esto no debería pasar (managed=False). "
                "Enviando a 'default' para evitar error."
            )
            return 'default'
        
        return 'default'
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Determina si permitir migraciones en una database.
        
        REGLAS:
        - apps/ivr/ → NO migraciones (managed=False)
        - Resto de apps → Solo migraciones en 'default'
        
        Args:
            db: Database name ('default', 'ivr_legacy')
            app_label: App label ('ivr', 'reports', etc.)
            model_name: Nombre del modelo (opcional)
            **hints: Hints adicionales
        
        Returns:
            False si:
              - app_label es 'ivr' (NUNCA migrar IVR)
              - db es 'ivr_legacy' (NUNCA migrar en MariaDB)
            True solo si:
              - db es 'default' Y app_label NO es 'ivr'
        """
        # REGLA 1: apps/ivr/ NUNCA permite migraciones
        if app_label in self.ivr_app_labels:
            return False
        
        # REGLA 2: Solo migrar en 'default'
        return db == 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Determina si permitir relaciones entre modelos.
        
        REGLAS:
        - Permitir relaciones dentro de la misma DB
        - Permitir relaciones entre IVR (MariaDB) y DEFAULT (PostgreSQL)
          (solo para ForeignKey que no requieren constraints en DB)
        
        Args:
            obj1: Primer modelo
            obj2: Segundo modelo
            **hints: Hints adicionales
        
        Returns:
            True si se permite la relación
            None si no hay regla específica (Django decide)
        """
        # Permitir relaciones dentro de la misma DB
        db1 = obj1._state.db or 'default'
        db2 = obj2._state.db or 'default'
        
        if db1 == db2:
            return True
        
        # Permitir relaciones cross-database si:
        # - Una es IVR (readonly) y otra es DEFAULT
        # - Solo para lectura (no constraints en DB)
        if (db1 == 'ivr_legacy' and db2 == 'default') or \
           (db1 == 'default' and db2 == 'ivr_legacy'):
            # Permitir pero SIN constraint en DB
            # Django maneja la relación en Python
            return True
        
        # Delegar a Django para otros casos
        return None
```

---

#### **4.3.2 Configuración en Settings**

```python
# config/settings/base.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='iact_db'),
        'USER': env('DB_USER', default='iact_user'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        'ATOMIC_REQUESTS': True,  # Transacciones automáticas
        'CONN_MAX_AGE': 600,  # Pool de conexiones
    },
    'ivr_legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('IVR_DB_NAME', default='ivr_database'),
        'USER': env('IVR_DB_USER', default='ivr_readonly'),
        'PASSWORD': env('IVR_DB_PASSWORD'),
        'HOST': env('IVR_DB_HOST', default='mariadb-server.local'),
        'PORT': env('IVR_DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'read_default_file': '/etc/mysql/my.cnf',  # Config adicional
        },
        'ATOMIC_REQUESTS': False,  # NO transacciones (readonly)
        'CONN_MAX_AGE': 300,  # Pool más corto (readonly)
        'AUTOCOMMIT': True,  # Autocommit para lecturas
    }
}

# Router
DATABASE_ROUTERS = ['config.routers.IVRRouter']

# IMPORTANTE: Usuario ivr_readonly debe tener SOLO permisos SELECT
# Configurar en MariaDB:
# GRANT SELECT ON ivr_database.* TO 'ivr_readonly'@'%';
# REVOKE INSERT, UPDATE, DELETE ON ivr_database.* FROM 'ivr_readonly'@'%';
```

---

### 4.4 Service Layer Pattern

#### **4.4.1 Estructura del Service Layer**

```
apps/reports/
├── __init__.py
├── models.py           → Modelos de la app (si los hay)
├── services.py         → ⭐ Service Layer (lógica de negocio)
├── views.py            → ViewSets DRF (capa web)
├── serializers.py      → Serializers DRF
├── permissions.py      → Permisos RBAC
└── urls.py             → Routing

PRINCIPIO:
- views.py → Delgado (solo HTTP, validación básica, RBAC)
- services.py → Gordo (lógica de negocio, queries, transformaciones)
```

---

#### **4.4.2 Ejemplo Completo: ReportService**

```python
# apps/reports/services.py

from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple
from django.db.models import QuerySet, Count, Avg, Sum
from django.core.exceptions import ValidationError

from apps.ivr.models import (
    CallRecord,
    CallRecord,
    CallRecord,
    QuarterlyReport,
    AbandonedCall
)
from apps.ivr.utils import get_trimestre_from_date
from apps.ivr.constants import ALLOWED_DIDS, get_did_name


class ReportService:
    """
    Servicio de reportes.
    
    Responsabilidades:
    - Validación de reglas de negocio
    - Consultas a MariaDB (IVR_LEGACY)
    - Agregaciones y transformaciones
    - Cálculos de métricas
    
    NO maneja:
    - HTTP (eso es views.py)
    - Serialización (eso es serializers.py)
    - RBAC (eso es permissions.py)
    
    IMPORTANTE:
    Este servicio es TESTEABLE sin Django web layer.
    Todos los tests unitarios NO requieren:
    - Request/Response
    - ViewSets
    - DRF
    """
    
    # Constantes (CNST-006, CNST-007)
    MAX_DATE_RANGE_DAYS = 730  # 2 años máximo
    MAX_EXPORT_RECORDS = 100000  # Límite de exportación
    
    @staticmethod
    def validate_date_range(
        start_date: date,
        end_date: date
    ) -> None:
        """
        Valida rango de fechas (CNST-006).
        
        Reglas:
        - start_date debe ser <= end_date
        - Rango no debe exceder 730 días (2 años)
        
        Args:
            start_date: Fecha inicio
            end_date: Fecha fin
        
        Raises:
            ValidationError: Si rango es inválido
        """
        if end_date < start_date:
            raise ValidationError(
                "Fecha fin debe ser mayor o igual a fecha inicio"
            )
        
        date_range_days = (end_date - start_date).days
        
        if date_range_days > ReportService.MAX_DATE_RANGE_DAYS:
            raise ValidationError(
                f"Rango máximo permitido: {ReportService.MAX_DATE_RANGE_DAYS} días (CNST-006). "
                f"Rango solicitado: {date_range_days} días"
            )
    
    @staticmethod
    def get_historico_model(fecha: date):
        """
        Determina qué modelo Historico usar según la fecha.
        
        Args:
            fecha: Fecha a evaluar
        
        Returns:
            CallRecord, CallRecord, o CallRecord
        
        Raises:
            ValueError: Si fecha está fuera de trimestres
        """
        trimestre = get_trimestre_from_date(fecha)
        
        mapping = {
            'Q1': CallRecord,
            'Q2': CallRecord,
            'Q3': CallRecord,
        }
        
        return mapping[trimestre]
    
    @staticmethod
    def get_call_records(
        start_date: date,
        end_date: date,
        did: Optional[str] = None,
        menu: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtiene registros de llamadas por rango de fechas.
        
        Si el rango cruza trimestres, consulta múltiples tablas
        y combina resultados.
        
        Args:
            start_date: Fecha inicio
            end_date: Fecha fin
            did: Filtro opcional por DID
            menu: Filtro opcional por menú
        
        Returns:
            Lista de diccionarios con registros
        
        Raises:
            ValidationError: Si rango es inválido
            ValueError: Si DID no es permitido
        """
        # Validar rango
        ReportService.validate_date_range(start_date, end_date)
        
        # Validar DID si se proporciona
        if did and did not in ALLOWED_DIDS:
            raise ValueError(f"DID {did} no permitido")
        
        # Determinar trimestres involucrados
        start_trimestre = get_trimestre_from_date(start_date)
        end_trimestre = get_trimestre_from_date(end_date)
        
        records = []
        
        # Caso 1: Mismo trimestre
        if start_trimestre == end_trimestre:
            Model = ReportService.get_historico_model(start_date)
            queryset = Model.objects.filter(
                dFecha__gte=start_date,
                dFecha__lte=end_date
            )
            
            if did:
                queryset = queryset.filter(cDID_800Transfer=did)
            if menu:
                queryset = queryset.filter(cMenu=menu)
            
            records = list(queryset.values())
        
        # Caso 2: Múltiples trimestres
        else:
            # Implementar lógica para cruzar trimestres
            # (simplificado aquí, ver implementación completa)
            pass
        
        # Validar límite CNST-007
        if len(records) > ReportService.MAX_EXPORT_RECORDS:
            raise ValidationError(
                f"Límite de {ReportService.MAX_EXPORT_RECORDS} registros excedido "
                f"(CNST-007). Total: {len(records)}"
            )
        
        return records
    
    @staticmethod
    def get_trimestral_metrics(
        trimestre: str,
        anio: int,
        did: Optional[str] = None
    ) -> Dict:
        """
        Obtiene métricas del reporte trimestral.
        
        Lee de tbl_reporte_trimestral (datos pre-agregados del ETL).
        
        Args:
            trimestre: 'Q1', 'Q2', 'Q3'
            anio: Año
            did: Filtro opcional por DID
        
        Returns:
            {
                'total_llamadas': int,
                'tasa_abandono': float,
                'clientes_unicos': int,
                'promedio_duracion': float,
                ...
            }
        """
        queryset = QuarterlyReport.objects.filter(
            trimestre=trimestre,
            anio=anio
        )
        
        if did:
            did_name = get_did_name(did)
            queryset = queryset.filter(servicio_800=did_name)
        
        # Agregar métricas
        metrics = queryset.aggregate(
            total_llamadas=Sum('total_llamadas'),
            total_completadas=Sum('llamadas_completadas'),
            total_abandonadas=Sum('llamadas_abandonadas'),
            total_transferidas=Sum('llamadas_transferidas'),
            clientes_unicos=Sum('clientes_unicos'),
            duracion_promedio=Avg('duracion_promedio_seg'),
        )
        
        # Calcular tasa de abandono
        if metrics['total_llamadas'] and metrics['total_llamadas'] > 0:
            metrics['tasa_abandono'] = round(
                (metrics['total_abandonadas'] / metrics['total_llamadas']) * 100,
                2
            )
        else:
            metrics['tasa_abandono'] = 0
        
        return metrics
    
    @staticmethod
    def get_abandonadas_detail(
        trimestre: str,
        did: Optional[str] = None,
        menu: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtiene detalle de llamadas abandonadas.
        
        Lee de tbl_reporte_llamadas_abandonadas.
        
        Args:
            trimestre: 'Q1', 'Q2', 'Q3'
            did: Filtro opcional por DID
            menu: Filtro opcional por menú
        
        Returns:
            Lista de diccionarios con detalle de abandonadas
        """
        queryset = AbandonedCall.objects.filter(
            trimestre=trimestre
        )
        
        if did:
            queryset = queryset.filter(did=did)
        if menu:
            queryset = queryset.filter(menu=menu)
        
        return list(queryset.values(
            'fecha',
            'did',
            'menu',
            'total_abandonadas',
            'tiempo_espera_promedio_seg',
            'abandonadas_antes_30seg',
            'abandonadas_30_60seg',
            'abandonadas_mas_60seg',
            'tasa_abandono'
        ))
```

---

#### **4.4.3 Uso del Service en ViewSet**

```python
# apps/reports/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.access.decorators import require_function
from apps.reports.services import ReportService
from apps.reports.serializers import ReportMetricsSerializer
from django.core.exceptions import ValidationError
from datetime import datetime


class ReportViewSet(viewsets.ViewSet):
    """
    API de reportes.
    
    Esta clase es DELGADA:
    - Maneja HTTP (request/response)
    - Valida permisos RBAC
    - Serializa datos
    - Delega lógica a ReportService
    
    NO contiene lógica de negocio.
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    @require_function('reports.view')
    def trimestral_metrics(self, request):
        """
        Obtiene métricas trimestrales.
        
        GET /api/v1/reports/trimestral-metrics/
        Query params:
          - trimestre: Q1/Q2/Q3 (requerido)
          - anio: YYYY (requerido)
          - did: DID (opcional)
        
        Returns:
            200: Métricas del trimestre
            400: Parámetros inválidos
        """
        # 1. Extract parámetros (capa web)
        trimestre = request.query_params.get('trimestre')
        anio = request.query_params.get('anio')
        did = request.query_params.get('did')
        
        # 2. Validación básica (capa web)
        if not trimestre or not anio:
            return Response(
                {'error': 'trimestre y anio son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            anio = int(anio)
        except ValueError:
            return Response(
                {'error': 'anio debe ser numérico'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. Delegar a servicio (lógica de negocio)
        try:
            metrics = ReportService.get_trimestral_metrics(
                trimestre=trimestre,
                anio=anio,
                did=did
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 4. Serializar (capa web)
        serializer = ReportMetricsSerializer(data=metrics)
        serializer.is_valid(raise_exception=True)
        
        # 5. Retornar (capa web)
        return Response(serializer.data)
```

---

### 4.5 Estructura de Archivos Completa

```
iact-call-center/
├── apps/
│   ├── ivr/
│   │   ├── __init__.py
│   │   ├── models.py              → Modelos (managed=False)
│   │   ├── constants.py           → DIDs, constantes
│   │   ├── utils.py               → Helpers (trimestres, etc.)
│   │   └── tests/
│   │       └── test_models.py
│   │
│   ├── reports/
│   │   ├── __init__.py
│   │   ├── models.py              → Modelos de reports (si hay)
│   │   ├── services.py            → ⭐ Service Layer
│   │   ├── views.py               → ViewSets DRF
│   │   ├── serializers.py         → Serializers DRF
│   │   ├── permissions.py         → Permisos RBAC
│   │   ├── urls.py                → Routing
│   │   └── tests/
│   │       ├── test_services.py   → Tests del servicio
│   │       └── test_views.py      → Tests de API
│   │
│   ├── dashboard/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── services.py            → DashboardService
│   │   ├── views.py               → DashboardViewSet
│   │   ├── serializers.py
│   │   ├── widgets.py             → Widget system
│   │   └── tests/
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── services.py            → ETLMonitoringService
│   │   ├── views.py               → PipelineViewSet
│   │   ├── serializers.py
│   │   └── tests/
│   │
│   ├── access/
│   │   ├── __init__.py
│   │   ├── models.py              → Function, Agrupador
│   │   ├── services.py            → AccessService
│   │   ├── decorators.py          → @require_function
│   │   ├── middleware.py          → AccessAuditMiddleware
│   │   ├── views.py
│   │   └── tests/
│   │
│   └── utils/
│       ├── __init__.py
│       ├── models.py              → Modelos abstractos (TimeStampedModel, SoftDeleteMixin)
│       ├── helpers.py
│       └── exceptions.py
│
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py                → Settings base
│   │   ├── development.py
│   │   └── production.py
│   ├── routers.py                 → ⭐ IVRRouter
│   ├── urls.py                    → URL root
│   └── wsgi.py
│
├── docs/
│   ├── arquitectura/
│   │   └── diseño/
│   │       └── ARQUITECTURA_REAL_ETL_DEFINITIVA_v1_0_0_PARTE_*.md
│   └── soporte/
│       └── CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1_PARTE_*.md
│
├── manage.py
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

---

**CONTINÚA EN SECCIÓN 5: APIs y Endpoints...**

<a name="5-apis-y-endpoints"></a>
## 5. APIS Y ENDPOINTS

### 5.1 Endpoints de Reportes (POST)

#### **5.1.1 Visión General**

```
REPORTES (7 endpoints):
Método: POST (generación bajo demanda)
Base URL: /api/v1/reports/

Endpoints:
1. POST /api/v1/reports/llamadas-abandonadas/
2. POST /api/v1/reports/clientes-unicos/
3. POST /api/v1/reports/promedio-clientes/
4. POST /api/v1/reports/clientes-menu/
5. POST /api/v1/reports/llamadas-menu/
6. POST /api/v1/reports/detalle-transferencias/
7. POST /api/v1/reports/menu-errores/

RBAC:
- reports.view: Ver reportes (cualquier tipo)
- reports.export.excel: Exportar Excel
- reports.export.csv: Exportar CSV
```

---

#### **5.1.2 Endpoint 1: Llamadas Abandonadas**

```python
# apps/reports/views.py

class AbandonedCallViewSet(viewsets.ViewSet):
    """
    Reporte de llamadas abandonadas (RPT-TR-021).
    
    POST /api/v1/reports/llamadas-abandonadas/
    """
    
    permission_classes = [IsAuthenticated]
    
    @require_function('reports.view')
    def create(self, request):
        """
        Genera reporte de llamadas abandonadas.
        
        Request Body:
        {
            "trimestre": "Q1",
            "did": "19020084",  // Opcional
            "menu": "CREDITOS", // Opcional
            "formato": "excel"  // excel|csv
        }
        
        Response 200:
        {
            "status": "completed",
            "data": [
                {
                    "fecha": "2025-01-15",
                    "did": "19020084",
                    "menu": "CREDITOS",
                    "total_abandonadas": 45,
                    "tiempo_espera_promedio_seg": 62,
                    "abandonadas_antes_30seg": 10,
                    "abandonadas_30_60seg": 20,
                    "abandonadas_mas_60seg": 15,
                    "tasa_abandono": 12.5
                },
                ...
            ],
            "total_records": 150,
            "download_url": "/media/reports/llamadas_abandonadas_Q1_2025.xlsx"
        }
        """
        # Validar serializer
        serializer = AbandonedCallRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extraer datos
        trimestre = serializer.validated_data['trimestre']
        did = serializer.validated_data.get('did')
        menu = serializer.validated_data.get('menu')
        formato = serializer.validated_data.get('formato', 'excel')
        
        # Delegar a servicio
        try:
            data = ReportService.get_abandonadas_detail(
                trimestre=trimestre,
                did=did,
                menu=menu
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generar archivo
        if formato == 'excel':
            file_path = ReportService.generate_excel(
                data=data,
                filename=f'llamadas_abandonadas_{trimestre}_{datetime.now().strftime("%Y%m%d")}'
            )
        else:  # csv
            file_path = ReportService.generate_csv(
                data=data,
                filename=f'llamadas_abandonadas_{trimestre}_{datetime.now().strftime("%Y%m%d")}'
            )
        
        # Retornar
        return Response({
            'status': 'completed',
            'data': data[:10],  # Primeros 10 para preview
            'total_records': len(data),
            'download_url': f'/media/reports/{os.path.basename(file_path)}'
        })
```

**Request/Response Ejemplo:**

```bash
# Request
POST /api/v1/reports/llamadas-abandonadas/
Authorization: Bearer <token>
Content-Type: application/json

{
    "trimestre": "Q1",
    "did": "19020084",
    "formato": "excel"
}

# Response 200
{
    "status": "completed",
    "data": [
        {
            "fecha": "2025-01-15",
            "did": "19020084",
            "menu": "CREDITOS",
            "total_abandonadas": 45,
            "tiempo_espera_promedio_seg": 62,
            "abandonadas_antes_30seg": 10,
            "abandonadas_30_60seg": 20,
            "abandonadas_mas_60seg": 15,
            "tasa_abandono": 12.5
        }
    ],
    "total_records": 150,
    "download_url": "/media/reports/llamadas_abandonadas_Q1_20260118.xlsx"
}
```

---

#### **5.1.3 Endpoint 2: Clientes Únicos**

```python
class UniqueClientViewSet(viewsets.ViewSet):
    """
    Reporte de clientes únicos (RPT-TR-011).
    
    POST /api/v1/reports/clientes-unicos/
    """
    
    @require_function('reports.view')
    def create(self, request):
        """
        Genera reporte de clientes únicos.
        
        Request Body:
        {
            "trimestre": "Q1",
            "did": "19020084",  // Opcional
            "formato": "excel"
        }
        
        Response 200:
        {
            "status": "completed",
            "data": [
                {
                    "fecha": "2025-01-15",
                    "did": "19020084",
                    "total_clientes_unicos": 1250,
                    "total_llamadas": 2500,
                    "promedio_llamadas_por_cliente": 2.0
                },
                ...
            ],
            "total_records": 90,
            "download_url": "/media/reports/clientes_unicos_Q1_2025.xlsx"
        }
        """
        # Implementación similar a AbandonedCallViewSet
        pass
```

---

#### **5.1.4 Endpoint 3: Detalle de Transferencias**

```python
class DetalleTransferenciasViewSet(viewsets.ViewSet):
    """
    Reporte detalle de transferencias (RPT-DET-001).
    
    POST /api/v1/reports/detalle-transferencias/
    
    Basado en: q_REP_DETALLE_TRANSFERENCIA_MENU_OPCION-v.0.3.1.sql
    """
    
    @require_function('reports.view')
    def create(self, request):
        """
        Request Body:
        {
            "trimestre": "Q2",
            "menu": "CREDITOS",  // Opcional
            "opcion": "1",       // Opcional
            "formato": "excel"
        }
        
        Response 200:
        {
            "status": "completed",
            "data": [
                {
                    "fecha": "2025-04-10",
                    "menu": "CREDITOS",
                    "opcion": "1",
                    "total_transferencias": 320,
                    "transferencias_exitosas": 280,
                    "transferencias_fallidas": 40,
                    "tiempo_promedio_transferencia_seg": 45
                },
                ...
            ],
            "total_records": 180,
            "download_url": "/media/reports/transferencias_Q2_2025.xlsx"
        }
        """
        pass
```

---

#### **5.1.5 Endpoint 4: Errores de Menú**

```python
class MenuErroresViewSet(viewsets.ViewSet):
    """
    Reporte de errores de menú (RPT-ERR-001).
    
    POST /api/v1/reports/menu-errores/
    
    Basado en: q_cMENU_ERROR.sql
    """
    
    @require_function('reports.view')
    def create(self, request):
        """
        Request Body:
        {
            "trimestre": "Q3",
            "menu": "SALDOS",    // Opcional
            "formato": "csv"
        }
        
        Response 200:
        {
            "status": "completed",
            "data": [
                {
                    "fecha": "2025-07-20",
                    "menu": "SALDOS",
                    "tipo_error": "TIMEOUT",
                    "total_errores": 25,
                    "descripcion_error": "Usuario no respondió en tiempo"
                },
                ...
            ],
            "total_records": 45,
            "download_url": "/media/reports/menu_errores_Q3_2025.csv"
        }
        """
        pass
```

---

#### **5.1.6 Tabla Resumen de Endpoints de Reportes**

```
┌───────────────────────────────────┬──────────────────┬─────────────┐
│ Endpoint                          │ Script SQL Base  │ RBAC        │
├───────────────────────────────────┼──────────────────┼─────────────┤
│ /llamadas-abandonadas/            │ q_REPTRIM021     │ reports.view│
│ /clientes-unicos/                 │ q_REPTRIM011     │ reports.view│
│ /promedio-clientes/               │ q_REPTRIM031     │ reports.view│
│ /clientes-menu/                   │ q_REPTRIM041     │ reports.view│
│ /llamadas-menu/                   │ q_REPTRIM121     │ reports.view│
│ /detalle-transferencias/          │ q_REP_DETALLE    │ reports.view│
│ /menu-errores/                    │ q_cMENU_ERROR    │ reports.view│
└───────────────────────────────────┴──────────────────┴─────────────┘
```

---

### 5.2 Endpoints de Dashboards (GET)

#### **5.2.1 Visión General**

```
DASHBOARDS (3 endpoints):
Método: GET (visualización en vivo)
Base URL: /api/v1/dashboard/

Endpoints:
1. GET /api/v1/dashboard/metricas-trimestrales/
2. GET /api/v1/dashboard/analisis-clientes/
3. GET /api/v1/dashboard/performance-ivr/

RBAC:
- dashboard.view: Ver dashboards (cualquier tipo)
- dashboard.export.excel: Exportar snapshot Excel
- dashboard.export.csv: Exportar snapshot CSV
```

---

#### **5.2.2 Endpoint 1: Métricas Trimestrales**

```python
# apps/dashboard/views.py

class MetricasTrimestralesViewSet(viewsets.ViewSet):
    """
    Dashboard de métricas trimestrales.
    
    GET /api/v1/dashboard/metricas-trimestrales/
    """
    
    permission_classes = [IsAuthenticated]
    
    @require_function('dashboard.view')
    def list(self, request):
        """
        Retorna widgets del dashboard de métricas.
        
        Query Params:
        - trimestre: Q1/Q2/Q3 (requerido)
        - did: DID (opcional)
        
        Response 200:
        {
            "widgets": [
                {
                    "id": "kpi-total-llamadas",
                    "type": "kpi",
                    "label": "Total Llamadas",
                    "value": 45320,
                    "icon": "phone",
                    "color": "blue"
                },
                {
                    "id": "kpi-tasa-abandono",
                    "type": "kpi",
                    "label": "Tasa Abandono",
                    "value": "8.5%",
                    "icon": "alert",
                    "color": "green"
                },
                {
                    "id": "chart-evolucion",
                    "type": "chart",
                    "chartType": "line",
                    "label": "Evolución Diaria",
                    "data": [
                        {"x": "2025-01-01", "y": 1500},
                        {"x": "2025-01-02", "y": 1620},
                        ...
                    ]
                },
                {
                    "id": "table-top-menus",
                    "type": "table",
                    "label": "Top Menús",
                    "columns": ["Menu", "Llamadas", "Tasa Éxito"],
                    "rows": [
                        ["CREDITOS", 12500, "92.3%"],
                        ["SALDOS", 8900, "94.1%"],
                        ...
                    ]
                }
            ],
            "last_updated": "2026-01-18T07:30:00Z",
            "cache_ttl": 300
        }
        """
        # Extraer parámetros
        trimestre = request.query_params.get('trimestre')
        did = request.query_params.get('did')
        
        if not trimestre:
            return Response(
                {'error': 'trimestre es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delegar a servicio
        try:
            widgets = DashboardService.get_dashboard_widgets(
                trimestre=trimestre,
                did=did
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Retornar
        return Response({
            'widgets': widgets,
            'last_updated': datetime.now().isoformat(),
            'cache_ttl': DashboardService.CACHE_TIMEOUT
        })
```

**Request/Response Ejemplo:**

```bash
# Request
GET /api/v1/dashboard/metricas-trimestrales/?trimestre=Q1&did=19020084
Authorization: Bearer <token>

# Response 200
{
    "widgets": [
        {
            "id": "kpi-total-llamadas",
            "type": "kpi",
            "label": "Total Llamadas",
            "value": 45320,
            "icon": "phone",
            "color": "blue"
        },
        {
            "id": "kpi-tasa-abandono",
            "type": "kpi",
            "label": "Tasa Abandono",
            "value": "8.5%",
            "icon": "alert",
            "color": "green"
        },
        {
            "id": "chart-evolucion",
            "type": "chart",
            "chartType": "line",
            "label": "Evolución Diaria",
            "data": [
                {"x": "2025-01-01", "y": 1500},
                {"x": "2025-01-02", "y": 1620}
            ]
        }
    ],
    "last_updated": "2026-01-18T07:30:00Z",
    "cache_ttl": 300
}
```

---

#### **5.2.3 Endpoint 2: Análisis de Clientes**

```python
class AnalisisClientesViewSet(viewsets.ViewSet):
    """
    Dashboard de análisis de clientes.
    
    GET /api/v1/dashboard/analisis-clientes/
    """
    
    @require_function('dashboard.view')
    def list(self, request):
        """
        Query Params:
        - trimestre: Q1/Q2/Q3
        
        Response 200:
        {
            "widgets": [
                {
                    "id": "kpi-clientes-unicos",
                    "type": "kpi",
                    "label": "Clientes Únicos",
                    "value": 12450,
                    "icon": "users"
                },
                {
                    "id": "kpi-promedio-llamadas",
                    "type": "kpi",
                    "label": "Promedio Llamadas/Cliente",
                    "value": 3.6,
                    "icon": "activity"
                },
                {
                    "id": "chart-distribucion",
                    "type": "chart",
                    "chartType": "pie",
                    "label": "Distribución por DID",
                    "data": [
                        {"label": "Puebla", "value": 45},
                        {"label": "Nacional A", "value": 35},
                        {"label": "Nacional B", "value": 20}
                    ]
                }
            ]
        }
        """
        pass
```

---

#### **5.2.4 Endpoint 3: Performance IVR**

```python
class PerformanceIVRViewSet(viewsets.ViewSet):
    """
    Dashboard de performance del IVR.
    
    GET /api/v1/dashboard/performance-ivr/
    """
    
    @require_function('dashboard.view')
    def list(self, request):
        """
        Query Params:
        - trimestre: Q1/Q2/Q3
        
        Response 200:
        {
            "widgets": [
                {
                    "id": "kpi-tiempo-promedio",
                    "type": "kpi",
                    "label": "Tiempo Promedio Atención",
                    "value": "3m 45s",
                    "icon": "clock"
                },
                {
                    "id": "chart-tiempos",
                    "type": "chart",
                    "chartType": "bar",
                    "label": "Tiempos por Menú",
                    "data": [
                        {"label": "CREDITOS", "value": 225},
                        {"label": "SALDOS", "value": 180}
                    ]
                }
            ]
        }
        """
        pass
```

---

### 5.3 Pipeline Monitoring

#### **5.3.1 Endpoint: GET /api/v1/pipeline/status/**

```python
# apps/pipeline/views.py

class PipelineViewSet(viewsets.ViewSet):
    """
    Monitoreo del pipeline ETL.
    
    GET /api/v1/pipeline/status/
    """
    
    permission_classes = [IsAuthenticated]
    
    @require_function('pipeline.monitor')
    def list(self, request):
        """
        Retorna estado del último ETL.
        
        Response 200:
        {
            "status": "SUCCESS",
            "last_execution": {
                "job_name": "etl_daily",
                "start_time": "2026-01-18T02:00:00Z",
                "end_time": "2026-01-18T02:12:35Z",
                "duration_seconds": 755,
                "status": "SUCCESS",
                "records_extracted": 8920,
                "records_loaded": 85,
                "records_failed": 0,
                "executed_by": "cron"
            },
            "should_have_run_today": false,
            "next_execution_estimated": "2026-01-19T02:00:00Z",
            "health": "healthy"
        }
        """
        # Delegar a servicio
        status_data = ETLMonitoringService.check_etl_status()
        should_run = ETLMonitoringService.check_etl_should_have_run()
        
        # Determinar health
        health = 'healthy'
        if status_data['status'] == 'FAILED':
            health = 'unhealthy'
        elif should_run:
            health = 'warning'  # Debería haber corrido pero no lo hizo
        
        # Retornar
        return Response({
            'status': status_data['status'],
            'last_execution': status_data,
            'should_have_run_today': should_run,
            'next_execution_estimated': self._get_next_execution(),
            'health': health
        })
    
    def _get_next_execution(self):
        """Calcula próxima ejecución (mañana 2:00 AM)."""
        tomorrow = datetime.now() + timedelta(days=1)
        next_run = tomorrow.replace(hour=2, minute=0, second=0)
        return next_run.isoformat()
```

---

### 5.4 RBAC Permissions

#### **5.4.1 Modelo de Permisos**

```python
# apps/access/models.py

class Function(models.Model):
    """
    Función del sistema (permiso).
    
    Ejemplos:
    - reports.view
    - reports.export.excel
    - dashboard.view
    - pipeline.monitor
    """
    
    code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Código",
        help_text="Código único de la función (ej: reports.view)"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Nombre",
        help_text="Nombre descriptivo"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    category = models.CharField(
        max_length=50,
        choices=[
            ('reports', 'Reportes'),
            ('dashboard', 'Dashboards'),
            ('pipeline', 'Pipeline'),
            ('users', 'Usuarios'),
            ('access', 'Acceso'),
        ],
        verbose_name="Categoría"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    
    class Meta:
        verbose_name = 'Función'
        verbose_name_plural = 'Funciones'
        ordering = ['category', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Agrupador(models.Model):
    """
    Agrupador de funciones (rol).
    
    Ejemplos:
    - AGR_008: Reportes
    - AGR_009: Dashboards
    - AGR_010: Pipeline Monitoring
    """
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código",
        help_text="Código del agrupador (ej: AGR_008)"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Nombre"
    )
    functions = models.ManyToManyField(
        Function,
        related_name='agrupadores',
        verbose_name="Funciones"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    
    class Meta:
        verbose_name = 'Agrupador'
        verbose_name_plural = 'Agrupadores'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
```

---

#### **5.4.2 Decorador @require_function**

```python
# apps/access/decorators.py

from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from apps.access.services import AccessService


def require_function(function_code: str):
    """
    Decorador para requerir función (permiso).
    
    Uso:
        @require_function('reports.view')
        def my_view(request):
            ...
    
    Args:
        function_code: Código de la función requerida
    
    Returns:
        Decorator
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(view_instance, request, *args, **kwargs):
            # Verificar si usuario tiene la función
            user = request.user
            
            if not user.is_authenticated:
                return Response(
                    {'error': 'Autenticación requerida'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Verificar permiso
            has_permission = AccessService.user_has_function(
                user=user,
                function_code=function_code
            )
            
            if not has_permission:
                return Response(
                    {
                        'error': 'Permiso denegado',
                        'required_function': function_code
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Auditar acceso
            AccessService.audit_access(
                user=user,
                function_code=function_code,
                request_path=request.path,
                request_method=request.method
            )
            
            # Ejecutar vista
            return view_func(view_instance, request, *args, **kwargs)
        
        return wrapped_view
    return decorator
```

---

#### **5.4.3 Funciones Definidas**

```python
# apps/access/fixtures/functions.json

[
    {
        "model": "access.function",
        "fields": {
            "code": "reports.view",
            "name": "Ver Reportes",
            "description": "Permite ver y generar cualquier tipo de reporte",
            "category": "reports",
            "is_active": true
        }
    },
    {
        "model": "access.function",
        "fields": {
            "code": "reports.export.excel",
            "name": "Exportar Reportes a Excel",
            "category": "reports",
            "is_active": true
        }
    },
    {
        "model": "access.function",
        "fields": {
            "code": "reports.export.csv",
            "name": "Exportar Reportes a CSV",
            "category": "reports",
            "is_active": true
        }
    },
    {
        "model": "access.function",
        "fields": {
            "code": "dashboard.view",
            "name": "Ver Dashboards",
            "description": "Permite acceder a dashboards en tiempo real",
            "category": "dashboard",
            "is_active": true
        }
    },
    {
        "model": "access.function",
        "fields": {
            "code": "pipeline.monitor",
            "name": "Monitorear Pipeline ETL",
            "description": "Permite ver estado del ETL",
            "category": "pipeline",
            "is_active": true
        }
    }
]
```

---

<a name="6-flujo-de-datos-completo"></a>
## 6. FLUJO DE DATOS COMPLETO

### 6.1 Flujo General del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│ FLUJO COMPLETO: IVR → ETL → Django → API → Frontend            │
└─────────────────────────────────────────────────────────────────┘

PASO 1: ORIGEN - IVR Legacy
├─ Sistema PBX (fuera de Django)
├─ Genera CDRs en tiempo real
└─ Inserta en MariaDB → tbl_historico_t1/t2/t3_2025

PASO 2: ETL - Stored Procedure (Diario 2:00 AM)
├─ Cron ejecuta sp_etl_daily()
├─ Lee de tbl_historico_t*
├─ Agrega datos
├─ Escribe en tbl_reporte_*
└─ Registra en job_execution_log

PASO 3: DJANGO - Lectura Readonly
├─ apps/ivr/models.py (managed=False)
├─ Database Router → 'ivr_legacy'
├─ ORM lee tablas (SELECT only)
└─ Usuario ivr_readonly (no INSERT/UPDATE/DELETE)

PASO 4: API - Django REST Framework
├─ apps/reports/views.py (POST endpoints)
├─ apps/dashboard/views.py (GET endpoints)
├─ Service Layer (lógica de negocio)
├─ RBAC (@require_function)
└─ Serializers (JSON response)

PASO 5: FRONTEND - Consumo de API
├─ React/Vue (fuera de scope)
├─ Fetch de endpoints
├─ Renderiza reportes/dashboards
└─ Descarga archivos (Excel/CSV)
```

---

### 6.2 Diagrama de Secuencia: Generación de Reporte

```
┌──────┐     ┌─────────┐     ┌──────────┐     ┌──────────┐     ┌────────┐
│ User │     │Frontend │     │  Django  │     │ Service  │     │MariaDB │
└──┬───┘     └────┬────┘     └────┬─────┘     └────┬─────┘     └───┬────┘
   │              │               │                │               │
   │ 1. POST /reports/llamadas-abandonadas/       │               │
   ├─────────────>│               │                │               │
   │              │               │                │               │
   │              │ 2. Autenticación + RBAC        │               │
   │              ├──────────────>│                │               │
   │              │               │                │               │
   │              │               │ 3. Validar request             │
   │              │               ├───────────────>│               │
   │              │               │                │               │
   │              │               │                │ 4. SELECT     │
   │              │               │                ├──────────────>│
   │              │               │                │               │
   │              │               │                │<──────────────┤
   │              │               │                │ 5. Datos      │
   │              │               │                │               │
   │              │               │<───────────────┤               │
   │              │               │ 6. Datos procesados            │
   │              │               │                │               │
   │              │ 7. Generar Excel               │               │
   │              │<──────────────┤                │               │
   │              │               │                │               │
   │<─────────────┤               │                │               │
   │ 8. JSON + download_url       │                │               │
   │              │               │                │               │
   │ 9. GET /media/reports/file.xlsx               │               │
   ├─────────────>│               │                │               │
   │              │               │                │               │
   │<─────────────┤               │                │               │
   │ 10. Archivo Excel            │                │               │
   │              │               │                │               │
```

**Detalle:**

1. **Usuario hace POST** a endpoint de reporte
2. **Django valida autenticación** y RBAC (@require_function)
3. **ViewSet delega a Service** con parámetros validados
4. **Service consulta MariaDB** (via Database Router → ivr_legacy)
5. **MariaDB retorna datos** crudos
6. **Service procesa y transforma** datos
7. **Service genera archivo Excel** en /tmp/reports/
8. **Django retorna JSON** con URL de descarga
9. **Usuario solicita archivo**
10. **Django sirve archivo Excel**

---

### 6.3 Diagrama de Secuencia: Dashboard en Tiempo Real

```
┌──────┐     ┌─────────┐     ┌──────────┐     ┌──────────┐     ┌────────┐
│ User │     │Frontend │     │  Django  │     │Dashboard │     │MariaDB │
│      │     │         │     │          │     │ Service  │     │        │
└──┬───┘     └────┬────┘     └────┬─────┘     └────┬─────┘     └───┬────┘
   │              │               │                │               │
   │ 1. GET /dashboard/metricas-trimestrales/     │               │
   ├─────────────>│               │                │               │
   │              │               │                │               │
   │              │ 2. Autenticación + RBAC        │               │
   │              ├──────────────>│                │               │
   │              │               │                │               │
   │              │               │ 3. Check cache │               │
   │              │               ├───────────────>│               │
   │              │               │<───────────────┤               │
   │              │               │ Cache MISS     │               │
   │              │               │                │               │
   │              │               │                │ 4. SELECT     │
   │              │               │                ├──────────────>│
   │              │               │                │               │
   │              │               │                │<──────────────┤
   │              │               │                │ 5. Datos      │
   │              │               │                │               │
   │              │               │<───────────────┤               │
   │              │               │ 6. Widgets (JSON)              │
   │              │               │                │               │
   │              │               │ 7. Save cache (5min)           │
   │              │               ├───────────────>│               │
   │              │               │                │               │
   │              │<──────────────┤                │               │
   │<─────────────┤ 8. JSON (widgets)              │               │
   │              │               │                │               │
   │              │ 9. Render widgets              │               │
   │              ├──────────────>│                │               │
   │              │               │                │               │
```

**Detalle:**

1. **Usuario hace GET** a endpoint de dashboard
2. **Django valida autenticación** y RBAC
3. **Service verifica cache** (LocMem, 5 minutos TTL - CNST-010)
4. **Cache MISS → consulta MariaDB**
5. **MariaDB retorna datos** agregados
6. **Service transforma en widgets** (KPI, Charts, Tables)
7. **Service guarda en cache** (5 min TTL, memoria local)
8. **Django retorna JSON** con widgets
9. **Frontend renderiza widgets** inmediatamente

---

### 6.4 Flujo ETL Detallado con Monitoreo

```
┌─────────────────────────────────────────────────────────────────┐
│ FLUJO ETL + MONITOREO                                           │
└─────────────────────────────────────────────────────────────────┘

02:00 AM - Cron ejecuta /usr/local/bin/run_etl.sh
  │
  ├─> Script bash inicia
  │
  ├─> Conecta a MariaDB
  │
  ├─> Ejecuta: CALL sp_etl_daily();
  │   │
  │   ├─> SP: INSERT job_execution_log (status='RUNNING')
  │   │
  │   ├─> SP: Leer tbl_historico_t* (SELECT WHERE dFecha = yesterday)
  │   │   └─> Registros leídos: ~8,920
  │   │
  │   ├─> SP: Ejecutar transformaciones SQL
  │   │   ├─> q_REPTRIM021 → tbl_reporte_llamadas_abandonadas
  │   │   ├─> q_REPTRIM011 → tbl_reporte_clientes_unicos
  │   │   ├─> q_REPTRIM031 → tbl_reporte_promedio_clientes
  │   │   └─> ... (7 transformaciones total)
  │   │
  │   ├─> SP: INSERT/UPDATE tbl_reporte_* (ON DUPLICATE KEY)
  │   │   └─> Registros cargados: ~85
  │   │
  │   └─> SP: UPDATE job_execution_log (status='SUCCESS')
  │
  ├─> Script bash verifica exit code
  │   └─> 0 = SUCCESS
  │
  └─> Log: /var/log/etl/etl_daily_20260118.log

07:30 AM - Usuario consulta dashboard
  │
  ├─> GET /api/v1/pipeline/status/
  │
  ├─> ETLMonitoringService.check_etl_status()
  │   │
  │   └─> SELECT * FROM job_execution_log
  │       WHERE job_name='etl_daily'
  │       ORDER BY start_time DESC LIMIT 1
  │
  └─> Response:
      {
        "status": "SUCCESS",
        "last_execution": {
          "start_time": "2026-01-18T02:00:00Z",
          "end_time": "2026-01-18T02:12:35Z",
          "duration_seconds": 755,
          "records_loaded": 85
        },
        "health": "healthy"
      }
```

---

### 6.5 Flujo de Datos Cross-Database

```
┌─────────────────────────────────────────────────────────────────┐
│ CROSS-DATABASE: MariaDB (readonly) + PostgreSQL (read/write)   │
└─────────────────────────────────────────────────────────────────┘

ESCENARIO: Usuario genera reporte → Se guarda metadata en PostgreSQL

Usuario:
  POST /api/v1/reports/llamadas-abandonadas/
  Body: { "trimestre": "Q1", "formato": "excel" }

Django ViewSet:
  1. Validar request
  2. Delegar a ReportService

ReportService:
  3. Consultar MariaDB (ivr_legacy)
     │
     └─> SELECT * FROM tbl_reporte_llamadas_abandonadas
         WHERE trimestre='Q1'
         [Database Router → 'ivr_legacy']
  
  4. Procesar datos
  
  5. Generar archivo Excel
     └─> /tmp/reports/llamadas_abandonadas_Q1_20260118.xlsx
  
  6. Guardar metadata en PostgreSQL (default)
     │
     └─> Report.objects.create(
             name='Llamadas Abandonadas Q1',
             file_path='/tmp/reports/...',
             generated_by=user,
             status='completed'
         )
         [Database Router → 'default']

Django ViewSet:
  7. Retornar JSON con download_url

Usuario:
  8. GET /media/reports/llamadas_abandonadas_Q1_20260118.xlsx
  9. Descarga archivo
```

**Claves:**
- **MariaDB (ivr_legacy):** Solo LECTURA de datos IVR
- **PostgreSQL (default):** Escritura de metadata de reportes
- **Database Router:** Maneja automáticamente la separación
- **No hay ForeignKey constraints** entre MariaDB y PostgreSQL

---

### 6.6 Flujo de Cache en Dashboards

```
┌─────────────────────────────────────────────────────────────────┐
│ CACHE STRATEGY: LocMem Cache para Dashboards (CNST-010)        │
└─────────────────────────────────────────────────────────────────┘

IMPORTANTE: Según RESTRICCIONES v1.0.0 (CNST-010):
  ❌ NO se usa Redis (prohibido)
  ✅ Cache: django.core.cache.backends.locmem.LocMemCache

Primera solicitud (Cache MISS):
  GET /api/v1/dashboard/metricas-trimestrales/?trimestre=Q1
  │
  ├─> DashboardService.get_dashboard_widgets('Q1')
  │   │
  │   ├─> cache_key = 'dashboard_metrics_Q1'
  │   │
  │   ├─> cached = cache.get('dashboard_metrics_Q1')
  │   │   └─> None (MISS)
  │   │
  │   ├─> Consultar MariaDB (SELECT FROM tbl_reporte_trimestral)
  │   │
  │   ├─> Calcular widgets
  │   │
  │   └─> cache.set('dashboard_metrics_Q1', widgets, 300)
  │       └─> TTL: 5 minutos (almacenado en memoria local)
  │
  └─> Retornar widgets (JSON)
  
  Duración: ~800ms

Segunda solicitud (dentro de 5 min, mismo proceso) - Cache HIT:
  GET /api/v1/dashboard/metricas-trimestrales/?trimestre=Q1
  │
  ├─> DashboardService.get_dashboard_widgets('Q1')
  │   │
  │   ├─> cached = cache.get('dashboard_metrics_Q1')
  │   │   └─> widgets (HIT - desde memoria local)
  │   │
  │   └─> Retornar cached widgets
  │
  └─> Retornar widgets (JSON)
  
  Duración: ~50ms (16x más rápido)

Después de 5 minutos - Cache EXPIRE:
  Cache invalidado automáticamente
  Siguiente request → Cache MISS → Recalcular

NOTA: LocMem cache es por-proceso. Si hay múltiples workers Gunicorn,
cada uno tiene su propio cache. Para ambiente de 1 worker, funciona perfecto.
```

**Configuración LocMem Cache (CNST-010):**

```python
# config/settings/base.py

CACHES = {
    'default': {
        # ✅ LocMem Cache (desarrollo/producción mono-worker)
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'iact-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,  # Máximo 1000 entradas en memoria
        },
        'KEY_PREFIX': 'iact',
        'TIMEOUT': 300,  # 5 minutos default
    }
}

# Para producción multi-worker, considerar:
# 'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
# (deshabilita cache completamente, queries directas siempre)
```

**Alternativa para Producción Multi-Worker:**

Si se despliega con múltiples workers Gunicorn, se puede usar `DummyCache`:

```python
# config/settings/production.py

CACHES = {
    'default': {
        # ✅ Dummy Cache (deshabilita caching)
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
```

**Ventajas de NO usar Redis (CNST-010):**
- ✅ Sin dependencias externas
- ✅ Sin procesos adicionales corriendo
- ✅ Despliegue más simple
- ✅ Menor superficie de ataque
- ✅ Más fácil troubleshooting

**Limitaciones de LocMem:**
- ⚠️  Cache por-proceso (no compartido entre workers)
- ⚠️  Se pierde al reiniciar proceso
- ⚠️  Limitado por RAM del proceso

**Decisión Final:**
Según volumetría del sistema (~5-10K llamadas/día), el impacto de 
no tener cache compartido es mínimo. Queries a MariaDB son rápidas 
(~800ms) y frecuencia de consulta es baja.
```

---

**FIN DE PARTE 2/3**

**Continúa en:** ARQUITECTURA_REAL_ETL_DEFINITIVA_v1_0_0_PARTE_3.md

---

**Resumen Parte 2:**
- ✅ Sección 4: Arquitectura Django (completa)
  - Apps y responsabilidades
  - Modelos Django (managed=False) completos
  - Database Router (IVR_LEGACY vs DEFAULT)
  - Service Layer Pattern exhaustivo
  - Estructura de archivos
- ✅ Sección 5: APIs y Endpoints (completa)
  - 7 endpoints de reportes (POST) con ejemplos
  - 3 endpoints de dashboards (GET) con widgets
  - Pipeline monitoring
  - RBAC completo (Functions, Agrupadores, decoradores)
- ✅ Sección 6: Flujo de Datos Completo (exhaustivo)
  - Diagramas de secuencia (reportes, dashboards)
  - Flujo ETL con monitoreo
  - Cross-database flows
  - Cache strategy (LocMem - CNST-010)

**Próxima parte:** Nomenclatura, Constantes, Diagramas, Referencias
