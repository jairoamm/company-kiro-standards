---
name: generate-jmeter-project
description: Genera un proyecto JMeter revisable a partir de un plan de performance aprobado, sin ejecutar carga. Úsalo cuando exista un objetivo no productivo autorizado, endpoints definidos y criterios medibles.
---

# Generar proyecto JMeter

## Propósito

Crear los archivos iniciales de un proyecto JMeter reproducible. Este Skill produce un borrador para revisión humana; nunca inicia JMeter ni envía tráfico.

## Entradas obligatorias

- Historia de Usuario o cambio relacionado.
- Objetivo de performance y razón de negocio.
- URL o variable de destino no productivo.
- Endpoints, métodos, contratos y secuencia.
- Modelo de carga: tasa o concurrencia, ramp-up y duración.
- Umbrales aprobados y percentiles requeridos.
- Datos sintéticos y estrategia de aislamiento.
- Mecanismo de autenticación aprobado, sin valores secretos.
- Condiciones de parada y responsable autorizado para ejecutar.

Si falta alguna entrada, crea una lista de decisiones pendientes. No inventes tasas, credenciales ni umbrales.

## Procedimiento

1. Confirma que el objetivo está identificado como no productivo y que existe autorización de carga.
2. Revisa el plan de performance y detecta contradicciones entre concurrencia, tasa, duración y volumen.
3. Modela grupos, transacciones, correlación, parametrización y assertions sin incluir secretos.
4. Usa variables para host, protocolo, credenciales indirectas, tasas y duración.
5. Define timeouts y fallos de assertion de forma explícita.
6. Mantén listeners pesados fuera de la ejecución de carga; prepara resultados JTL y reporte posterior.
7. Documenta cómo validar el proyecto con una ejecución mínima, separada de la carga completa.
8. Presenta el árbol y el diff para revisión antes de escribir archivos.

## Salidas esperadas

- Archivo `.jmx`.
- Plantilla de datos sintéticos.
- Archivo de propiedades sin secretos.
- README con prerrequisitos, variables y comandos propuestos.
- Matriz de transacciones y assertions.
- Checklist de autorización y parada.
- Lista de supuestos y limitaciones.

## Límites de seguridad

- Nunca ejecutes JMeter como parte de este Skill.
- Nunca apuntes a producción ni a un destino cuya clasificación sea incierta.
- Nunca incrustes tokens, contraseñas, cookies o datos reales.
- Nunca reduzcas umbrales para conseguir un resultado aprobado.
- Nunca asumas que un namespace aísla capacidad compartida.
- La ejecución requiere una acción humana explícita y separada.
