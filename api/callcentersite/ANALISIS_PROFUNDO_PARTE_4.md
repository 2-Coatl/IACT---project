# ANÁLISIS PROFUNDO DEL PROYECTO - PARTE 4 DE 5
## DEPENDENCIAS Y PRIORIZACIÓN

**Proyecto:** IACT Call Center System  
**Fecha Análisis:** 16 de enero de 2026  

---

## 4.1 MAPA DE DEPENDENCIAS

### Diagrama de Dependencias:

```
MIGRACIONES (BLOQUEANTE)
    ↓
DEPENDENCIAS (Pillow, etc.)
    ↓
┌───────────────┬────────────────┬───────────────┐
│               │                │               │
│  MODELOS      │   SERIALIZERS  │   COMMANDS    │
│  REPORTS      │   FALTANTES    │   POPULATE    │
│               │                │               │
└───────┬───────┴────────┬───────┴───────┬───────┘
        │                │               │
        └────────────────┼───────────────┘
                         ↓
                    APIS COMPLETAS
                         ↓
                ┌────────┴────────┐
                │                 │
            TESTS            INTEGRACIÓN
                │                 │
                └────────┬────────┘
                         ↓
                   DOCKER + CI/CD
                         ↓
                   DOCUMENTACIÓN
```

---

## 4.2 TAREAS CON DEPENDENCIAS

### NIVEL 0: BLOQUEANTES (HACER PRIMERO)

```
[M0] Crear migraciones
     │
     ├─ users (CRÍTICO - avatar, phone, etc.)
     ├─ access (CRÍTICO - RBAC)
     ├─ core
     ├─ authentication
     ├─ audit
     └─ pipeline
     
     Tiempo: 2h
     Dependencias: NINGUNA
     Bloqueante para: TODO
```

```
[D0] Instalar dependencias
     │
     ├─ Pillow (CRÍTICO para avatar)
     ├─ openpyxl (para reports)
     ├─ reportlab (para PDF)
     └─ Verificar todas
     
     Tiempo: 1h
     Dependencias: NINGUNA
     Bloqueante para: Avatar, Reports
```

### NIVEL 1: FUNDACIÓN (DESPUÉS DE M0, D0)

```
[M1] Aplicar migraciones
     python manage.py migrate
     
     Tiempo: 0.5h
     Dependencias: [M0]
     Bloqueante para: BD funcional
```

```
[CMD1] Commands de población inicial
     │
     ├─ populate_functions (44 funciones RBAC)
     ├─ populate_modules (desde JSON)
     └─ populate_initial_data (centers, services)
     
     Tiempo: 3h
     Dependencias: [M0, M1]
     Bloqueante para: Sistema funcional
```

### NIVEL 2: CORE FUNCIONALIDAD

```
[MODEL1] Modelos Reports
     │
     ├─ Report
     ├─ ReportSchedule
     ├─ Dashboard
     └─ ReportExecution
     
     Tiempo: 4h
     Dependencias: [M0, M1]
     Bloqueante para: APIs Reports
```

```
[SER1] Serializers faltantes
     │
     ├─ ReportSerializer
     ├─ DashboardSerializer
     └─ Mejorar existentes
     
     Tiempo: 3h
     Dependencias: [MODEL1]
     Bloqueante para: APIs
```

```
[API1] APIs RBAC completas
     │
     ├─ CRUD Functions
     ├─ Assign/Revoke Functions
     └─ User Functions management
     
     Tiempo: 8h
     Dependencias: [M0, M1, CMD1]
     Bloqueante para: RBAC funcional
```

```
[API2] APIs Users completas
     │
     ├─ Change password
     ├─ Reset password
     └─ Activate/Deactivate
     
     Tiempo: 5h
     Dependencias: [M0, M1]
     Bloqueante para: Gestión users
```

### NIVEL 3: FUNCIONALIDAD EXTENDIDA

```
[API3] APIs Reports
     │
     ├─ Generate reports
     ├─ Export CSV/Excel/PDF
     └─ Dashboards
     
     Tiempo: 15h
     Dependencias: [MODEL1, SER1, D0]
     Bloqueante para: Reports funcional
```

```
[API4] APIs Core CRUD
     │
     ├─ Centers CRUD
     ├─ Services CRUD
     └─ CallRecords escritura
     
     Tiempo: 5h
     Dependencias: [M0, M1]
     Bloqueante para: Gestión core
```

### NIVEL 4: CALIDAD

```
[TEST1] Tests faltantes
     │
     ├─ Reports tests
     ├─ Access tests ampliados
     ├─ Core tests
     └─ Integration tests
     
     Tiempo: 10h
     Dependencias: [API1, API2, API3, API4]
     Bloqueante para: CI/CD confiable
```

### NIVEL 5: INFRAESTRUCTURA

```
[INFRA1] Docker + CI/CD
     │
     ├─ Dockerfile
     ├─ docker-compose.yml
     ├─ GitHub Actions
     └─ .env.example
     
     Tiempo: 5h
     Dependencias: [TEST1]
     Bloqueante para: Deploy automatizado
```

```
[DOC1] Documentación
     │
     ├─ README actualizado
     ├─ API docs
     └─ DEPLOYMENT.md
     
     Tiempo: 4h
     Dependencias: Todas anteriores
     Bloqueante para: NADA (puede ir en paralelo)
```

---

## 4.3 MATRIZ DE PRIORIZACIÓN

### Matriz Impacto vs Esfuerzo:

