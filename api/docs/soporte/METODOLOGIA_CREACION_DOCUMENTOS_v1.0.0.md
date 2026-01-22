---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: Metodología de Trabajo
categoria: soporte
---

# METODOLOGÍA PARA CREACIÓN DE DOCUMENTOS

---

## OBJETIVO

Establecer un proceso sistemático para crear documentos técnicos siguiendo la estructura semántica del proyecto IACT, garantizando que cada documento esté en la ubicación correcta según su propósito.

---

## PRINCIPIO FUNDAMENTAL

### ❌ NO organizar por TIPO de documento

```
Incorrecto:
/docs/
  ├── analisis/        ← Todos los análisis juntos
  ├── resumenes/       ← Todos los resúmenes juntos
  └── planes/          ← Todos los planes juntos
```

### ✅ SI organizar por DOMINIO SEMÁNTICO

```
Correcto:
/docs/
  ├── arquitectura/    ← CÓMO construir el sistema
  ├── analisis/        ← QUÉ necesita + validación
  ├── gestion/         ← INFO para stakeholders
  └── soporte/         ← Referencias y metodologías
```

---

## ESTRUCTURA SEMÁNTICA DEFINIDA

### 1. arquitectura/

**Propósito:** Documentos que definen CÓMO construir y diseñar el sistema.

```
arquitectura/
├── diseño/
│   ├── planes/          → CÓMO implementar (estrategias, pasos)
│   ├── logica/          → POR QUÉ decisiones técnicas
│   └── patrones/        → Patrones de diseño aplicados
│
├── patrones/            → Guías de PATRONES DE DISEÑO específicos
│
├── testing/             → Estrategias de pruebas
│
├── deployment/          → Deploy y configuración
│
└── integracion/         → Integraciones externas
```

**Ejemplos de documentos:**
- `planes/PLAN_MIGRACION_DB_v1.0.0.md`
- `logica/LOGICA_PROBLEMAS_CLEAN_CODE_v1.0.0.md`
- `testing/ANALISIS_OPCIONES_TESTING_v1.0.0.md`
- `patrones/SERVICE_LAYER_PATTERN_v1.0.0.md`

**Pregunta clave:** ¿Este documento explica CÓMO construir algo?

#### 1.1 DISTINCIÓN IMPORTANTE: patrones/ vs diseño/logica/

**Esta es una distinción sutil pero importante:**

```
┌────────────────────────────────────────────────────────────┐
│ arquitectura/patrones/                                      │
├────────────────────────────────────────────────────────────┤
│ Para: Documentos sobre PATRONES DE DISEÑO específicos      │
│ Contenido: Service Layer, Repository, Factory, etc         │
│ Enfoque: QUÉ es el patrón + CÓMO se aplica                 │
│                                                             │
│ Ejemplos:                                                   │
│ ✅ SERVICE_LAYER_PATTERN_v1.0.0.md                          │
│    → QUÉ: Patrón para separar lógica de negocio            │
│    → CÓMO: Implementación paso a paso                       │
│    → Fundamentos teóricos (Clean Code, Martin Fowler)      │
│                                                             │
│ ✅ REPOSITORY_PATTERN_v1.0.0.md                             │
│    → QUÉ: Patrón para abstracción de datos                 │
│    → CÓMO: Implementación con ejemplos                      │
│                                                             │
│ ✅ ANALISIS_SERVICE_LAYER_REFACTORING_v1.0.0.md             │
│    → Guía completa del patrón Service Layer                │
│    → Filosofía, implementación, roadmap                     │
│    → 40% QUÉ es + 30% CÓMO + 30% POR QUÉ                   │
│                                                             │
│ Características:                                            │
│ - Reutilizable en otros proyectos                           │
│ - Fundamentos teóricos                                      │
│ - Guía de implementación                                    │
│ - Enfoque en el PATRÓN en sí                                │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ arquitectura/diseño/logica/                                 │
├────────────────────────────────────────────────────────────┤
│ Para: Documentos que explican POR QUÉ decisiones técnicas  │
│ Contenido: Razones, justificaciones, análisis alternativas │
│ Enfoque: POR QUÉ refactorizar, POR QUÉ elegir opción X     │
│                                                             │
│ Ejemplos:                                                   │
│ ✅ ANALISIS_OPCION_B_SERVICE_LAYER_v1.0.0.md                │
│    → POR QUÉ: Refactorizar a Service Layer en IACT        │
│    → Evidencia específica del proyecto                      │
│    → Comparación de alternativas (Opción A vs B)           │
│    → Métricas de impacto en IACT                           │
│                                                             │
│ ✅ JUSTIFICACION_POSTGRES_VS_MYSQL_v1.0.0.md                │
│    → POR QUÉ: Elegir PostgreSQL                            │
│    → Análisis de alternativas                              │
│    → Decisión fundamentada                                  │
│                                                             │
│ ✅ LOGICA_PROBLEMAS_CLEAN_CODE_v1.0.0.md                    │
│    → POR QUÉ: Ciertos problemas en el código              │
│    → Evidencia específica del proyecto                      │
│                                                             │
│ Características:                                            │
│ - Específico del proyecto                                   │
│ - Análisis de decisiones                                    │
│ - Comparación de opciones                                   │
│ - Justificación fundamentada                                │
└────────────────────────────────────────────────────────────┘
```

