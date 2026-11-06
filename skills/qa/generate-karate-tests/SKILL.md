---
name: generate-karate-tests
description: Genera pruebas de API con Karate y JUnit desde una Historia de Usuario, un plan QA y un contrato aprobados. Úsalo sin duplicar la suite versionada ni inventar autenticación.
---

# Generar pruebas de API con Karate

## Propósito

Convertir casos de API aprobados en escenarios Karate trazables. La Skill crea features, fixtures y un runner JUnit; no convierte colecciones automáticamente, no envía solicitudes sin autorización y no certifica la HU.

## Cuándo usarla

Úsala cuando Karate sea la única suite versionada de regresión para los casos indicados. Postman permanece reservado para exploración, reproducción rápida y colecciones compartibles. No uses esta Skill si los mismos escenarios se mantienen como otra regresión sin una decisión explícita de ownership.

## Políticas relacionadas

Aplica `steering/qa/test-automation-standards.md`, `steering/qa/black-box-test-automation.md` cuando exista handoff de caja negra, y `steering/core/security.md`.

## Recursos incluidos

- [Feature completo y sintético](examples/hu-demo-001.feature)
- [Datos del feature](examples/test-data.json)
- [Plantilla reutilizable de feature](templates/api.feature.template)
- [Referencia de configuración y sanitización](references/sanitization-and-configuration.md)

## Entradas obligatorias

- `qa-input/<HU>/user-story.md` y `qa-input/<HU>/test-plan.md`, aprobados.
- `qa-input/<HU>/api-spec/openapi.yaml` o un contrato versionado equivalente.
- `qa-input/<HU>/deployment-context.json`, con ambiente, `BASE_URL`, build, commit y autorización.
- `qa-input/<HU>/test-data/`, con requests y valores sintéticos.
- Build existente con Karate, Java compatible y JUnit 5.
- Decisión que identifica a Karate como única suite de regresión para esos casos.
- Mecanismo de autenticación aprobado, si aplica, sin valores secretos.

## Precondiciones y bloqueos

Confirma que HU, plan y API describen la misma versión; método, path, headers funcionales, request, status y esquema están definidos; no existe regresión duplicada; y build, commit y destino coinciden. La ejecución remota MUST tener autorización explícita.

Si falta el contrato, hay contradicciones o la autenticación no está definida, detente. No inventes headers, tokens, roles, usuarios ni flujos de login.

## Procedimiento

1. Lee entradas y registra sus versiones y casos.
2. Construye `caso → operación → request → status → assertions → criterio`; marca brechas.
3. Reutiliza paquetes, `karate-config.js`, tags y tarea Gradle existentes.
4. Busca escenarios equivalentes; si hay duplicación, solicita decidir qué suite conserva la regresión.
5. Crea un escenario por caso y usa fixtures externos para cuerpos no triviales.
6. Obtén el destino de `BASE_URL`, conserva paths relativos y aplica únicamente la autenticación aprobada.
7. Configura evidencia conforme a la [referencia de sanitización](references/sanitization-and-configuration.md); no registres material sensible.
8. Añade runner JUnit 5, tags de HU/caso y metadata de build, commit y contrato.
9. Revisa el diff y compila con una tarea local finita.
10. Presenta trazabilidad y compilación; espera autorización antes de `karateTest`.

## Archivos de salida

```text
src/test/resources/demo/api/hu-demo-001.feature
src/test/resources/demo/api/data/cp-007-request.json
src/test/java/demo/api/HuDemo001Runner.java
build/karate-reports/
build/test-results/karateTest/
build/evidence/api/run-metadata.json
```

Adapta las rutas solo cuando el repositorio ya tenga una convención equivalente.

## Ejemplo de prompt

```text
Genera Karate para CP-007 y CP-008 de HU-DEMO-001 desde el plan, OpenAPI,
deployment-context.json y datos aprobados. Verifica que no duplique Postman, sanitiza
evidencia, muestra el diff y compila. No ejecutes contra la API sin autorización.
```

## Ejemplo de salida

```gherkin
@CP-007
Scenario: consultar un pedido existente
  Given path 'orders', data.existingOrderId
  When method get
  Then status 200
  And match response contains { id: '#string', status: '#string' }
```

`baseUrl` y los datos provienen de configuración aprobada. Consulta el [feature completo](examples/hu-demo-001.feature).

## Validación

Ejecuta solo validaciones locales y finitas:

```bash
HU="${HU:?defina HU}"
python3 -m json.tool "qa-input/$HU/deployment-context.json" >/dev/null
./gradlew testClasses
git diff --check -- src/test/resources/demo/api src/test/java/demo/api
```

Una ejecución con `BASE_URL` es posterior y exige revisión del diff y autorización explícita.

## Manejo de fallos

- **Contrato incompleto:** lista operación, campo y caso; no deduzcas la API.
- **Suite duplicada:** detén la generación hasta designar una suite versionada.
- **Autenticación ausente:** no envíes solicitudes; pide el mecanismo aprobado.
- **Build, commit o destino inconsistente:** bloquea ejecución remota.
- **Compilación fallida:** corrige solo código generado o reporta dependencias.
- **Evidencia sensible:** detén publicación, sanitiza una copia y reporta la exposición.
- **Assertion fallida en una ejecución posterior:** conserva evidencia; no cambies la expectativa para obtener verde.

## Límites y responsabilidades

- QA decide la suite de regresión, revisa la ejecución y conserva la certificación.
- El owner de API mantiene contrato y autenticación.
- No conviertas ni dupliques colecciones automáticamente.
- No despliegues, modifiques la API ni amplíes permisos de red.
- No almacenes secretos, tokens, cookies, credenciales ni payloads sensibles.
- Compilar valida estructura local; no demuestra comportamiento remoto ni certifica la HU.
