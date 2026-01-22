---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: Guía Metodológica
categoria: soporte/metodologia
---

# LÓGICA DE ORGANIZACIÓN SEMÁNTICA DE DOCUMENTOS

**Guía para Estructurar Documentación por Dominio, No por Tipo**

---

## PRINCIPIO FUNDAMENTAL

```
❌ NO organizar por TIPO de documento:
   "Todos los análisis juntos"
   "Todos los planes juntos"
   "Todos los resumenes juntos"

✅ SÍ organizar por DOMINIO SEMÁNTICO:
   "Todo sobre ARQUITECTURA junto"
   "Todo sobre ANÁLISIS junto"
   "Todo sobre GESTIÓN junto"
```

**Por Qué:**
- Más fácil encontrar información relacionada
- Contexto natural
- Escalable (crece orgánicamente)
- No requiere reorganizar constantemente

---

## ESTRUCTURA SEMÁNTICA IACT

```
/tmp/iact-real/docs/
│
├── arquitectura/          ← CÓMO construir el sistema
│   ├── diseño/
│   │   ├── planes/        Planes de implementación
│   │   ├── logica/        POR QUÉ decisiones técnicas (justificación)
│   │   └── patrones/      [DEPRECATED - usar raíz]
│   │
│   ├── patrones/          Guías de PATRONES específicos (QUÉ+CÓMO)
│   │                      Service Layer, Repository, Factory, etc
│   │
│   └── testing/           Estrategias de testing
│
├── analisis/              ← QUÉ necesita el sistema
│   ├── requisitos/        Levantamiento de necesidades
│   ├── clean-code/        Validación de calidad
│   └── calidad/           QA y problemas
│
├── gestion/               ← INFO para stakeholders
│   ├── resumenes/         Resúmenes ejecutivos
│   ├── testing/           Info testing para decisión
│   └── guias/             Cómo usar el sistema
│
└── soporte/               ← Referencias y metodología
    └── metodologia/       Cómo se hace el trabajo
```

### DISTINCIÓN IMPORTANTE: arquitectura/patrones/ vs arquitectura/diseño/logica/

Esta distinción es sutil pero crítica para organización semántica correcta:

```
┌─────────────────────────────────────────────────────────────┐
│ arquitectura/patrones/                                       │
│ ═══════════════════════════════════════════════════════════ │
│ PARA: Documentos sobre PATRONES DE DISEÑO específicos       │
│ ENFOQUE: QUÉ es el patrón + CÓMO se implementa              │
│                                                              │
│ Contenido típico:                                            │
│ • Definición del patrón                                      │
│ • Fundamentos teóricos (Clean Code, Gang of Four)           │
│ • Guía de implementación paso a paso                         │
│ • Ejemplos de código                                         │
│ • Casos de uso del patrón                                    │
│ • Reutilizable en otros proyectos                            │
│                                                              │
│ Ejemplos:                                                    │
│ ✓ SERVICE_LAYER_PATTERN_v1.0.0.md                            │
│ ✓ REPOSITORY_PATTERN_v1.0.0.md                               │
│ ✓ FACTORY_PATTERN_v1.0.0.md                                  │
│ ✓ ANALISIS_SERVICE_LAYER_REFACTORING_v1.0.0.md              │
│   (Guía completa del patrón: 40% QUÉ + 30% CÓMO + 30% POR QUÉ) │
│                                                              │
│ Pregunta clave:                                              │
│ "¿Este documento enseña CÓMO implementar un patrón?"         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ arquitectura/diseño/logica/                                  │
│ ═══════════════════════════════════════════════════════════ │
│ PARA: Documentos que justifican decisiones técnicas         │
│ ENFOQUE: POR QUÉ elegir opción X en ESTE proyecto           │
│                                                              │
│ Contenido típico:                                            │
│ • Contexto del problema específico                           │
│ • Análisis de alternativas (Opción A vs B vs C)             │
│ • Evidencia del código actual                                │
│ • Métricas de impacto                                        │
│ • Justificación de la decisión                               │
│ • Específico del proyecto                                    │
│                                                              │
│ Ejemplos:                                                    │
│ ✓ ANALISIS_OPCION_B_SERVICE_LAYER_v1.0.0.md                  │
│   (POR QUÉ refactorizar a Service Layer en IACT)            │
│ ✓ JUSTIFICACION_POSTGRES_VS_MYSQL_v1.0.0.md                  │
│ ✓ DECISION_FRONTEND_FRAMEWORK_v1.0.0.md                      │
│ ✓ LOGICA_PROBLEMAS_CLEAN_CODE_v1.0.0.md                      │
│                                                              │
│ Pregunta clave:                                              │
│ "¿Este documento justifica POR QUÉ una decisión técnica?"   │
└─────────────────────────────────────────────────────────────┘
```

