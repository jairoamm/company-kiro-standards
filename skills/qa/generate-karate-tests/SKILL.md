---
name: generate-karate-tests
description: Genera pruebas de API con Karate y un runner JUnit desde una Historia de Usuario, un plan QA y una especificación de servicio aprobados. Úsalo en el repositorio de QA sin duplicar la suite versionada ni inventar autenticación.
---

# Generar pruebas de API con Karate

## Propósito

Convertir casos de API aprobados en escenarios Karate trazables y revisables. El procedimiento crea features, fixtures y un runner JUnit; no convierte automáticamente colecciones Postman, no envía solicitudes remotas sin autorización y no certifica la Historia de Usuario.

## Cuándo usarla

Úsala cuando el equipo haya elegido Karate como única suite versionada de regresión para los casos indicados. Es apropiada para contratos HTTP, validación de respuestas y recorridos de servicio que no requieren interfaz web.

No la uses si los mismos escenarios ya se mantienen como regresión en Postman u otro framework. Postman puede seguir utilizándose para exploración o reproducción, pero debe existir un solo owner de la regresión versionada.

## Políticas relacionadas

Aplica `steering/qa/test-automation-standards.md`, `steering/qa/black-box-test-automation.md` cuando el flujo use un handoff de caja negra, y `steering/core/security.md`. Este documento se limita al procedimiento Karate.

## Entradas obligatorias

Recibe las rutas equivalentes del repositorio QA. Si no existe otra convención, usa:

- `qa-input/<HU>/user-story.md`: Historia de Usuario y criterios aprobados.
- `qa-input/<HU>/test-plan.md`: plan QA aprobado con los casos seleccionados, por ejemplo `CP-007` y `CP-008`.
- `qa-input/<HU>/api-spec/openapi.yaml` o `.json`: OpenAPI 3.x; también se admite un contrato de endpoints versionado en Markdown si el proyecto no usa OpenAPI.
- `qa-input/<HU>/deployment-context.json`: JSON con ambiente, `baseUrl`, build, commit de aplicación y autorización.
- `qa-input/<HU>/test-data/`: requests y valores sintéticos en JSON o CSV.
- Configuración de build existente con Karate, Java compatible y JUnit 5.
- Decisión del equipo que identifica a Karate como suite de regresión para esos casos.
- Mecanismo de autenticación aprobado, si la API lo requiere, descrito sin valores secretos.

## Precondiciones y bloqueos

Confirma antes de generar:

- La Historia de Usuario, el plan y la especificación describen la misma versión del contrato.
- Método, path, headers funcionales, request, códigos de estado y esquema esperado están definidos.
- La decisión que identifica a Karate como única suite versionada MUST estar registrada, porque mantener el mismo caso en dos frameworks divide ownership y evidencia.
- La URL pertenece al build y commit indicados en el handoff.
- Si el endpoint requiere autenticación, el mecanismo aprobado está documentado y disponible mediante el proveedor seguro del proyecto.
- La ejecución remota tiene autorización explícita; compilar localmente no la concede.

Si falta el esquema, hay contradicciones o la autenticación no está definida, detente y reporta el bloqueo. No inventes headers, tokens, roles, usuarios ni flujos de login.

## Procedimiento

1. Lee la Historia de Usuario, el plan, la especificación API, el contexto de despliegue y los datos. Registra sus versiones.
2. Construye la relación `caso → operación → request → status → assertions → criterio` y señala campos no definidos.
3. Inspecciona la convención Karate existente, incluidos paquetes, `karate-config.js`, tags y tarea Gradle. No crees una segunda estructura.
4. Busca escenarios equivalentes en Postman y en la suite versionada. Si los hay, detente y solicita decidir qué suite conserva la regresión.
5. Propón el árbol de archivos. Por defecto, crea features bajo `src/test/resources/demo/api/` y runners bajo `src/test/java/demo/api/`.
6. Obtén `baseUrl` desde configuración parametrizada. Mantén paths relativos en los escenarios y no incrustes hosts.
7. Implementa un escenario por caso trazable. Usa fixtures externos para cuerpos no triviales y assertions específicas del contrato; no snapshots completos que oculten el propósito.
8. Integra únicamente el mecanismo de autenticación aprobado. Lee referencias seguras desde la configuración del proyecto y evita imprimir headers sensibles.
9. Configura sanitización para que requests, responses y reportes redacten tokens, cookies, identificadores sensibles y datos no necesarios.
10. Añade el runner JUnit 5 y tags por HU y caso. Conserva metadata de ambiente, build, commit, versión de contrato y versión de Karate.
11. Muestra el diff y compila con una tarea local finita. Espera autorización antes de ejecutar `karateTest` contra el destino remoto.

