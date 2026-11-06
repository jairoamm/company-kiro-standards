---
name: create-performance-plan
description: Crea un plan de performance con objetivos, carga, observabilidad y condiciones de parada trazables a fuentes aprobadas. Úsalo antes de generar JMeter y sin enviar tráfico.
---

# Crear plan de performance

## Propósito

Convertir un riesgo o requisito no funcional en un plan revisable que defina qué medir, con qué carga y bajo qué condiciones. El resultado prepara una decisión; no autoriza carga ni demuestra capacidad.

## Cuándo usarla

Úsala antes de construir JMeter o cuando un plan carece de fuentes, umbrales u observabilidad. No la uses para asignar objetivos genéricos ni analizar una ejecución terminada.

## Políticas relacionadas

Aplica `steering/qa/test-automation-standards.md`, `steering/core/security.md` y `steering/core/engineering-quality.md`.

## Recursos incluidos

- [Plan completo con fuentes sintéticas](examples/performance-plan.md)
- [Modelo de carga del ejemplo](examples/load-model.csv)
- [Plantilla de plan sin valores operativos](templates/performance-plan.md)
- [Plantilla de modelo de carga](templates/load-model.csv)

Los números del ejemplo pertenecen solo a fuentes sintéticas declaradas; nunca son defaults.

## Entradas obligatorias

- `performance-input/<HU>/user-story.md` y `nfr.md`.
- `performance-input/<HU>/traffic-model.csv`.
- `performance-input/<HU>/environment.md` y `observability.md`.
- `performance-input/<HU>/test-data.md`, con datos sintéticos y limpieza.
- Línea base comparable, si existe.
- Responsables de ambiente, ejecución, monitoreo y decisión.

Cada número MUST citar una fuente aprobada o quedar `NO_SUMINISTRADO`, porque un valor ilustrativo no es un compromiso.

## Precondiciones y bloqueos

Confirma riesgo medible, destino no productivo, modelo que distingue tasa o concurrencia, duración y volumen, umbrales con owner, capacidad compartida, observabilidad y condiciones de parada. Si falta carga o umbral, produce como máximo un borrador bloqueado.

## Procedimiento

1. Registra objetivo, decisión, riesgo y fuentes.
2. Separa requisitos confirmados, supuestos y preguntas con owner y fecha.
3. Define alcance y exclusiones por operación y dependencia.
4. Incluye solo escenarios que respondan al riesgo.
5. Copia carga, ramp-up, duración, mezcla y volumen desde fuentes; verifica coherencia.
6. Relaciona latencia, throughput y errores con cada NFR aprobado.
7. Define datos sintéticos, preparación, aislamiento, rotación y limpieza.
8. Mapea señales de aplicación, infraestructura y dependencias a las hipótesis.
9. Documenta capacidad, diferencias frente a producción y presupuesto agregado.
10. Define condiciones de parada observables, responsable y canal.
11. Define evidencia, metadata y responsables de revisión.
12. Registra la revisión de aplicación, ambiente y QA sin borrar decisiones rechazadas.

## Archivos de salida

```text
performance/<HU>/plan/
├── performance-plan.md
├── load-model.csv
├── observability-map.md
├── authorization-checklist.md
└── data/README.md
```

El checklist prepara una autorización posterior; no la concede.

## Ejemplo de prompt

```text
Crea el plan de HU-DEMO-001 desde NFR, modelo de tráfico, ambiente y observabilidad.
Conserva valores aprobados, usa NO_SUMINISTRADO para faltantes y no generes JMX,
no inventes carga o umbrales y no envíes tráfico.
```

## Ejemplo de salida

```text
Escenario: PERF-01
Carga: trazada a TRAFFIC-SYN-12
Criterios: trazados a NFR-SYN-03
Destino: no productivo; valor suministrado mediante BASE_URL
Estado: listo solo después de aprobación de owners
```

El [plan completo](examples/performance-plan.md) explica fuentes, límites y parada.

## Validación

Ejecuta comprobaciones locales y finitas:

```bash
HU="${HU:?defina HU}"
test -s "performance/$HU/plan/performance-plan.md"
test -s "performance/$HU/plan/load-model.csv"
test -s "performance/$HU/plan/authorization-checklist.md"
python3 -c 'import csv,sys; list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))' \
  "performance/$HU/plan/load-model.csv"
git diff --check -- "performance/$HU/plan"
```

La revisión humana confirma cada fuente. Ningún comando envía tráfico.

## Manejo de fallos

- **Objetivo no medible:** reformúlalo con el owner; no elijas un umbral.
- **Carga o umbral sin fuente:** marca decisión pendiente y bloquea estado listo.
- **Ambiente incierto o productivo:** detén preparación para ejecución.
- **Capacidad compartida desconocida:** solicita presupuesto agregado.
- **Observabilidad insuficiente:** declara conclusiones que no podrán sostenerse.
- **Datos no sintéticos:** recházalos y solicita reemplazo.

## Límites y responsabilidades

- Negocio o producto aprueba objetivo y riesgo.
- Aplicación y ambiente confirman capacidad, observabilidad y parada.
- QA mantiene plan y coordina autorización separada.
- No generes JMX ni envíes tráfico.
- No inventes carga, distribución, duración, percentiles o umbrales.
- No almacenes secretos, endpoints sensibles ni datos reales.
- Un plan aprobado define el experimento; no certifica capacidad.
