---
name: create-performance-plan
description: Crea un plan de performance con objetivos, modelo de carga, observabilidad y condiciones de parada trazables a fuentes aprobadas. Úsalo antes de generar JMeter y sin enviar tráfico.
---

# Crear plan de performance

## Propósito

Convertir un riesgo de negocio o requisito no funcional en un plan revisable que defina qué medir, con qué carga y bajo qué condiciones. El resultado prepara una decisión y una ejecución posterior; no autoriza carga ni demuestra capacidad.

## Cuándo usarla

Úsala antes de construir un proyecto JMeter, cuando se incorpora un escenario de performance o cuando un plan existente carece de fuentes, umbrales u observabilidad. No la uses para asignar objetivos genéricos a toda Historia de Usuario ni para analizar una ejecución ya terminada.

## Políticas relacionadas

Aplica `steering/qa/test-automation-standards.md`, `steering/core/security.md` y `steering/core/engineering-quality.md`. Este procedimiento concreta la preparación del plan sin repetir el estándar general de performance.

## Entradas obligatorias

Recibe, en las rutas equivalentes del proyecto:

- `performance-input/<HU>/user-story.md`: Historia de Usuario, flujo o servicio y riesgo de negocio.
- `performance-input/<HU>/nfr.md`: objetivos no funcionales aprobados y su fuente.
- `performance-input/<HU>/traffic-model.csv`: operaciones, distribución, tasa o concurrencia, ramp-up, duración y volumen esperados.
- `performance-input/<HU>/environment.md`: destino no productivo, capacidad, topología y diferencias frente a producción.
- `performance-input/<HU>/observability.md`: métricas, dashboards, logs y responsables disponibles.
- `performance-input/<HU>/test-data.md`: datos sintéticos, aislamiento y limpieza.
- Línea base comparable, si existe, con build, configuración y ventana.
- Responsables de ambiente, ejecución, monitoreo y decisión.

Cada número MUST citar una fuente aprobada o quedar marcado como decisión pendiente, porque una estimación ilustrativa no constituye un compromiso.

## Precondiciones y bloqueos

Antes de marcar el plan como listo:

- Existe un riesgo o pregunta medible que justifica la prueba.
- El destino está identificado como no productivo y su owner conoce el ejercicio propuesto.
- El modelo de tráfico distingue tasa, concurrencia, duración y volumen.
- Los umbrales y percentiles tienen owner y fuente.
- La capacidad compartida y la carga simultánea de otros equipos están documentadas.
- Hay señales observables y condiciones de parada.

Si faltan carga o umbrales aprobados, puedes producir un borrador con `<PENDIENTE: owner/decisión>`, pero no lo declares listo para generar JMeter. Si la clasificación del ambiente es incierta, trátalo como bloqueado.

## Procedimiento

1. Registra objetivo, decisión que habilitará la prueba, riesgo y fuentes.
2. Separa requisitos confirmados, supuestos y preguntas abiertas. Asigna owner y fecha objetivo a cada pregunta.
3. Define alcance y fuera de alcance por operación, recorrido y dependencia.
4. Describe escenarios de línea base, carga, estrés, pico o duración únicamente cuando respondan al riesgo identificado.
5. Para cada escenario, copia tasa o concurrencia, ramp-up, duración, mezcla y volumen desde una fuente aprobada. Comprueba su coherencia aritmética.
6. Define latencia por percentiles, throughput y errores. Relaciona cada umbral con el NFR o decisión que lo originó.
7. Especifica datos sintéticos, preparación, aislamiento, rotación y limpieza.
8. Mapea métricas de aplicación, infraestructura y dependencias a las hipótesis que ayudarán a evaluar.
9. Documenta capacidad del ambiente, diferencias frente a producción, presupuesto agregado de carga y límites de dependencias.
10. Define condiciones de parada observables, responsable autorizado para detener y canal de coordinación.
11. Define archivos de evidencia, metadata de ejecución y responsables de revisión técnica y ejecutiva.
12. Revisa el plan con owners de aplicación, ambiente y QA. Registra decisiones; no borres supuestos rechazados sin dejar resolución.

## Archivos de salida

```text
performance/<HU>/plan/
├── performance-plan.md
├── load-model.csv
├── observability-map.md
├── authorization-checklist.md
└── data/
    └── README.md
```

`performance-plan.md` debe incluir objetivo, alcance, escenarios, criterios, ambiente, condiciones de parada, evidencia, responsabilidades, supuestos y limitaciones. `authorization-checklist.md` prepara la revisión; no concede autorización por sí mismo.

## Ejemplo de prompt

```text
Crea el plan de performance para HU-DEMO-001 usando nfr.md, traffic-model.csv,
environment.md y observability.md. Conserva los valores aprobados, marca cualquier dato
faltante como pendiente y genera archivos bajo performance/HU-DEMO-001/plan. No generes
JMX, no inventes carga o umbrales y no ejecutes tráfico.
```

## Ejemplo de salida

Fragmento ilustrativo, donde los números ya constan en `NFR-03` y `TRAFFIC-12`:

```markdown
### Escenario PERF-01 — consulta en estado estable
- Riesgo: degradación del flujo de consulta durante la hora pico.
- Fuente de carga: TRAFFIC-12 aprobado.
- Modelo: 20 usuarios concurrentes; ramp-up 120 s; estado estable 10 min.
- Criterio: p95 ≤ 800 ms y errores < 1 %, según NFR-03.
- Destino: `<AMBIENTE_NO_PRODUCTIVO_AUTORIZADO>`.
- Parada: error rate ≥ 5 % durante 60 s o señal crítica del owner del ambiente.
- Limitación: la capacidad del ambiente es 50 % de producción; no extrapolar linealmente.
```

Si `NFR-03` o `TRAFFIC-12` no existen, esos valores deben aparecer como pendientes y no como ejemplo aplicable.

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

La revisión humana confirma que cada carga y umbral tiene una fuente. Ningún comando de esta sección envía tráfico.

## Manejo de fallos

- **Objetivo no medible:** reformula la pregunta con el owner; no elijas un umbral por conveniencia.
- **Carga o umbral sin fuente:** marca owner y decisión pendiente; bloquea el estado listo.
- **Ambiente incierto o productivo:** detén la preparación para ejecución y solicita un destino no productivo autorizado.
- **Capacidad compartida desconocida:** documenta el riesgo y solicita presupuesto agregado antes de aprobar el plan.
- **Observabilidad insuficiente:** declara qué conclusiones no podrán sostenerse y añade una precondición.
- **Datos no sintéticos:** recházalos y solicita un conjunto seguro.

## Límites y responsabilidades

- El owner de negocio o producto aprueba el objetivo y el riesgo.
- Los owners de aplicación y ambiente confirman capacidad, observabilidad y condiciones de parada.
- QA mantiene el plan y coordina una autorización de ejecución separada.
- No generes JMX ni envíes tráfico como parte de este procedimiento.
- No inventes carga, distribución, duración, percentiles o umbrales.
- No almacenes secretos, endpoints sensibles ni datos reales en el plan.
- Un plan aprobado define el experimento; no certifica capacidad ni equivalencia con producción.
