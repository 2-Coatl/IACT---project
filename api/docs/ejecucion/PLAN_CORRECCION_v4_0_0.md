# PLAN DE CORRECCIÓN v4.0.0 - ERROR CRÍTICO DOCUMENTACIÓN

**Fecha:** 2026-01-21  
**Criticidad:** ALTA  
**Tipo:** Corrección documentación errónea  

---

## 🚨 ERROR CRÍTICO DETECTADO

### Problema

En FASE C se documentó **incorrectamente** el sistema de permisos:

```yaml
❌ ERROR COMETIDO:
  - Documenté códigos como RPT_VIEW, DSH_EXP_CSV como clave primaria
  - Inventé sistema de funciones basado en códigos
  - README.md tiene 46 funciones con códigos incorrectos

✅ REALIDAD SEGÚN MODELO_RBAC_IACT_v6_0_0:
  - permission_django es la clave primaria
  - Formato: reports.view, dashboard.export.csv
  - code es solo REFERENCIAL (no es PK)
```

### Evidencia

**MODELO_RBAC_IACT_v6_0_0_PARTE_1.md líneas 105-111:**

```python
✅ permission_django:       Inglés (reports.view, dashboard.export.csv)
✅ code (referencial):      Inglés (RPT_VIEW, DSH_EXP_CSV)
✅ display_name (UI):       Español (Ve Reportes, Exporta CSV)
✅ description:             Español (con casos de uso)
```

**Ejemplo función real:**

```python
class Function(models.Model):
    """Función atómica del sistema RBAC."""
    
    permission_django = models.CharField(
        max_length=100,
        primary_key=True,  # ← CLAVE PRIMARIA
        help_text="reports.view, dashboard.export.csv"
    )
    
    code = models.CharField(
        max_length=30,
        help_text="Código: RPT_VIEW, DSH_EXP_CSV"  # ← REFERENCIAL
    )
```

---

## 📊 ALCANCE DEL ERROR

### Archivos Afectados

```yaml
apps/access/README.md:
  ❌ Sección "Funciones del Sistema"
  ❌ Workflows con códigos incorrectos
  ❌ Ejemplos con códigos incorrectos
  ❌ Documentación de 46 funciones errónea
  
docs/ejecucion/FASE_C_COMPLETADO.md:
  ❌ Listado funciones con códigos incorrectos
```

### Datos Correctos (MODELO_RBAC v6.0.0)

**46 funciones REALES:**

```yaml
MOD_Auth (4):
  - auth.login
  - auth.logout
  - auth.recover_password
  - auth.manage_sessions

MOD_Users (9):
  - users.view_user
  - users.add_user
  - users.change_user
  - users.delete_user
  - users.change_password
  - users.reset_password
  - users.lock_user
  - users.unlock_user
  - users.view_profile

MOD_Access (5):
  - access.assign_functions
  - access.revoke_functions
  - access.view_permissions
  - access.manage_groups
  - access.view_separation

MOD_Pipeline (4):
  - pipeline.view_job
  - pipeline.execute_job
  - pipeline.stop_job
  - pipeline.view_logs

MOD_Reports (6):
  - reports.view
  - reports.create
  - reports.delete
  - reports.export.csv
  - reports.export.excel
  - reports.export.pdf (planificado)

MOD_Dashboard (6):
  - dashboard.view
  - dashboard.export.csv
  - dashboard.export.excel
  - dashboard.export.pdf (planificado)
  - dashboard.share (planificado)
  - dashboard.edit (planificado)

MOD_Alerts (6):
  - alerts.view_alert
  - alerts.configure_alert
  - alerts.send_alert
  - alerts.manage_subscriptions
  - alerts.mark_read
  - alerts.delete_alert

MOD_Audit (4):
  - audit.view_log
  - audit.search_log
  - audit.export_log
  - audit.generate_compliance

MOD_Logs (2):
  - logs.view_technical
  - logs.export_logs
```

---

## 🎯 FASE D - CORRECCIÓN

### D.1: Corregir apps/access/README.md (1h)

**Secciones a corregir:**

1. **Funciones del Sistema (Sección 5)**
   - Actualizar tabla con permission_django correcto
   - Mantener code como referencial
   - Agregar display_name en español

2. **Workflows (Sección 6)**
   ```python
   # ANTES (INCORRECTO):
   function = Function.objects.get(code='RPT_VIEW')
   
   # DESPUÉS (CORRECTO):
   function = Function.objects.get(permission_django='reports.view')
   ```

3. **Ejemplos de Uso (Sección 8)**
   - Actualizar todos los ejemplos
   - Usar permission_django como PK

4. **API Endpoints (Sección 7)**
   - Mantener (no afectados)

5. **Testing (Sección 9)**
   - Actualizar tests con permission_django

### D.2: Crear URLS_REPORTES_Y_DASHBOARDS.md (30 min)

**Contenido:**
- Separación apps/reports/ vs apps/dashboard/
- Endpoints /api/v1/reports/ vs /api/v1/dashboard/
- Justificación separación módulos
- Basado en MODELO_RBAC v6.0.0

### D.3: Actualizar Documentación de Fases (30 min)

**Archivos:**
- docs/ejecucion/FASE_C_COMPLETADO.md
- docs/ejecucion/PLAN_REMEDIACION_FASES_ABC_COMPLETADO.md

**Cambios:**
- Nota de corrección v4
- Link a este documento
- Funciones correctas

---

## ✅ CRITERIOS DE COMPLETITUD

```yaml
README.md corregido:
  ✅ 46 funciones con permission_django correcto
  ✅ code documentado como referencial
  ✅ display_name en español
  ✅ Workflows actualizados
  ✅ Ejemplos corregidos
  ✅ Tests actualizados

URLS_REPORTES_Y_DASHBOARDS.md:
  ✅ Creado
  ✅ Arquitectura apps/reports/ vs apps/dashboard/
  ✅ Endpoints documentados

Documentación actualizada:
  ✅ FASE_C_COMPLETADO.md con nota corrección
  ✅ Links a plan v4
```

---

## 📊 TIEMPO ESTIMADO

```yaml
D.1: Corregir README.md: 1h
D.2: Crear URLS_REPORTES_Y_DASHBOARDS.md: 30 min
D.3: Actualizar docs fases: 30 min

Total: 2h
```

---

## 🔗 DOCUMENTOS DE REFERENCIA

```yaml
Fuente de verdad:
  ✅ docs/rbac/MODELO_RBAC_IACT_v6_0_0_PARTE_1.md
  ✅ docs/rbac/MODELO_RBAC_IACT_v6_0_0_PARTE_2.md

Menciones:
  - URLS_REPORTES_Y_DASHBOARDS.md (NUEVO, pendiente crear)
  - CLEAN_CODE_NAMING_PRINCIPLES_v3_0_1.md
  - RESTRICCIONES_ARQUITECTONICAS_IACT_v1_0_0.md
```

---

**Estado:** PENDIENTE EJECUCIÓN  
**Prioridad:** ALTA  
**Versión:** 4.0.0  
**Documento:** docs/ejecucion/PLAN_CORRECCION_v4_0_0.md
