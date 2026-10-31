---
name: create-performance-plan
description: Diseña un plan de pruebas de performance basado en objetivos medibles, capacidad autorizada y patrones de uso. Úsalo antes de crear scripts JMeter o cuando faltan criterios claros de carga.
---

# Crear plan de performance

## Propósito

Convertir una necesidad de negocio en un plan de performance verificable. El resultado define qué medir y bajo qué condiciones; no genera tráfico ni declara capacidad sin evidencia.

## Entradas obligatorias

- Historia de Usuario, flujo o servicio bajo evaluación.
- Objetivo de negocio y riesgo.
- Línea base disponible, si existe.
- Patrón de tráfico esperado y operaciones principales.
- Ambiente no productivo y diferencias frente a producción.
- Datos sintéticos requeridos.
- Métricas de aplicación e infraestructura disponibles.
- Responsables de ambiente, ejecución y decisión.

## Procedimiento

1. Separa requisitos confirmados, supuestos y preguntas.
2. Define alcance y fuera de alcance.
3. Describe la mezcla de operaciones y los recorridos representativos.
4. Propón, para aprobación, pruebas de línea base, carga, estrés, picos o duración solo cuando respondan al riesgo.
5. Define tasa o concurrencia, ramp-up, duración y volumen con su fuente. Si no hay fuente, marca los valores como propuesta pendiente.
6. Define latencia por percentiles, throughput, errores y métricas de dependencias.
7. Establece criterios de aceptación, condiciones de parada y señales de saturación.
8. Documenta capacidad compartida, límites y carga agregada de todos los equipos.
9. Define evidencia, formato de reporte y responsables de revisión.
10. Identifica limitaciones que impiden extrapolar el resultado a producción.

## Salidas esperadas

- Objetivo y riesgo.
- Escenarios y mezcla de operaciones.
- Modelo de carga con fuentes o decisiones pendientes.
- Métricas y umbrales.
- Datos y precondiciones.
- Estrategia de observabilidad.
- Condiciones de parada.
- Matriz de responsabilidad.
- Evidencia esperada.
- Supuestos y limitaciones.

## Límites

- No inventes un objetivo de performance para una Historia de Usuario que no lo necesita.
- No uses valores genéricos como compromiso del sistema.
- No declares equivalencia entre QA y producción sin un análisis de capacidad.
- No ejecutes herramientas ni modifiques ambientes.
- Si no existe autorización, entrega un plan pendiente de aprobación o un ejercicio basado en resultados pregrabados.