**CLAVE PARA DECIDIR:**

```python
def decidir_ubicacion(documento):
    """
    Decidir entre patrones/ o diseño/logica/
    """
    # Preguntas
    enfoque_patron = "¿El documento explica QUÉ es un patrón y CÓMO aplicarlo?"
    enfoque_decision = "¿El documento justifica POR QUÉ una decisión técnica?"
    
    if enfoque_patron == True and es_reutilizable:
        return "arquitectura/patrones/"
    
    elif enfoque_decision == True and es_especifico_proyecto:
        return "arquitectura/diseño/logica/"
    
    else:
        # Si tiene AMBOS enfoques, usar regla 60/40:
        if porcentaje_patron > 60:
            return "arquitectura/patrones/"
        else:
            return "arquitectura/diseño/logica/"
```

**EJEMPLO REAL - Service Layer:**

```
Tenemos 2 documentos sobre Service Layer:

1. ANALISIS_SERVICE_LAYER_REFACTORING_v1.0.0.md
   Contenido:
   - 40% QUÉ es Service Layer (teoría)
   - 30% CÓMO implementarlo (práctica)
   - 30% POR QUÉ aplicarlo
   
   Decisión: arquitectura/patrones/
   Razón: Mayormente sobre el PATRÓN (70% QUÉ+CÓMO)

2. ANALISIS_OPCION_B_SERVICE_LAYER_v1.0.0.md
   Contenido:
   - 20% QUÉ es Service Layer
   - 80% POR QUÉ refactorizar en IACT
   - Evidencia específica del código actual
   - Métricas de impacto
   
   Decisión: arquitectura/diseño/logica/
   Razón: Mayormente justificación de DECISIÓN (80% POR QUÉ)
```

**NOTA:** Ambos documentos son válidos y complementarios:
- `patrones/` → Para aprender sobre el patrón
- `diseño/logica/` → Para entender la decisión en IACT

---

### 2. analisis/

**Propósito:** Documentos que analizan QUÉ necesita el sistema y validan calidad.

```
analisis/
├── requisitos/          → QUÉ necesita (levantamiento)
│   ├── LEVANTAMIENTO_ESTADO_ACTUAL_v1.0.0.md
│   └── REQUISITOS_FUNCIONALES_v1.0.0.md
│
├── calidad/             → Validación, errores, problemas
│   ├── VALIDACION_CLEAN_CODE_REAL_v1.0.0.md
│   └── ANALISIS_CRITICO_CODIGO_v1.0.0.md
│
└── performance/         → Análisis de rendimiento
    └── ANALISIS_PERFORMANCE_DB_v1.0.0.md
```

**Ejemplos de documentos:**
- `requisitos/LEVANTAMIENTO_APPS_v1.0.0.md`
- `calidad/VALIDACION_CLEAN_CODE_v1.0.0.md`

**Pregunta clave:** ¿Este documento identifica QUÉ se necesita o valida calidad?