### Regla de Decisión 60/40

```python
def decidir_ubicacion(documento):
    """
    Si un documento tiene AMBOS enfoques (patrón + decisión),
    usar regla 60/40:
    """
    porcentaje_patron = calcular_porcentaje_QUE_COMO(documento)
    porcentaje_decision = calcular_porcentaje_POR_QUE(documento)
    
    if porcentaje_patron >= 60:
        return "arquitectura/patrones/"
    elif porcentaje_decision >= 60:
        return "arquitectura/diseño/logica/"
    else:
        # Empate o cerca: decidir por PÚBLICO objetivo
        if publico_objetivo == "aprender_patron":
            return "arquitectura/patrones/"
        else:
            return "arquitectura/diseño/logica/"
```

### Ejemplo Real: Service Layer

Actualmente tenemos 2 documentos sobre Service Layer que van en carpetas diferentes:

```
1️⃣ arquitectura/patrones/ANALISIS_SERVICE_LAYER_REFACTORING_v1.0.0.md
   ────────────────────────────────────────────────────────────────
   Contenido:
   • 40% QUÉ es Service Layer (teoría, Clean Code, Martin Fowler)
   • 30% CÓMO implementarlo (refactoring paso a paso)
   • 30% POR QUÉ aplicarlo (ventajas generales)
   
   Público: Desarrolladores que quieren aprender el patrón
   Reutilizable: SÍ (aplicable a cualquier proyecto Django)
   
   Ubicación: arquitectura/patrones/ ✓
   Razón: Mayormente sobre el PATRÓN (70% QUÉ+CÓMO)

2️⃣ arquitectura/diseño/logica/ANALISIS_OPCION_B_SERVICE_LAYER_v1.0.0.md
   ────────────────────────────────────────────────────────────────
   Contenido:
   • 20% QUÉ es Service Layer (contexto)
   • 10% CÓMO implementarlo (guía rápida)
   • 70% POR QUÉ refactorizar en IACT
     - Evidencia del código actual (UserServiceAccess)
     - Métricas específicas (67% lógica en model)
     - Análisis de impacto en IACT
   
   Público: Equipo IACT decidiendo si implementar
   Reutilizable: NO (específico de IACT)
   
   Ubicación: arquitectura/diseño/logica/ ✓
   Razón: Mayormente justificación de DECISIÓN (70% POR QUÉ)
```

**AMBOS SON VÁLIDOS Y COMPLEMENTARIOS:**
- Lee `patrones/` para **aprender** el patrón
- Lee `diseño/logica/` para **entender** la decisión en IACT

---

## PROCESO DE DECISIÓN

### Paso 1: Identificar el TEMA

```
Pregunta: ¿De qué trata el documento?

Ejemplo: "Service Layer Refactoring"
→ Tema: Patrón de arquitectura
→ Subtema: Service Layer Pattern
```

### Paso 2: Identificar el DOMINIO

```
Pregunta: ¿Cuál es el PROPÓSITO del documento?

DOMINIOS:

arquitectura/  → CÓMO diseñar/construir
   "Este documento explica CÓMO implementar X patrón"
   "Este plan define CÓMO construir Y feature"

analisis/      → QUÉ necesitamos / problemas
   "Este documento analiza QUÉ problemas hay"
   "Este levantamiento define QUÉ se requiere"

gestion/       → INFORMACIÓN para decidir
   "Este resumen ayuda a DECIDIR si implementar"
   "Esta guía ayuda a USAR el sistema"

soporte/       → REFERENCIAS y metodología
   "Este documento explica CÓMO trabajamos"
   "Esta referencia tiene información de apoyo"
```

