# Plan sintético de performance: HU-DEMO-001

> Ejemplo documental. Los valores proceden de fuentes sintéticas y no deben reutilizarse como defaults.

## Control

- Estado: listo para revisión.
- Decisión: evaluar si el flujo de consulta cumple NFR-SYN-03 bajo TRAFFIC-SYN-12.
- Destino: ambiente `qa-synthetic`, no productivo.
- URL: suministrada en ejecución mediante `BASE_URL`.
- Owner del plan: `QA-SYNTHETIC`.

## Fuentes

| ID | Fuente sintética | Decisión aportada |
|---|---|---|
| NFR-SYN-03 | `performance-input/HU-DEMO-001/nfr.md` | p95 y tasa de errores |
| TRAFFIC-SYN-12 | `performance-input/HU-DEMO-001/traffic-model.csv` | concurrencia, ramp-up y duración |
| STOP-SYN-01 | `performance-input/HU-DEMO-001/environment.md` | condición de parada |

## Objetivo y riesgo

El ejercicio evalúa la degradación del flujo `GET /orders/{id}` durante una ventana sintética comparable con la hora pico descrita por TRAFFIC-SYN-12. La decisión posterior es mantener el build como candidato o solicitar diagnóstico.

## Alcance

- Consulta de un pedido sintético existente.
- Estado estable de diez minutos después del ramp-up.
- Métricas de aplicación, pool de conexiones y dependencia de almacenamiento.

## Fuera de alcance

- Escrituras, autenticación y creación de pedidos.
- Producción o extrapolación lineal hacia producción.
- Pruebas de estrés y duración prolongada.

## Escenario PERF-01

- Fuente de carga: `TRAFFIC-SYN-12`.
- Modelo: 20 usuarios concurrentes.
- Ramp-up: 120 segundos.
- Estado estable: 600 segundos.
- Mezcla: 100 % consulta.
- Datos: identificadores `ORDER-SYNTHETIC-*`, sin estado real.

## Criterios

| Criterio | Umbral sintético | Fuente |
|---|---|---|
| NFR-SYN-03-p95 | p95 menor o igual a 800 ms durante estado estable | NFR-SYN-03 |
| NFR-SYN-03-errors | tasa de errores menor a 1 % durante estado estable | NFR-SYN-03 |

## Ambiente y limitaciones

El ambiente tiene 50 % de la capacidad declarada para producción en ENV-SYN-02. El resultado solo compara builds dentro de esta topología. El presupuesto agregado de la ventana es de 20 usuarios y requiere confirmación del owner antes de autorizar ejecución.

## Observabilidad

| Hipótesis | Señal | Fuente | Owner |
|---|---|---|---|
| Saturación de cómputo | CPU y memoria por tarea | dashboard sintético | APP-SYNTHETIC |
| Espera por conexión | conexiones activas y pendientes | dashboard sintético | DATA-SYNTHETIC |
| Error de dependencia | latencia y errores de almacenamiento | dashboard sintético | DATA-SYNTHETIC |

## Condición de parada

STOP-SYN-01 ordena detener cuando la tasa de errores sea al menos 5 % durante 60 segundos o cuando el owner del ambiente declare una señal crítica. `QA-SYNTHETIC` coordina la parada por el canal acordado antes de la ejecución.

## Evidencia

- JMX y propiedades efectivas.
- JTL completo, log y dashboard HTML.
- Metadata con build, commit, ventana y configuración.
- Exportes de observabilidad de la misma ventana y zona horaria.

## Supuestos y pendientes

- Los valores solo ilustran trazabilidad a fuentes sintéticas.
- Autorización de ejecución: `NO_SUMINISTRADO`.
- Build y commit futuros: `NO_SUMINISTRADO`.