---

### 3. gestion/

**Propósito:** Información para stakeholders y decisores (ejecutiva).

```
gestion/
├── resumenes/           → Resumenes ejecutivos
│   ├── RESUMEN_EJECUTIVO_FINAL_v1.0.0.md
│   └── RESUMEN_EJECUTIVO_CODIGO_v1.0.0.md
│
├── guias/               → Guías de uso/operación
│   ├── GUIA_SETUP_v1.0.0.md
│   └── GUIA_DEPLOYMENT_v1.0.0.md
│
├── testing/             → Info ejecutiva sobre testing
│   └── RESUMEN_TESTING_v1.0.0.md
│
└── reportes/            → Reportes de progreso
    └── REPORTE_SEMANAL_v1.0.0.md
```

**Ejemplos de documentos:**
- `resumenes/RESUMEN_EJECUTIVO_v1.0.0.md`
- `guias/GUIA_USUARIO_v1.0.0.md`
- `reportes/STATUS_PROYECTO_v1.0.0.md`

**Pregunta clave:** ¿Este documento es para decisores/stakeholders?

---

### 4. soporte/

**Propósito:** Referencias, metodologías, índices, navegación.

```
soporte/
├── METODOLOGIA_ANALISIS_v1.0.0.md
├── METODOLOGIA_CREACION_DOCUMENTOS_v1.0.0.md
├── INDICE_MAESTRO_v1.0.0.md
├── GLOSARIO_v1.0.0.md
└── REFERENCIAS_v1.0.0.md
```

**Ejemplos de documentos:**
- `METODOLOGIA_ANALISIS_v1.0.0.md`
- `INDICE_MAESTRO_v1.0.0.md`

**Pregunta clave:** ¿Este documento ayuda a navegar o entender el proceso?

---

## PROCESO DE CREACIÓN DE DOCUMENTOS

### PASO 1: Identificar el Propósito

**Pregunta:** ¿Qué tipo de información contiene este documento?

```python
# Árbol de decisión

if documento_explica_COMO_construir:
    dominio = "arquitectura/"
    
    if es_plan_implementacion:
        ruta = "arquitectura/diseño/planes/"
    elif explica_POR_QUE_decision:
        ruta = "arquitectura/diseño/logica/"
    elif es_patron_diseño:
        ruta = "arquitectura/diseño/patrones/"
    elif es_estrategia_testing:
        ruta = "arquitectura/testing/"
    elif es_deployment:
        ruta = "arquitectura/deployment/"

elif documento_identifica_QUE_necesita:
    dominio = "analisis/"
    
    if es_levantamiento_requisitos:
        ruta = "analisis/requisitos/"
    elif es_validacion_calidad:
        ruta = "analisis/calidad/"
    elif es_analisis_performance:
        ruta = "analisis/performance/"

elif documento_para_STAKEHOLDERS:
    dominio = "gestion/"
    
    if es_resumen_ejecutivo:
        ruta = "gestion/resumenes/"
    elif es_guia_usuario:
        ruta = "gestion/guias/"
    elif es_reporte_progreso:
        ruta = "gestion/reportes/"

elif documento_es_REFERENCIA:
    dominio = "soporte/"
    ruta = "soporte/"
```

**Ejemplo Real:**

```
Documento: "ANALISIS_OPCION_B_SERVICE_LAYER"

Pregunta 1: ¿Explica CÓMO construir?
→ NO, explica POR QUÉ refactorizar

Pregunta 2: ¿Es análisis de QUÉ necesita?
→ NO

Pregunta 3: ¿Explica POR QUÉ una decisión técnica?
→ SÍ

Resultado: arquitectura/diseño/logica/
```

---

### PASO 2: Definir el Nombre del Archivo

**Convención de Nomenclatura:**

