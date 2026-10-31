---
name: analyze-jmeter-report
description: Analiza resultados JMeter junto con el plan, la configuración efectiva y las métricas del sistema. Úsalo para producir hallazgos técnicos y un resumen ejecutivo sin confundir correlación con causa.
---

# Analizar reporte JMeter

## Propósito

Evaluar una ejecución ya finalizada y relacionar sus resultados con los criterios acordados. Este Skill analiza evidencia; no vuelve a ejecutar la prueba ni modifica umbrales.

## Entradas obligatorias

- Plan de performance aprobado.
- JMX o configuración efectiva de la ejecución.
- JTL o reporte HTML completo.
- Fecha, duración, ambiente, build y versión de JMeter.
- Tasa o concurrencia realmente aplicada.
- Métricas de aplicación e infraestructura de la misma ventana.
- Eventos, errores y motivo de terminación.

Si faltan elementos esenciales, declara el análisis inconcluso y enumera lo necesario.

## Procedimiento

1. Comprueba que el resultado pertenece al ambiente, build y ventana indicados.
2. Compara configuración efectiva con el plan aprobado.
3. Calcula o extrae muestras, throughput, errores y percentiles requeridos.
4. Evalúa cada criterio como aprobado, fallido o inconcluso.
5. Separa calentamiento, estado estable, picos y recuperación cuando los datos lo permitan.
6. Correlaciona resultados con CPU, memoria, concurrencia, colas, dependencias y errores.
7. Formula hipótesis de cuello de botella y registra evidencia a favor y en contra.
8. No atribuyas causa raíz solamente por coincidencia temporal.
9. Compara con una línea base únicamente si ambos experimentos son comparables.
10. Produce una sección técnica y otra ejecutiva con riesgos y siguientes pasos.

## Salidas esperadas

### Resumen ejecutivo

- Objetivo.
- Resultado general.
- Criterios fallidos.
- Riesgo de negocio.
- Recomendación y decisiones pendientes.

### Análisis técnico

- Configuración efectiva.
- Calidad y limitaciones de los datos.
- Tabla de métricas y percentiles.
- Errores por tipo.
- Línea de tiempo.
- Correlación con observabilidad.
- Hipótesis, evidencia y experimentos siguientes.

## Límites

- No ejecutes carga.
- No cambies umbrales después de conocer el resultado.
- No presentes promedios como sustitutos de percentiles.
- No extrapoles capacidad de producción sin justificar diferencias de ambiente.
- No ocultes muestras descartadas, errores o terminación anticipada.
- Redacta identificadores, tokens y datos sensibles antes de compartir el reporte.
