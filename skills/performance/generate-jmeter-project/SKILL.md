---
name: generate-jmeter-project
description: Genera un proyecto JMeter parametrizado desde un plan de performance aprobado, con assertions y evidencia definidas, sin ejecutar carga. Úsalo solo para un destino no productivo autorizado.
---

# Generar proyecto JMeter

## Propósito

Crear un proyecto JMeter reproducible y revisable a partir de decisiones ya aprobadas. El procedimiento escribe JMX, propiedades de ejemplo, datos sintéticos y documentación; no envía tráfico ni convierte la generación en autorización.

## Cuándo usarla

Úsala después de aprobar un plan de performance con operaciones, carga, umbrales, observabilidad y condiciones de parada. No la uses para decidir esos valores, apuntar a producción, analizar resultados existentes ni realizar una prueba rápida contra un host no clasificado.

## Políticas relacionadas

Aplica `steering/qa/test-automation-standards.md`, `steering/core/security.md` y `steering/core/engineering-quality.md`. `skills/performance/create-performance-plan/SKILL.md` produce la entrada principal; este procedimiento no vuelve a diseñar el plan.

## Entradas obligatorias

Proporciona:

- `performance/<HU>/plan/performance-plan.md`: plan aprobado.
- `performance/<HU>/plan/load-model.csv`: tasa o concurrencia, ramp-up, duración, mezcla y volumen aprobados.
- Especificación versionada de endpoints, métodos, headers funcionales, cuerpos y correlaciones.
- `performance-input/<HU>/deployment-context.json`: destino no productivo, build, commit y referencia de autorización.
- `performance/<HU>/plan/data/`: datos sintéticos y estrategia de aislamiento.
- Umbrales aprobados por transacción y percentil.
- Mecanismo de autenticación aprobado, descrito sin material secreto.
- Versión de JMeter soportada y convenciones del repositorio.
- Responsable de una futura ejecución y condiciones de parada.

No aceptes valores como “carga normal”, “rápido” o “muchos usuarios”. Solicita valores y fuentes concretos.

## Precondiciones y bloqueos

Antes de escribir el JMX:

- El plan está aprobado y no contiene decisiones pendientes para los escenarios solicitados.
- El destino MUST estar clasificado como no productivo y la autorización debe identificar alcance, tasa y duración máximos, porque el JMX prepara tráfico potencialmente dañino.
- La carga agregada de equipos concurrentes cabe en el presupuesto acordado.
- La especificación define correlación, requests, respuestas y errores esperados.
- El mecanismo de autenticación existe en el proyecto; no requiere incrustar secretos.
- Las condiciones de parada pueden observarse durante la futura ejecución.

Si una precondición falla, entrega una lista de decisiones pendientes. No generes defaults que puedan producir tráfico accidental.

## Procedimiento

1. Lee el plan, el modelo de carga, la especificación, el contexto de despliegue y los datos. Registra versiones y aprobaciones.
2. Comprueba que concurrencia o tasa, ramp-up, duración y volumen sean coherentes. Reporta contradicciones antes de crear archivos.
3. Mapea escenarios a Thread Groups, transacciones, samplers, correlaciones y assertions. Mantén una fila de trazabilidad por operación.
4. Propón el árbol de archivos y los nombres de propiedades. Usa propiedades obligatorias para protocolo, host, puerto, usuarios o tasa, ramp-up y duración; evita defaults operativos peligrosos.
5. Genera el JMX sin valores secretos ni hosts reales. Parametriza datos y evita cuerpos repetidos cuando un CSV o fixture sea más claro.
6. Añade timeouts explícitos y assertions para status, contrato y criterios acordados. No reduzcas umbrales para lograr verde.
7. Mantén listeners de interfaz y resultados detallados fuera del plan de carga. Configura JTL y dashboard HTML como artefactos de la futura ejecución.
8. Documenta cómo el mecanismo aprobado entregará autenticación en tiempo de ejecución sin persistirla en Git, JMX, propiedades, JTL o comandos compartidos.
9. Añade un checklist previo con build, commit, destino, autorización, observabilidad, presupuesto agregado y condiciones de parada.
10. Documenta el comando propuesto de ejecución con placeholders. Etiquétalo claramente como `NO EJECUTAR DURANTE LA GENERACIÓN`.
11. Valida localmente el XML, revisa el diff y entrega la matriz `escenario → transacción → assertion → criterio`.

## Archivos de salida

```text
performance/<HU>/jmeter/
├── test-plan.jmx
├── README.md
├── assertions.md
├── execution-checklist.md
├── config/
│   └── example.properties
└── data/
    └── users.example.csv
```