```
FORMATO:
{TIPO}_{TEMA}_{DETALLE}_v{VERSION}.md

REGLAS:
- MAYÚSCULAS con guiones bajos
- Descriptivo y específico
- Incluir versión semántica
- Sin espacios

EJEMPLOS CORRECTOS:
✓ ANALISIS_OPCIONES_TESTING_v1.0.0.md
✓ PLAN_ACCION_INMEDIATA_v1.0.0.md
✓ RESUMEN_EJECUTIVO_CODIGO_REAL_v1.0.0.md
✓ VALIDACION_CLEAN_CODE_REAL_v1.0.0.md
✓ METODOLOGIA_CREACION_DOCUMENTOS_v1.0.0.md

EJEMPLOS INCORRECTOS:
✗ analisis.md                      (no descriptivo)
✗ opciones de testing.md           (espacios)
✗ ANALISIS_OPCIONES.md             (sin versión)
✗ testing_analisis_v1.0.0.md       (orden inconsistente)
```

**Componentes del Nombre:**

```
1. TIPO (obligatorio):
   - ANALISIS: Análisis técnico
   - PLAN: Plan de acción
   - RESUMEN: Resumen ejecutivo
   - VALIDACION: Validación de calidad
   - METODOLOGIA: Proceso/metodología
   - GUIA: Guía de usuario
   - REPORTE: Reporte de progreso

2. TEMA (obligatorio):
   - Tema principal del documento
   - Ejemplos: OPCIONES, TESTING, CODIGO, CLEAN_CODE

3. DETALLE (opcional):
   - Información adicional específica
   - Ejemplos: COMPLETO, INMEDIATA, REAL

4. VERSION (obligatorio):
   - Formato: v{MAJOR}.{MINOR}.{PATCH}
   - Ejemplos: v1.0.0, v1.1.0, v2.0.0
```

---

### PASO 3: Verificar/Crear Ruta

**Algoritmo:**

```python
def crear_documento(nombre_archivo, contenido):
    """
    Crear documento en la ruta correcta.
    
    Args:
        nombre_archivo: Nombre del archivo
        contenido: Contenido del documento
    """
    # 1. Identificar dominio semántico
    ruta_base = "/tmp/iact-real/docs/"
    ruta_completa = identificar_ruta_semantica(nombre_archivo, contenido)
    
    # 2. Verificar si ruta existe
    ruta_full = ruta_base + ruta_completa
    
    if not exists(ruta_full):
        # 3. Crear ruta completa (mkdir -p)
        crear_directorios(ruta_full)
        print(f"✓ Ruta creada: {ruta_full}")
    else:
        print(f"✓ Ruta existe: {ruta_full}")
    
    # 4. Crear archivo
    archivo_path = ruta_full + nombre_archivo
    
    if exists(archivo_path):
        print(f"⚠️  Archivo existe, creando versión nueva")
        # Incrementar versión o usar timestamp
        archivo_path = generar_nombre_unico(archivo_path)
    
    # 5. Escribir contenido
    write_file(archivo_path, contenido)
    print(f"✓ Documento creado: {archivo_path}")
    
    # 6. Actualizar índice maestro
    actualizar_indice_maestro(archivo_path)
    
    return archivo_path
```

**Implementación Bash:**

```bash
#!/bin/bash
# crear_documento.sh

crear_documento() {
    local nombre_archivo=$1
    local ruta_semantica=$2
    local contenido=$3
    
    # Ruta base
    local base_dir="/tmp/iact-real/docs"
    local ruta_completa="${base_dir}/${ruta_semantica}"
    
    # Verificar/crear directorio
    if [ ! -d "$ruta_completa" ]; then
        echo "Creando ruta: $ruta_completa"
        mkdir -p "$ruta_completa"
    fi
    
    # Ruta del archivo
    local archivo="${ruta_completa}/${nombre_archivo}"
    
    # Verificar si archivo existe
    if [ -f "$archivo" ]; then
        echo "⚠️  Archivo existe: $archivo"
        read -p "¿Sobrescribir? (y/n): " respuesta
        if [ "$respuesta" != "y" ]; then
            echo "Cancelado"
            return 1
        fi
    fi
    
    # Crear archivo
    echo "$contenido" > "$archivo"
    echo "✓ Documento creado: $archivo"
    
    # Actualizar índice
    actualizar_indice "$archivo"
    
    return 0
}

# Ejemplo de uso:
crear_documento \
    "ANALISIS_OPCION_B_v1.0.0.md" \
    "arquitectura/diseño/logica" \
    "$contenido_documento"
```

