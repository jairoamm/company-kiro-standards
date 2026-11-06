---
name: analyze-jmeter-report
description: Analiza una ejecución JMeter ya finalizada contra su plan, configuración efectiva y observabilidad, incluida la revisión de JTL y errorCount. Úsalo para producir conclusiones técnicas y ejecutivas sin reenviar tráfico.
---

# Analizar reporte JMeter

## Propósito

Evaluar evidencia de una ejecución JMeter terminada y decidir cada criterio como aprobado, fallido o inconcluso. El procedimiento distingue hechos, correlaciones e hipótesis; no vuelve a ejecutar carga, no cambia umbrales y no atribuye una causa sin evidencia.

## Cuándo usarla

Úsala cuando exista un JTL o dashboard completo, metadata del run y métricas de la misma ventana. No la uses para crear el plan, generar el JMX, recuperar evidencia ausente mediante otra ejecución ni validar un destino en vivo.

## Políticas relacionadas

Aplica `steering/qa/test-automation-standards.md`, `steering/core/security.md` y `steering/core/engineering-quality.md`. `skills/performance/create-performance-plan/SKILL.md` define los criterios y `skills/performance/generate-jmeter-project/SKILL.md` define el proyecto; este procedimiento analiza su evidencia.

## Entradas obligatorias

Proporciona rutas locales para:

- `performance/<HU>/plan/performance-plan.md`: plan y umbrales aprobados antes del run.
- `performance/<HU>/jmeter/test-plan.jmx`: JMX o configuración efectiva versionada.
- `performance/<HU>/results/<RUN_ID>/results.jtl`: JTL completo en CSV o XML.
- `performance/<HU>/results/<RUN_ID>/html/`: reporte HTML, incluido `statistics.json` cuando esté disponible.
- `performance/<HU>/results/<RUN_ID>/run-metadata.json`: fecha, ventana, ambiente, build, commit, versión de JMeter, tasa o concurrencia efectiva y motivo de terminación.
- `performance/<HU>/results/<RUN_ID>/jmeter.log`: log de la ejecución.
- Exportes de métricas de aplicación, infraestructura y dependencias para la misma ventana, con zona horaria.
- Eventos operativos, cambios y línea base comparable, si se utilizará una comparación.

Los archivos deben estar sanitizados o manejarse en una ubicación autorizada. No copies secretos a los reportes derivados.

## Precondiciones y bloqueos

Antes de concluir:

- El run corresponde al ambiente, build, commit y ventana declarados.
- La configuración efectiva puede compararse con el plan aprobado.
- El JTL está completo y su formato es conocido.
- Los relojes y zonas horarias de JMeter y observabilidad pueden alinearse.
- Calentamiento, estado estable, picos y recuperación pueden distinguirse o se declara la limitación.
- Los datos permiten calcular los percentiles exigidos por el plan.

Si falta el JTL, no se conoce la configuración efectiva o el run terminó antes del período evaluable, marca el análisis como `inconcluso`. No infieras resultados desde screenshots parciales.

## Procedimiento

1. Inventaría plan, JMX, JTL, dashboard, log, metadata y métricas con tamaño, hash o referencia de procedencia.
2. Verifica ambiente, build, commit, ventana, zona horaria y versión de JMeter.
3. Compara usuarios o tasa, ramp-up, duración, mezcla, timeouts y assertions efectivos con el plan. Registra cada desviación.
4. Revisa el estado del proceso, pero no lo uses como veredicto. JMeter puede devolver exit code `0` con samples o assertions fallidas.
5. Inspecciona `success=false`, mensajes de assertion y errores en el JTL. Contrasta el total con `errorCount` por transacción en `statistics.json` o el dashboard.
6. Calcula o extrae muestras, throughput, error rate y los percentiles exigidos. No sustituyas percentiles con promedios.
7. Separa calentamiento, estado estable, pico y recuperación cuando la ventana lo permita.
8. Evalúa cada criterio como `aprobado`, `fallido` o `inconcluso`, con fórmula y referencia de evidencia.
9. Alinea CPU, memoria, conexiones, colas, dependencias, autoscaling y errores con la línea de tiempo.
10. Formula hipótesis de cuello de botella con evidencia a favor, evidencia en contra y un experimento siguiente. No declares causa raíz solo por coincidencia temporal.
11. Compara con una línea base únicamente si escenario, datos, build, capacidad y configuración son comparables. Documenta diferencias.
12. Sanitiza ejemplos de error y genera un reporte técnico y un resumen ejecutivo. Revisa que ambos expresen el mismo veredicto.

## Archivos de salida

