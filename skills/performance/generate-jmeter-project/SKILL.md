---
name: generate-jmeter-project
description: Genera un proyecto JMeter parametrizado desde un plan aprobado, con assertions y evidencia definidas, sin ejecutar carga. Úsalo solo para un destino no productivo autorizado.
---

# Generar proyecto JMeter

## Propósito

Crear un proyecto JMeter reproducible desde decisiones aprobadas. La Skill escribe JMX, propiedades de ejemplo, datos sintéticos y documentación; no envía tráfico ni concede autorización.

## Cuándo usarla

Úsala después de aprobar operaciones, carga, umbrales, observabilidad y parada. No la uses para decidir valores, apuntar a producción, analizar resultados ni probar un host no clasificado.

## Políticas relacionadas

Aplica `steering/qa/test-automation-standards.md`, `steering/core/security.md` y `steering/core/engineering-quality.md`. El plan proviene de `create-performance-plan`.

## Recursos incluidos

- [JMX completo y sintético](examples/test-plan.jmx)
- [Propiedades del ejemplo](examples/example.properties)
- [Plantilla JMX parametrizada](templates/test-plan.jmx)
- [Plantilla de propiedades sin valores operativos](templates/example.properties)

Ningún recurso se ejecuta durante la generación.

## Entradas obligatorias

- `performance/<HU>/plan/performance-plan.md` y `load-model.csv`, aprobados.
- Especificación versionada de endpoints, cuerpos, headers funcionales y correlaciones.
- `performance-input/<HU>/deployment-context.json`, con destino no productivo, build, commit y autorización.
- Datos sintéticos, umbrales por transacción y mecanismo de autenticación aprobado.
- Versión de JMeter, convenciones del repositorio, owner de ejecución y condiciones de parada.

No aceptes “carga normal”, “rápido” o “muchos usuarios”; exige valores y fuentes.

## Precondiciones y bloqueos

El plan no puede tener decisiones pendientes. El destino MUST ser no productivo y la autorización debe limitar alcance, tasa y duración, porque el JMX prepara tráfico potencialmente dañino. Confirma presupuesto agregado, contrato, autenticación y señales de parada.

Si falla una condición, entrega pendientes y no generes defaults operativos.

## Procedimiento

1. Lee plan, carga, API, contexto y datos; registra versiones y aprobaciones.
2. Comprueba coherencia de tasa o concurrencia, ramp-up, duración y volumen.
3. Mapea `escenario → Thread Group → transacción → sampler → assertion → criterio`.
4. Usa propiedades obligatorias para destino, carga, tiempos y datos; no incluyas defaults peligrosos.
5. Genera JMX sin secretos ni hosts reales y parametriza fixtures.
6. Añade timeouts y assertions aprobadas; no cambies umbrales.
7. Excluye listeners de interfaz y resultados detallados del plan de carga.
8. Documenta inyección segura de autenticación sin persistirla.
9. Añade checklist de build, commit, destino, autorización, observabilidad, presupuesto y parada.
10. Documenta el comando futuro como `NO EJECUTAR DURANTE LA GENERACIÓN`.
11. Valida únicamente XML, revisa diff y entrega la matriz de trazabilidad.

## Archivos de salida

```text
performance/<HU>/jmeter/
├── test-plan.jmx
├── README.md
├── assertions.md
├── execution-checklist.md
├── config/example.properties
└── data/users.example.csv
```

Una ejecución futura escribe JTL, log, HTML y metadata bajo `performance/<HU>/results/<RUN_ID>/`.

## Ejemplo de prompt

```text
Genera el proyecto JMeter de HU-DEMO-001 desde el plan, modelo de carga, API y contexto.
Usa propiedades obligatorias, muestra el diff y valida solo XML. No inventes carga,
umbrales o autenticación y no ejecutes JMeter.
```

## Ejemplo de salida

```xml
<ThreadGroup testname="PERF-01 consulta">
  <stringProp name="ThreadGroup.num_threads">${__P(users)}</stringProp>
  <stringProp name="ThreadGroup.duration">${__P(duration_seconds)}</stringProp>
</ThreadGroup>
```

El [JMX completo](examples/test-plan.jmx) no contiene destino real ni credenciales.

## Validación

Valida estructura sin iniciar JMeter ni realizar conexiones:

```bash
HU="${HU:?defina HU}"
python3 -c 'import sys,xml.etree.ElementTree as ET; ET.parse(sys.argv[1])' \
  "performance/$HU/jmeter/test-plan.jmx"
test -s "performance/$HU/jmeter/execution-checklist.md"
git diff --check -- "performance/$HU/jmeter"
```

El README puede documentar un comando futuro, marcado `NO EJECUTAR DURANTE LA GENERACIÓN`, pero esta Skill nunca lo invoca.

## Manejo de fallos

- **Plan pendiente:** devuelve campos y owners; no sustituyas valores.
- **Destino productivo o incierto:** detente y solicita uno no productivo autorizado.
- **Modelo incoherente:** muestra el cálculo contradictorio.
- **Autenticación ausente:** no inventes headers ni tokens.
- **XML inválido:** corrige solo estructura y repite validación estática.
- **Assertion sin criterio:** solicita requisito o retírala del borrador.
- **Riesgo de evidencia sensible:** ajusta sanitización antes de entregar.

## Límites y responsabilidades

- QA y ambiente autorizan por separado cualquier ejecución.
- El owner del plan aprueba carga, umbrales y parada.
- No ejecutes JMeter, accedas al destino ni analices resultados.
- No apuntes a producción ni a un ambiente incierto.
- No almacenes secretos, tokens, cookies, credenciales, hosts sensibles ni datos reales.
- No asumas que un namespace aísla capacidad compartida.
- Un JMX válido es un artefacto preparado; no certifica performance.