---

### PASO 4: Crear Header del Documento

**Template Obligatorio:**

```markdown
---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: [Tipo de Documento]
categoria: [Categoría Semántica]
autor: [Opcional]
---

# TÍTULO DEL DOCUMENTO

---

## CONTENIDO
...
```

**Ejemplo Real:**

```markdown
---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis Técnico - Refactoring
categoria: arquitectura/diseño/logica
autor: Claude Analysis
---

# ANÁLISIS OPCIÓN B: MOVER LÓGICA DEL MODEL AL SERVICE

---

## TABLA DE CONTENIDOS
1. [Contexto](#contexto)
2. [Problema Actual](#problema)
...
```

**Campos Obligatorios:**

```yaml
version:    Versión semántica del documento
date:       Fecha de creación YYYY-MM-DD
project:    Nombre del proyecto
type:       Tipo de documento (descripción)
categoria:  Ruta semántica del documento
```

**Campos Opcionales:**

```yaml
autor:      Autor del documento
status:     draft, review, approved, deprecated
tags:       Lista de etiquetas
relacionado: Documentos relacionados
```

---

### PASO 5: Estructurar el Contenido

**Estructura Estándar:**

```markdown
# TÍTULO PRINCIPAL

---

## TABLA DE CONTENIDOS
(Para documentos >5 páginas)

---

## 1. CONTEXTO
- Situación actual
- Problema a resolver
- Alcance del documento

## 2. ANÁLISIS
- Análisis detallado
- Evidencia
- Datos

## 3. OPCIONES/SOLUCIONES
- Opción 1
- Opción 2
- Opción N

## 4. RECOMENDACIONES
- Recomendación principal
- Justificación
- Próximos pasos

## 5. ANEXOS (opcional)
- Referencias
- Código de ejemplo
- Glosario

---

**FIN DEL DOCUMENTO**

Version: 1.0.0
Fecha: 2026-01-17
...
```

---

### PASO 6: Actualizar Índice Maestro

**Después de crear cada documento:**

```python
def actualizar_indice_maestro(nuevo_documento):
    """
    Actualizar INDICE_MAESTRO_ANALISIS con nuevo documento.
    
    Args:
        nuevo_documento: Path del documento creado
    """
    indice_path = "/tmp/iact-real/docs/soporte/INDICE_MAESTRO_v1.0.0.md"
    
    # Extraer metadata
    metadata = extraer_metadata(nuevo_documento)
    
    # Categoría semántica
    categoria = metadata['categoria']
    
    # Agregar entrada al índice
    entrada = f"""
### {metadata['type']}
**Archivo:** [{metadata['nombre']}]({nuevo_documento})  
**Versión:** {metadata['version']}  
**Fecha:** {metadata['date']}  
**Descripción:** {metadata['descripcion']}
"""
    
    # Insertar en sección correspondiente
    insertar_en_seccion(indice_path, categoria, entrada)
    
    print(f"✓ Índice maestro actualizado")
```

---

## EJEMPLOS COMPLETOS

### Ejemplo 1: Documento de Análisis Técnico

**Paso 1: Identificar propósito**
```
Documento: Análisis de por qué refactorizar models a services
Pregunta: ¿Explica POR QUÉ una decisión técnica?
Respuesta: SÍ
Categoría: arquitectura/diseño/logica/
```

**Paso 2: Nombre**
```
ANALISIS_REFACTORING_MODEL_SERVICE_v1.0.0.md
```

**Paso 3: Verificar/crear ruta**
```bash
mkdir -p /tmp/iact-real/docs/arquitectura/diseño/logica
```

**Paso 4: Crear header**
```yaml
---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: Análisis Técnico - Refactoring
categoria: arquitectura/diseño/logica
---
```

**Paso 5: Contenido**
```markdown
# ANÁLISIS: REFACTORING MODEL → SERVICE LAYER

## CONTEXTO
...

## ANÁLISIS
...

## RECOMENDACIÓN
...
```

**Paso 6: Actualizar índice**
```
✓ Entrada agregada a INDICE_MAESTRO
```