```
           ALTO IMPACTO
               ↑
               │
   NIVEL 1     │    NIVEL 2
   ┌──────────┼──────────┐
   │  [M0]    │  [API1]  │
   │  [M1]    │  [API2]  │
   │  [D0]    │  [MODEL1]│
   │  [CMD1]  │  [SER1]  │
   │          │          │
───┼──────────┼──────────┼───→ BAJO ESFUERZO
   │          │          │
   │  [API3]  │  [INFRA1]│
   │  [TEST1] │  [DOC1]  │
   │          │          │
   └──────────┼──────────┘
   NIVEL 3    │    NIVEL 4
               ↓
           BAJO IMPACTO
```

### Clasificación:

**CRÍTICO (Hacer Ya):**
- [M0] Migraciones
- [M1] Migrate
- [D0] Dependencias
- [CMD1] Population commands

**ALTO (Sprint 1):**
- [MODEL1] Modelos Reports
- [SER1] Serializers
- [API1] APIs RBAC
- [API2] APIs Users

**MEDIO (Sprint 2):**
- [API3] APIs Reports
- [API4] APIs Core
- [TEST1] Tests

**BAJO (Sprint 3):**
- [INFRA1] Docker + CI/CD
- [DOC1] Documentación

---

## 4.4 RUTA CRÍTICA (Critical Path)

### Secuencia obligatoria para sistema funcional:

```
1. [M0] Migraciones              (2h)    CRÍTICO
   ↓
2. [D0] Dependencias             (1h)    CRÍTICO
   ↓
3. [M1] Migrate                  (0.5h)  CRÍTICO
   ↓
4. [CMD1] Population             (3h)    ALTO
   ↓
5. [API1] APIs RBAC              (8h)    ALTO
   ↓
6. Sistema básico funcional      ✅

TOTAL RUTA CRÍTICA: 14.5 horas (~2 días)
```

### Después de ruta crítica (paralelo):

```
Rama A:                          Rama B:
[MODEL1] Modelos Reports         [API2] APIs Users
    ↓                                ↓
[SER1] Serializers               [API4] APIs Core
    ↓                                ↓
[API3] APIs Reports              [TEST1] Tests
```

---

## 4.5 BLOQUEANTES POR FUNCIONALIDAD

### Para que funcione RBAC completo:
```
NECESITA:
✅ [M0] Migraciones access
✅ [M1] Migrate
✅ [CMD1] populate_functions
✅ [API1] APIs RBAC completas
⚠️ Navegación ya implementada (MenuBuilder)
```

### Para que funcionen Reports:
```
NECESITA:
❌ [M0] Migraciones reports
❌ [D0] Pillow, openpyxl, reportlab
❌ [MODEL1] Modelos Reports
❌ [SER1] Serializers Reports
❌ [API3] APIs Reports
```

### Para que funcione gestión Users:
```
NECESITA:
⚠️ [M0] Migraciones users (avatar)
✅ [D0] Pillow (para avatar)
⚠️ [API2] APIs Users completas
✅ Avatar/Profile ya implementados
```

### Para deploy:
```
NECESITA:
❌ [TEST1] Tests completos
❌ [INFRA1] Docker + CI/CD
⚠️ [DOC1] Documentación
```

---

## 4.6 ESTRATEGIA DE IMPLEMENTACIÓN

### Fase 1: Sistema Funcional Básico (2 días)
```
Objetivo: Sistema corre, BD funciona, RBAC básico
Tareas: M0, D0, M1, CMD1, API1
Horas: 14.5h
```

### Fase 2: CRUD Completo (2-3 días)
```
Objetivo: Gestión completa users, core, y estructura reports
Tareas: MODEL1, SER1, API2, API4
Horas: 17h
```

### Fase 3: Reports Funcionales (3-4 días)
```
Objetivo: Generación y exportación de reportes
Tareas: API3
Horas: 15h
```

### Fase 4: Calidad y Deploy (2-3 días)
```
Objetivo: Tests, CI/CD, documentación
Tareas: TEST1, INFRA1, DOC1
Horas: 19h
```

**TOTAL: 65.5 horas = 8-9 días laborales = 1.5-2 semanas**

---

## 4.7 RECURSOS NECESARIOS

### Desarrollador Backend:
- Conocimiento Django/DRF
- Conocimiento RBAC
- SQL/Migraciones
- Testing (pytest)

### Habilidades opcionales:
- Docker
- CI/CD (GitHub Actions)
- Frontend (para integración)

### Herramientas:
- PostgreSQL local
- Redis (para Celery)
- Git
- IDE (VSCode, PyCharm)

---

## 4.8 RIESGOS IDENTIFICADOS

### ALTO:
```
❌ Migraciones fallan por conflictos
   Mitigación: Hacer backup antes de migrar
   
❌ Dependencias con versiones incompatibles
   Mitigación: Usar requirements.txt con versiones fijas
   
❌ RBAC muy complejo, retrasa desarrollo
   Mitigación: Implementar versión simplificada primero
```

### MEDIO:
```
⚠️ Reports toman más tiempo del estimado
   Mitigación: Implementar exportación básica primero
   
⚠️ Tests descubren bugs en navegación
   Mitigación: Priorizar tests críticos
```

### BAJO:
```
⚠️ Docker no funciona en primer intento
   Mitigación: Dejar para última fase
```

---

## RESUMEN PARTE 4

### RUTA CRÍTICA:
```
M0 → D0 → M1 → CMD1 → API1
14.5 horas (~2 días)
```

### DEPENDENCIAS CLAVE:
- Todo depende de migraciones
- RBAC depende de population
- Reports depende de modelos
- Deploy depende de tests

### PRIORIZACIÓN:
1. CRÍTICO: Migraciones + Dependencias (3h)
2. ALTO: RBAC + Users APIs (13h)
3. MEDIO: Reports + Tests (25h)
4. BAJO: Infra + Docs (9h)

---

## PRÓXIMA PARTE

**PARTE 5:** Plan de acción dividido en sprints detallados