### Paso 3: Determinar SUBCATEGORÍA

```
Dentro del dominio, ¿qué ASPECTO específico?

ARQUITECTURA puede tener:
- diseño/planes/       → Planes de implementación
- diseño/logica/       → Razones de decisiones
- patrones/            → Patrones específicos (Service, Repository)
- testing/             → Estrategias de testing

ANÁLISIS puede tener:
- requisitos/          → Qué se necesita
- clean-code/          → Validación calidad
- calidad/             → QA

GESTIÓN puede tener:
- resumenes/           → Para stakeholders
- testing/             → Info testing para decisión
- guias/               → Manuales de uso
```

### Paso 4: Nombrar el ARCHIVO

```
Formato:
NOMBRE_DESCRIPTIVO_v{VERSION}.md

Donde:
- NOMBRE_DESCRIPTIVO: Tema claro y específico
- VERSION: x.y.z semántico

Ejemplos:
✅ ANALISIS_COMPLETO_OPCIONES_TESTING_v1.0.0.md
✅ OPCION_B_MODEL_TO_SERVICE_v1.0.0.md
✅ RESUMEN_EJECUTIVO_TESTING_v1.0.0.md

❌ analisis.md
❌ doc1.md
❌ temp_file.md
```

---

## EJEMPLOS REALES

### Ejemplo 1: Análisis de Testing

```
DOCUMENTO: "Análisis completo de opciones para testing"

PASO 1 - TEMA:
→ Testing en entorno restringido
→ Opciones técnicas (SQLite, imports, fixtures)

PASO 2 - DOMINIO:
→ ¿CÓMO construir? → arquitectura/
→ Subtema: testing

PASO 3 - SUBCATEGORÍA:
→ arquitectura/testing/

PASO 4 - NOMBRE:
→ ANALISIS_COMPLETO_OPCIONES_TESTING_v1.0.0.md

RUTA FINAL:
/tmp/iact-real/docs/arquitectura/testing/
  ANALISIS_COMPLETO_OPCIONES_TESTING_v1.0.0.md
```

### Ejemplo 2: Service Layer Pattern

```
DOCUMENTO: "Mover lógica de model a service"

PASO 1 - TEMA:
→ Service Layer Pattern
→ Refactoring arquitectural

PASO 2 - DOMINIO:
→ ¿CÓMO diseñar? → arquitectura/
→ Subtema: patrón específico

PASO 3 - SUBCATEGORÍA:
→ arquitectura/patrones/

PASO 4 - NOMBRE:
→ OPCION_B_MODEL_TO_SERVICE_v1.0.0.md

RUTA FINAL:
/tmp/iact-real/docs/arquitectura/patrones/
  OPCION_B_MODEL_TO_SERVICE_v1.0.0.md
```

### Ejemplo 3: Resumen Ejecutivo

```
DOCUMENTO: "Resumen testing para stakeholders"

PASO 1 - TEMA:
→ Estado de testing
→ Decisión de inversión

PASO 2 - DOMINIO:
→ INFO para decidir → gestion/
→ Subtema: testing

PASO 3 - SUBCATEGORÍA:
→ gestion/testing/

PASO 4 - NOMBRE:
→ RESUMEN_TESTING_v1.0.0.md

RUTA FINAL:
/tmp/iact-real/docs/gestion/testing/
  RESUMEN_TESTING_v1.0.0.md
```

### Ejemplo 4: Service Layer - ¿patrones/ o diseño/logica/?

```
DOCUMENTO: "Guía completa del patrón Service Layer"

PASO 1 - TEMA:
→ Service Layer Pattern
→ Refactoring arquitectural

PASO 2 - DOMINIO:
→ ¿CÓMO diseñar? → arquitectura/
→ Subtema: patrón específico

PREGUNTA CLAVE:
¿El documento explica QUÉ es el patrón y CÓMO aplicarlo? SÍ
¿O justifica POR QUÉ una decisión específica del proyecto? NO

ANÁLISIS DE CONTENIDO:
- 40% Teoría del patrón (QUÉ es)
- 30% Guía de implementación (CÓMO)
- 30% Ventajas generales (POR QUÉ en general)

TOTAL: 70% sobre el PATRÓN (QUÉ+CÓMO)

PASO 3 - SUBCATEGORÍA:
→ arquitectura/patrones/

PASO 4 - NOMBRE:
→ ANALISIS_SERVICE_LAYER_REFACTORING_v1.0.0.md

RUTA FINAL:
/tmp/iact-real/docs/arquitectura/patrones/
  ANALISIS_SERVICE_LAYER_REFACTORING_v1.0.0.md
```