## Archivos de salida

```text
src/test/resources/demo/api/
├── hu-demo-001.feature
└── data/
    ├── cp-007-request.json
    └── cp-008-request.json
src/test/java/demo/api/
└── HuDemo001Runner.java
build/karate-reports/                  # reporte sanitizado
build/test-results/karateTest/         # JUnit XML
build/evidence/api/run-metadata.json
```

Adapta las rutas solo cuando el repositorio ya tenga una convención equivalente y documentada.

## Ejemplo de prompt

```text
Genera Karate para CP-007 y CP-008 de HU-DEMO-001 usando el plan, openapi.yaml,
deployment-context.json y los fixtures de qa-input/HU-DEMO-001/test-data. Verifica que no
duplique la suite Postman, crea feature y runner JUnit, sanitiza evidencia, muestra el diff
y compila. No inventes autenticación ni ejecutes contra la API hasta recibir autorización.
```

## Ejemplo de salida

Feature reducido:

```gherkin
@HU-DEMO-001
Feature: Consulta de pedido

  Background:
    * url baseUrl

  @CP-007
  Scenario: consultar un pedido existente
    Given path 'orders', existingOrderId
    When method get
    Then status 200
    And match response contains { id: '#string', status: '#string' }

  @CP-008
  Scenario: rechazar un identificador con formato inválido
    Given path 'orders', invalidOrderId
    When method get
    Then status 400
    And match response.code == 'INVALID_ORDER_ID'
```

Runner corto:

```java
class HuDemo001Runner {
    @Karate.Test
    Karate scenarios() {
        return Karate.run("hu-demo-001").relativeTo(getClass());
    }
}
```

`baseUrl`, `existingOrderId` e `invalidOrderId` provienen de configuración y datos aprobados. El ejemplo no presupone autenticación.

## Validación

Ejecuta validaciones locales y finitas:

```bash
HU="${HU:?defina HU}"
python3 -m json.tool "qa-input/$HU/deployment-context.json" >/dev/null
./gradlew testClasses
git diff --check -- src/test/resources/demo/api src/test/java/demo/api
```

Después de revisar el diff y recibir autorización explícita, QA puede ejecutar por separado:

```bash
BASE_URL="${BASE_URL:?defina BASE_URL con la URL autorizada}" \
  ./gradlew karateTest --tests "demo.api.HuDemo001Runner"
```

Comprueba JUnit XML, reporte Karate sanitizado y metadata. No copies una URL real ni material de autenticación al comando documentado.

## Manejo de fallos

- **Especificación incompleta:** lista operación, campo y caso bloqueado; no deduzcas el contrato.
- **Suite duplicada:** detén la generación hasta que QA designe la única suite versionada.
- **Autenticación ausente o ambigua:** no envíes solicitudes; solicita el mecanismo aprobado.
- **Build o commit inconsistente:** bloquea la ejecución remota y pide un handoff corregido.
- **Compilación fallida:** limita la corrección al código generado o reporta dependencias faltantes.
- **Respuesta con datos sensibles en una ejecución autorizada:** no publiques el artefacto; sanitiza una copia y reporta la exposición por el canal aprobado.
- **Assertion fallida:** conserva evidencia y clasifica producto, prueba o ambiente sin cambiar la expectativa para obtener verde.

## Límites y responsabilidades

- QA decide si Karate es la suite de regresión, revisa la ejecución y conserva la decisión de certificación.
- El owner de la API mantiene la especificación y el mecanismo de autenticación.
- No conviertas ni dupliques automáticamente colecciones Postman.
- No despliegues, modifiques la API ni amplíes permisos o exposición de red.
- No almacenes secretos, tokens, cookies, credenciales ni payloads sensibles en features, fixtures, logs o reportes.
- Una compilación correcta valida estructura local; no demuestra comportamiento remoto ni certifica la Historia de Usuario.
