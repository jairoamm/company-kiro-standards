# Reporte técnico sintético: RUN-SYNTHETIC-001

## Veredicto

**Fallido.** Los criterios sintéticos de latencia y errores no se cumplen. La condición de parada queda inconclusa porque falta el exporte de observabilidad.

## Calidad de evidencia

- JTL CSV: 3 muestras, completo para este ejemplo.
- `statistics.json`: 3 muestras y `errorCount=1`.
- Reconciliación: 1 fila con `success=false`; coincide con `errorCount` total.
- Metadata de build y commit: sintética.
- Exporte de observabilidad: `NO_SUMINISTRADO`.

## Configuración efectiva

La configuración declarada coincide con el escenario sintético PERF-01: 20 usuarios, ramp-up de 120 segundos y duración de 600 segundos. Este fixture abreviado contiene solo tres muestras para demostrar el análisis y no representa una ejecución real.

## Criterios

Consulta [criteria.csv](criteria.csv). NFR-SYN-03-p95 y NFR-SYN-03-errors fallan contra valores tomados del plan sintético. STOP-SYN-01 es inconcluso.

## Errores

Una muestra `GET orders` devolvió 503 y falló la assertion de status. El ejemplo no conserva payloads ni identificadores reales.

## Hipótesis H-01: espera en una dependencia

- Evidencia a favor: la muestra fallida también presenta la mayor latencia.
- Evidencia en contra: no existe un exporte de latencia de dependencias para la misma ventana.
- Conclusión: hipótesis pendiente; no es causa raíz confirmada.
- Próximo experimento: obtener observabilidad aprobada y decidir por separado si se autoriza otra ejecución.

## Limitaciones

- El conjunto es deliberadamente pequeño y sintético.
- No hay datos suficientes para extrapolar capacidad.
- No hay evidencia para evaluar la condición de parada durante 60 segundos.