**CONTRASTE: Mismo tema, diferente enfoque**

```
DOCUMENTO: "Análisis de por qué refactorizar a Service Layer en IACT"

PASO 1 - TEMA:
→ Service Layer refactoring
→ Decisión técnica para IACT

PASO 2 - DOMINIO:
→ ¿CÓMO diseñar? → arquitectura/
→ Subtema: justificación de decisión

PREGUNTA CLAVE:
¿Justifica POR QUÉ refactorizar en ESTE proyecto? SÍ
¿O enseña el patrón en general? NO

ANÁLISIS DE CONTENIDO:
- 20% Teoría del patrón (contexto)
- 10% Guía de implementación (resumen)
- 70% Evidencia específica de IACT (POR QUÉ en IACT)
  * Código actual con problemas
  * Métricas del proyecto (67% lógica en model)
  * Impacto en tests de IACT

TOTAL: 70% JUSTIFICACIÓN de decisión (POR QUÉ)

PASO 3 - SUBCATEGORÍA:
→ arquitectura/diseño/logica/

PASO 4 - NOMBRE:
→ ANALISIS_OPCION_B_SERVICE_LAYER_v1.0.0.md

RUTA FINAL:
/tmp/iact-real/docs/arquitectura/diseño/logica/
  ANALISIS_OPCION_B_SERVICE_LAYER_v1.0.0.md
```

**CONCLUSIÓN:**
Mismo tema (Service Layer), diferente propósito:
- `patrones/` → Para APRENDER el patrón (reutilizable)
- `diseño/logica/` → Para JUSTIFICAR la decisión (específico IACT)

---

## IMPLEMENTACIÓN EN CÓDIGO

```python
def determinar_ruta_documento(tema, proposito, subtema=None):
    """
    Determinar ruta semántica para documento.
    
    Args:
        tema: Tema principal del documento
        proposito: CÓMO/QUÉ/INFO/REFERENCIA
        subtema: Subcategoría específica (opcional)
        
    Returns:
        str: Ruta completa
    """
    # Dominio base según propósito
    dominios = {
        'CÓMO': 'arquitectura',
        'QUÉ': 'analisis',
        'INFO': 'gestion',
        'REF': 'soporte'
    }
    
    dominio = dominios.get(proposito)
    
    # Construir ruta
    base = f"/tmp/iact-real/docs/{dominio}"
    
    if subtema:
        ruta = f"{base}/{subtema}"
    else:
        ruta = base
    
    # Crear directorio si no existe
    os.makedirs(ruta, exist_ok=True)
    
    return ruta


# USO:
ruta = determinar_ruta_documento(
    tema='Service Layer Refactoring',
    proposito='CÓMO',
    subtema='patrones'
)
# → /tmp/iact-real/docs/arquitectura/patrones/
```

---

## VENTAJAS DE ESTE SISTEMA