Una ejecución futura, separada y autorizada, debe escribir bajo:

```text
performance/<HU>/results/<RUN_ID>/
├── results.jtl
├── jmeter.log
├── html/
└── run-metadata.json
```

No versiones propiedades con secretos ni resultados sin sanitizar.

## Ejemplo de prompt

```text
Genera el proyecto JMeter de HU-DEMO-001 desde performance-plan.md, load-model.csv,
la especificación API y deployment-context.json. Crea test-plan.jmx y archivos auxiliares
bajo performance/HU-DEMO-001/jmeter. Usa propiedades obligatorias, muestra el diff y
valida solo el XML. No inventes carga, umbrales o autenticación y no ejecutes JMeter.
```

## Ejemplo de salida

Fragmento JMX parametrizado, sin defaults de carga ni destino:

```xml
<ThreadGroup testname="PERF-01 consulta">
  <boolProp name="ThreadGroup.scheduler">true</boolProp>
  <stringProp name="ThreadGroup.num_threads">${__P(users)}</stringProp>
  <stringProp name="ThreadGroup.ramp_time">${__P(ramp_up_seconds)}</stringProp>
  <stringProp name="ThreadGroup.duration">${__P(duration_seconds)}</stringProp>
</ThreadGroup>
<HTTPSamplerProxy testname="GET /orders/{id}">
  <stringProp name="HTTPSampler.protocol">${__P(protocol)}</stringProp>
  <stringProp name="HTTPSampler.domain">${__P(host)}</stringProp>
  <stringProp name="HTTPSampler.path">/orders/${order_id}</stringProp>
</HTTPSamplerProxy>
```

`example.properties` enumera las claves sin asignar un host real:

```properties
protocol=<PROTOCOLO_APROBADO>
host=<HOST_NO_PRODUCTIVO_AUTORIZADO>
users=<USUARIOS_APROBADOS>
ramp_up_seconds=<RAMP_UP_APROBADO>
duration_seconds=<DURACION_APROBADA>
```

## Validación

Valida estructura sin iniciar JMeter ni realizar conexiones:

```bash
HU="${HU:?defina HU}"
python3 -c 'import sys,xml.etree.ElementTree as ET; ET.parse(sys.argv[1])' \
  "performance/$HU/jmeter/test-plan.jmx"
test -s "performance/$HU/jmeter/execution-checklist.md"
git diff --check -- "performance/$HU/jmeter"
```

El README puede documentar este comando para una ejecución futura, pero no debe invocarse durante la generación:

```bash
# NO EJECUTAR DURANTE LA GENERACIÓN
HU="${HU:?defina HU}"
RUN_ID="${RUN_ID:?defina RUN_ID}"
JMETER_PROPERTIES="${JMETER_PROPERTIES:?indique propiedades aprobadas sin secretos}"
jmeter -n \
  -t "performance/$HU/jmeter/test-plan.jmx" \
  -q "$JMETER_PROPERTIES" \
  -l "performance/$HU/results/$RUN_ID/results.jtl" \
  -e -o "performance/$HU/results/$RUN_ID/html"
```

Un proceso JMeter puede terminar con código `0` aunque existan samples o assertions fallidas. La revisión posterior MUST inspeccionar `success=false` en el JTL y `errorCount` en el reporte, además del exit code.

## Manejo de fallos

- **Plan con pendientes:** no generes valores sustitutos; devuelve los campos y owners faltantes.
- **Destino productivo o incierto:** detente y solicita un destino no productivo autorizado.
- **Modelo incoherente:** muestra el cálculo que contradice tasa, concurrencia, duración o volumen.
- **Autenticación no definida:** no inventes headers ni tokens; solicita el mecanismo aprobado.
- **XML inválido:** corrige solo la estructura generada y repite la validación estática.
- **Assertion sin criterio:** elimínala del borrador o solicita el requisito; no la presentes como umbral aprobado.
- **Riesgo de registrar datos sensibles:** ajusta nombres y sanitización antes de entregar el proyecto.

## Límites y responsabilidades

- QA y los owners del ambiente autorizan por separado cualquier ejecución.
- El owner del plan aprueba carga, umbrales y condiciones de parada.
- Este procedimiento no ejecuta JMeter, no accede al destino y no analiza resultados.
- No apuntes a producción ni a un ambiente cuya clasificación sea incierta.
- No almacenes secretos, tokens, cookies, credenciales, hosts sensibles ni datos reales.
- No asumas que un namespace aísla capacidad compartida.
- Un JMX válido es un artefacto preparado; no certifica performance ni capacidad.