---

### Ejemplo 2: Guía de Patrón de Diseño

**Paso 1: Identificar propósito**
```
Documento: Guía completa del patrón Service Layer
Pregunta: ¿Explica QUÉ es un patrón y CÓMO aplicarlo?
Respuesta: SÍ
Categoría: arquitectura/patrones/
```

**Paso 2: Nombre**
```
SERVICE_LAYER_PATTERN_GUIA_v1.0.0.md
```

**Paso 3: Verificar/crear ruta**
```bash
mkdir -p /tmp/iact-real/docs/arquitectura/patrones
```

**Paso 4: Crear header**
```yaml
---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: Guía de Patrón de Diseño
categoria: arquitectura/patrones
---
```

**Paso 5: Contenido**
```markdown
# SERVICE LAYER PATTERN - GUÍA COMPLETA

## QUÉ ES
Definición del patrón...

## FUNDAMENTOS
Clean Code, Martin Fowler...

## CÓMO IMPLEMENTAR
Paso a paso...

## EJEMPLOS
Código de ejemplo...
```

**Paso 6: Actualizar índice**
```
✓ Entrada agregada a INDICE_MAESTRO
```

---

### Ejemplo 3: Resumen Ejecutivo

**Paso 1: Identificar propósito**
```
Documento: Resumen de estado del proyecto para stakeholders
Pregunta: ¿Es para decisores?
Respuesta: SÍ
Categoría: gestion/resumenes/
```

**Paso 2: Nombre**
```
RESUMEN_EJECUTIVO_ESTADO_PROYECTO_v1.0.0.md
```

**Paso 3: Verificar/crear ruta**
```bash
ls /tmp/iact-real/docs/gestion/resumenes/
# Ya existe ✓
```

**Paso 4: Crear header**
```yaml
---
version: 1.0.0
date: 2026-01-17
project: IACT Call Center System
type: Resumen Ejecutivo
categoria: gestion/resumenes
---
```

---

## VALIDACIÓN DE UBICACIÓN

### Checklist de Validación:

```
ANTES DE CREAR DOCUMENTO:

□ He identificado el propósito del documento
□ He elegido la categoría semántica correcta
□ El nombre es descriptivo y sigue convención
□ La ruta existe o la crearé
□ El header está completo
□ La estructura es adecuada al tipo

DESPUÉS DE CREAR DOCUMENTO:

□ El documento está en la ruta correcta
□ El nombre es único (no duplicado)
□ El índice maestro está actualizado
□ El documento tiene tabla de contenidos (si >5 pág)
□ Los links relativos funcionan
□ La versión es correcta
```

---

## CASOS ESPECIALES

### Caso 1: Documento Pertenece a Múltiples Categorías

**Solución:** Ubicar en categoría PRINCIPAL, referenciar en otras

```
Documento: "Guía de Testing para Stakeholders"

¿Es arquitectura? (testing) → Parcialmente
¿Es gestión? (guía stakeholders) → Principalmente

Decisión: gestion/guias/GUIA_TESTING_STAKEHOLDERS_v1.0.0.md

Referencias:
- En arquitectura/testing/README.md → Link al documento
- En soporte/INDICE_MAESTRO → En ambas secciones
```

---

### Caso 2: Documento Temporal o Draft

**Solución:** Usar subcarpeta `drafts/` o marcar en header

```yaml
---
version: 0.1.0      # <1.0.0 indica draft
status: draft
---
```

O ubicar en:
```
/tmp/iact-real/docs/drafts/
└── BORRADOR_ANALISIS_XYZ_v0.1.0.md
```

---

### Caso 3: Actualización de Documento

**Solución:** Incrementar versión, mantener nombre

```
Original: ANALISIS_OPCIONES_v1.0.0.md

Actualización menor: ANALISIS_OPCIONES_v1.1.0.md
Actualización mayor: ANALISIS_OPCIONES_v2.0.0.md

Mantener ambos o archivar versión vieja:
/tmp/iact-real/docs/arquitectura/testing/
├── ANALISIS_OPCIONES_v1.0.0.md         (archivar)
├── ANALISIS_OPCIONES_v2.0.0.md         (actual)
└── archive/
    └── ANALISIS_OPCIONES_v1.0.0.md     (backup)
```