```
┌──────────────────────────────────────────────────┐
│ VENTAJA 1: Escalabilidad                          │
├──────────────────────────────────────────────────┤
│                                                   │
│ CRECE ORGÁNICAMENTE:                              │
│                                                   │
│ Año 1:                                            │
│ arquitectura/testing/ (3 documentos)              │
│                                                   │
│ Año 2:                                            │
│ arquitectura/testing/ (15 documentos)             │
│ arquitectura/deployment/ (8 documentos) ← NUEVO   │
│                                                   │
│ NO necesitas reorganizar lo anterior.             │
│ Solo agregas nuevas carpetas según surjan.        │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ VENTAJA 2: Contexto Natural                       │
├──────────────────────────────────────────────────┤
│                                                   │
│ Cuando buscas info sobre testing:                 │
│                                                   │
│ → vas a arquitectura/testing/                     │
│ → encuentras TODO sobre testing junto:            │
│   * Análisis opciones                             │
│   * Plan de acción                                │
│   * Estrategias                                   │
│   * Roadmap                                       │
│                                                   │
│ NO necesitas buscar en:                           │
│ - carpeta "analisis/" → análisis testing          │
│ - carpeta "planes/" → plan testing                │
│ - carpeta "estrategias/" → estrategia testing     │
│                                                   │
│ TODO está en un lugar lógico.                     │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ VENTAJA 3: Evita Confusión                        │
├──────────────────────────────────────────────────┤
│                                                   │
│ SIN organización semántica:                       │
│                                                   │
│ docs/analisis/                                    │
│ ├── analisis_testing.md                          │
│ ├── analisis_security.md                         │
│ ├── analisis_performance.md                      │
│ └── ... (50 archivos)                            │
│                                                   │
│ ¿Cuál es cuál? Necesitas abrir cada uno.         │
│                                                   │
│ CON organización semántica:                       │
│                                                   │
│ docs/                                             │
│ ├── arquitectura/testing/analisis.md             │
│ ├── arquitectura/security/analisis.md            │
│ └── arquitectura/performance/analisis.md         │
│                                                   │
│ Contexto claro desde la ruta.                     │
└──────────────────────────────────────────────────┘
```

---

## REGLAS DE ORO

```
1. DOMINIO POR PROPÓSITO, NO POR TIPO
   ❌ "carpeta de análisis"
   ✅ "carpeta de arquitectura que contiene análisis"

2. MÚLTIPLES NIVELES SON OK
   ✅ arquitectura/patrones/service-layer/
   No te limites a 2 niveles

3. NOMBRES DESCRIPTIVOS
   ✅ ANALISIS_COMPLETO_OPCIONES_TESTING_v1.0.0.md
   ❌ doc1.md

4. VERSIONAR TODO
   ✅ v1.0.0, v1.1.0, v2.0.0
   Poder rastrear cambios

5. README en cada carpeta
   ✅ arquitectura/testing/README.md
   Explicar qué contiene la carpeta

6. LINKS ENTRE DOCUMENTOS
   Referenciar documentos relacionados
   Ver sección "Documentos Relacionados"
```

---

## ANTIPATRONES A EVITAR

```
❌ ANTIPATRÓN 1: Por tipo de documento

docs/
├── analisis/    ← Todos los análisis
├── planes/      ← Todos los planes
├── resumenes/   ← Todos los resúmenes
└── guias/       ← Todas las guías

PROBLEMA: Info relacionada dispersa


❌ ANTIPATRÓN 2: Por fecha

docs/
├── 2024-01/
├── 2024-02/
└── 2024-03/

PROBLEMA: Imposible encontrar temas


❌ ANTIPATRÓN 3: Por autor

docs/
├── juan/
├── maria/
└── pedro/

PROBLEMA: Información duplicada


✅ CORRECTO: Por dominio semántico

docs/
├── arquitectura/
│   └── testing/
├── analisis/
│   └── requisitos/
└── gestion/
    └── resumenes/
```

---

## CHECKLIST DE CREACIÓN

```
□ 1. Identificar TEMA del documento
□ 2. Identificar PROPÓSITO (CÓMO/QUÉ/INFO/REF)
□ 3. Determinar DOMINIO (arquitectura/analisis/gestion/soporte)
□ 4. Determinar SUBCATEGORÍA (testing/patrones/requisitos/etc)
□ 5. Verificar si ruta existe
□ 6. Crear ruta si no existe: mkdir -p
□ 7. Nombrar archivo: TEMA_DESCRIPTIVO_v1.0.0.md
□ 8. Agregar metadata al inicio:
   ---
   version: 1.0.0
   date: YYYY-MM-DD
   categoria: dominio/subcategoria
   ---
□ 9. Crear documento
□ 10. Agregar a README de la carpeta (si existe)
```

---

## CONCLUSIÓN

La **organización semántica** permite:

✅ Escalar sin reorganizar  
✅ Encontrar info rápidamente  
✅ Contexto natural  
✅ Evitar confusión  
✅ Colaboración más fácil  

**NO es más trabajo, es MEJOR trabajo.**

---

**FIN DE LA GUÍA**

Version: 1.0.0
Fecha: 2026-01-17
Categoría: soporte/metodologia