```text
performance/<HU>/analysis/<RUN_ID>/
├── technical-report.md
├── executive-summary.md
├── criteria.csv
├── sanitized-errors.csv
└── evidence-inventory.md
```

`technical-report.md` contiene configuración efectiva, calidad de datos, métricas, errores, línea de tiempo, correlaciones, hipótesis y limitaciones. `executive-summary.md` contiene objetivo, veredicto, criterios fallidos o inconclusos, riesgo y decisiones pendientes.

## Ejemplo de prompt

```text
Analiza el run RUN-2026-11-03-01 de HU-DEMO-001 con su plan, JMX, results.jtl,
statistics.json, metadata y métricas de la misma ventana. Revisa success=false y errorCount,
sanitiza errores y genera reportes bajo performance/HU-DEMO-001/analysis/<RUN_ID>.
No ejecutes JMeter, no cambies umbrales y no declares causa raíz sin evidencia.
```

## Ejemplo de salida

Extracto de `criteria.csv`:

```csv
criterion,status,observed,threshold,evidence
NFR-03-p95,failed,920 ms,<= 800 ms,statistics.json:GET_orders
NFR-03-errors,failed,2.4 %,< 1 %,results.jtl success=false + errorCount=29
PERF-STOP-01,inconclusive,no metric export,>= 5 % for 60 s,observability export missing
```

Extracto técnico:

```markdown
### Hipótesis H-01 — saturación del pool de conexiones
Evidencia a favor: p95 aumenta en la misma ventana en que el pool alcanza su máximo.
Evidencia en contra: no existe métrica de tiempo de espera por conexión.
Conclusión: hipótesis pendiente; no es causa raíz confirmada.
Siguiente experimento: repetir el escenario aprobado después de habilitar esa métrica,
mediante una autorización nueva y separada.
```

## Validación

Comprueba presencia y fallos registrados sin enviar tráfico:

```bash
HU="${HU:?defina HU}"
RUN_ID="${RUN_ID:?defina RUN_ID}"
RESULT_ROOT="performance/$HU/results/$RUN_ID"
test -s "$RESULT_ROOT/results.jtl"
test -s "$RESULT_ROOT/run-metadata.json"
python3 -m json.tool "$RESULT_ROOT/run-metadata.json" >/dev/null
python3 -c 'import csv,sys; rows=csv.DictReader(open(sys.argv[1], encoding="utf-8")); failed=sum(row.get("success", "").lower() == "false" for row in rows); print(f"jtl_failures={failed}")' \
  "$RESULT_ROOT/results.jtl"
python3 -c 'import json,sys; data=json.load(open(sys.argv[1], encoding="utf-8")); print({name: value.get("errorCount") for name, value in data.items() if isinstance(value, dict)})' \
  "$RESULT_ROOT/html/statistics.json"
git diff --check -- "performance/$HU/analysis/$RUN_ID"
```

Los dos comandos de conteo asumen JTL CSV y `statistics.json` disponible. Si el JTL es XML o el dashboard no se generó, documenta el formato y usa el parser local ya aprobado; no omitas la comprobación. Los conteos del JTL y `errorCount` MUST reconciliarse aunque el proceso haya terminado con `0`, porque el exit code no representa todas las assertions.

## Manejo de fallos

- **JTL ausente, truncado o ilegible:** marca el análisis inconcluso y solicita el artefacto original; no uses solo el HTML.
- **Configuración distinta del plan:** reporta la desviación y evalúa si invalida uno o más criterios.
- **Conteos JTL y dashboard no coinciden:** no elijas el resultado más favorable; investiga filtros, muestras descartadas y generación del dashboard.
- **Ventanas o zonas horarias incompatibles:** evita correlaciones y solicita exportes alineados.
- **Metadata incompleta:** no atribuyas el resultado a un build o ambiente sin evidencia.
- **Datos sensibles:** detén la publicación, crea una copia sanitizada y conserva el original solo en la ubicación autorizada.
- **Causa no demostrada:** expresa una hipótesis y el experimento necesario, no una conclusión causal.

## Límites y responsabilidades

- QA mantiene la evaluación contra criterios y coordina la revisión con owners técnicos y de negocio.
- Los owners de aplicación e infraestructura revisan hipótesis y evidencia de sus componentes.
- Este procedimiento analiza archivos existentes; no ejecuta JMeter, no reenvía tráfico y no modifica el ambiente.
- No cambies umbrales después de conocer el resultado ni ocultes errores, muestras descartadas o terminación anticipada.
- No extrapoles capacidad de producción sin justificar diferencias de topología y escala.
- No almacenes secretos, identificadores sensibles ni payloads reales en salidas compartidas.
- El análisis sustenta una decisión humana; no certifica por sí mismo capacidad ni una Historia de Usuario.