---

## HERRAMIENTAS DE APOYO

### Script: identificar_categoria.sh

```bash
#!/bin/bash
# identificar_categoria.sh
# Ayuda a identificar la categoría semántica de un documento

identificar_categoria() {
    echo "=== IDENTIFICADOR DE CATEGORÍA SEMÁNTICA ==="
    echo ""
    
    # Pregunta 1
    read -p "¿El documento explica CÓMO construir algo? (y/n): " respuesta1
    if [ "$respuesta1" = "y" ]; then
        echo "Dominio: arquitectura/"
        
        read -p "¿Es un plan de implementación? (y/n): " respuesta2
        if [ "$respuesta2" = "y" ]; then
            echo "Categoría: arquitectura/diseño/planes/"
            return
        fi
        
        read -p "¿Explica POR QUÉ una decisión técnica? (y/n): " respuesta3
        if [ "$respuesta3" = "y" ]; then
            echo "Categoría: arquitectura/diseño/logica/"
            return
        fi
        
        read -p "¿Es sobre testing? (y/n): " respuesta4
        if [ "$respuesta4" = "y" ]; then
            echo "Categoría: arquitectura/testing/"
            return
        fi
        
        echo "Categoría: arquitectura/ (revisar subcategoría)"
        return
    fi
    
    # Pregunta 2
    read -p "¿El documento analiza QUÉ necesita el sistema? (y/n): " respuesta5
    if [ "$respuesta5" = "y" ]; then
        echo "Dominio: analisis/"
        
        read -p "¿Es levantamiento de requisitos? (y/n): " respuesta6
        if [ "$respuesta6" = "y" ]; then
            echo "Categoría: analisis/requisitos/"
            return
        fi
        
        read -p "¿Es validación de calidad? (y/n): " respuesta7
        if [ "$respuesta7" = "y" ]; then
            echo "Categoría: analisis/calidad/"
            return
        fi
        
        echo "Categoría: analisis/ (revisar subcategoría)"
        return
    fi
    
    # Pregunta 3
    read -p "¿El documento es para stakeholders/decisores? (y/n): " respuesta8
    if [ "$respuesta8" = "y" ]; then
        echo "Dominio: gestion/"
        
        read -p "¿Es un resumen ejecutivo? (y/n): " respuesta9
        if [ "$respuesta9" = "y" ]; then
            echo "Categoría: gestion/resumenes/"
            return
        fi
        
        read -p "¿Es una guía de usuario? (y/n): " respuesta10
        if [ "$respuesta10" = "y" ]; then
            echo "Categoría: gestion/guias/"
            return
        fi
        
        echo "Categoría: gestion/ (revisar subcategoría)"
        return
    fi
    
    # Por defecto
    echo "Categoría: soporte/ (metodologías/referencias)"
}

# Ejecutar
identificar_categoria
```

---

## CONCLUSIÓN

### Proceso Resumido:

```
1. IDENTIFICAR propósito → Categoría semántica
2. DEFINIR nombre → Convención nomenclatura  
3. VERIFICAR ruta → Crear si no existe
4. CREAR header → Metadata completo
5. ESTRUCTURAR contenido → Template adecuado
6. ACTUALIZAR índice → Mantener navegación
```

### Principios Clave:

```
✓ Organizar por DOMINIO, no por TIPO
✓ Nombres descriptivos y versionados
✓ Header completo con metadata
✓ Estructura consistente
✓ Índice siempre actualizado
```

### Beneficios:

```
✅ Documentos fáciles de encontrar
✅ Estructura escalable
✅ Navegación intuitiva
✅ Mantenimiento simple
✅ Colaboración eficiente
```

---

**FIN DE LA METODOLOGÍA**

Version: 1.0.0
Fecha: 2026-01-17
Categoría: soporte
Autor: Claude

**Documentos Relacionados:**
- INDICE_MAESTRO_ANALISIS_v1.0.0.md
- METODOLOGIA_ANALISIS_v1.0.0.md

