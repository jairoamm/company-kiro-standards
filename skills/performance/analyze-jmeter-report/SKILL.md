---
name: analyze-jmeter-report
description: Analiza una ejecución JMeter finalizada contra su plan y observabilidad, incluida la reconciliación de JTL y errorCount. Úsalo sin reenviar tráfico ni cambiar umbrales.
---

# Analizar reporte JMeter

## Propósito

Evaluar evidencia de un run terminado y decidir cada criterio como aprobado, fallido o inconcluso. Distingue hechos, correlaciones e hipótesis; no repite carga ni atribuye una causa sin evidencia.

## Cuándo usarla

Úsala con JTL o dashboard completo, metadata y métricas de la misma ventana. No la uses para crear plan o JMX, recuperar evidencia mediante otra ejecución ni validar un destino vivo.

## Políticas relacionadas

Aplica `steering/qa/test-automation-standards.md`, `steering/core/security.md` y `steering/core/engineering-quality.md`.

## Recursos incluidos

- [Reporte técnico sintético](examples/technical-report.md)
- [Criterios evaluados del ejemplo](examples/criteria.csv)
- [JTL sintético](examples/results.jtl) y [statistics.json sintético](examples/statistics.json)
- [Plantilla de reporte técnico](templates/technical-report.md)
- [Plantilla de criterios](templates/criteria.csv)
- [Reconciliador estático de errores](scripts/reconcile_jmeter_errors.py)

## Entradas obligatorias

- `performance/<HU>/plan/performance-plan.md` y JMX efectivo.
- `performance/<HU>/results/<RUN_ID>/results.jtl`, reporte HTML y `statistics.json` si existe.
- `run-metadata.json` y `jmeter.log`.
- Métricas de aplicación, infraestructura y dependencias de la misma ventana.
- Eventos, cambios y línea base comparable, si se usarán.

Los archivos deben estar sanitizados o permanecer en una ubicación autorizada.

## Precondiciones y bloqueos

Confirma ambiente, build, commit, configuración efectiva, JTL completo, formato, zonas horarias, fases de carga y percentiles requeridos. Los conteos JTL y `errorCount` MUST reconciliarse porque el exit code no representa assertions fallidas. Si falta JTL, no se conoce la configuración o el run terminó antes de la ventana evaluable, marca `inconcluso`.

## Procedimiento

1. Inventaría evidencia con tamaño, hash o procedencia.
2. Verifica ambiente, build, commit, ventana, zona horaria y versión.
3. Compara carga, ramp-up, duración, mezcla, timeouts y assertions con el plan.
4. Registra el exit code, pero no lo uses como veredicto.
5. Revisa `success=false` y reconcilia el total con `errorCount` mediante el script incluido.
6. Calcula muestras, throughput, errores y percentiles exigidos; no sustituyas percentiles por promedios.
7. Separa calentamiento, estado estable, pico y recuperación cuando sea posible.
8. Evalúa cada criterio como `aprobado`, `fallido` o `inconcluso`, con fórmula y evidencia.
9. Alinea señales técnicas con la línea de tiempo.
10. Formula hipótesis con evidencia a favor, en contra y próximo experimento; no declares causa raíz por coincidencia.
11. Compara con línea base solo si escenario, datos, build, capacidad y configuración son comparables.
12. Sanitiza errores y genera reporte técnico y resumen ejecutivo coherentes.

## Archivos de salida

```text
performance/<HU>/analysis/<RUN_ID>/
├── technical-report.md
├── executive-summary.md
├── criteria.csv
├── sanitized-errors.csv
└── evidence-inventory.md
```

El reporte técnico incluye calidad de datos, configuración, métricas, errores, correlaciones, hipótesis y límites.

## Ejemplo de prompt

```text
Analiza RUN-SYNTHETIC-001 con plan, JMX, JTL, statistics.json, metadata y métricas.
Revisa success=false y errorCount, sanitiza errores y genera los reportes. No ejecutes
JMeter, no cambies umbrales y no declares causa raíz sin evidencia.
```

## Ejemplo de salida

```csv
criterion,status,observed,threshold,evidence
NFR-SYN-03-errors,failed,33.3 %,< 1 %,results.jtl + statistics.json
```

El [reporte completo](examples/technical-report.md) mantiene la causa como hipótesis.

## Validación

Define `SKILL_DIR` como este directorio y no envíes tráfico:

```bash
HU="${HU:?defina HU}"
RUN_ID="${RUN_ID:?defina RUN_ID}"
SKILL_DIR="${SKILL_DIR:?defina la ruta de analyze-jmeter-report}"
RESULT_ROOT="performance/$HU/results/$RUN_ID"
python3 -m json.tool "$RESULT_ROOT/run-metadata.json" >/dev/null
python3 "$SKILL_DIR/scripts/reconcile_jmeter_errors.py" \
  --jtl "$RESULT_ROOT/results.jtl" \
  --statistics "$RESULT_ROOT/html/statistics.json"
git diff --check -- "performance/$HU/analysis/$RUN_ID"
```

El script acepta JTL CSV. Para XML usa un parser local aprobado y documenta el formato; nunca omitas la reconciliación.

## Manejo de fallos

- **JTL ausente, truncado o ilegible:** marca inconcluso; no uses solo HTML.
- **Configuración distinta:** registra desviación y criterios invalidados.
- **Conteos distintos:** investiga filtros, muestras descartadas y generación del dashboard.
- **Zonas horarias incompatibles:** evita correlaciones y solicita exportes alineados.
- **Metadata incompleta:** no atribuyas resultado a build o ambiente.
- **Datos sensibles:** detén publicación y crea una copia sanitizada.
- **Causa no demostrada:** expresa hipótesis y evidencia faltante.

## Límites y responsabilidades

- QA mantiene evaluación y coordina owners técnicos y de negocio.
- Aplicación e infraestructura revisan hipótesis de sus componentes.
- No ejecutes JMeter, reenvíes tráfico ni modifiques el ambiente.
- No cambies umbrales después del resultado ni ocultes errores.
- No extrapoles producción sin justificar topología y escala.
- No almacenes secretos, identificadores sensibles ni payloads reales.
- El análisis apoya una decisión humana; no certifica capacidad.
