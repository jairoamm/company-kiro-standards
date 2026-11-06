---
name: generate-selenium-tests
description: Genera pruebas web de caja negra con Java 21, JUnit 5 y Selenium desde un plan QA aprobado y un handoff verificable. Úsalo en el repositorio de QA para crear código, compilarlo y dejar la ejecución remota bajo autorización explícita.
---

# Generar pruebas Selenium de caja negra

## Propósito

Convertir casos web aprobados en pruebas Selenium revisables y trazables, sin inspeccionar el código de Desarrollo ni modificar la aplicación desplegada. El procedimiento genera código y evidencia preparada; una ejecución remota autorizada y la decisión de QA son pasos separados.

## Cuándo usarla

Úsala cuando QA haya seleccionado recorridos web que justifican automatización end-to-end y exista un handoff completo para el mismo build. No la uses para pruebas unitarias, de API, de carga ni para descubrir selectores desde el DOM o el repositorio de Desarrollo.

## Políticas relacionadas

Aplica `steering/qa/test-automation-standards.md`, `steering/qa/black-box-test-automation.md` y `steering/core/security.md`. Esos Steering definen las reglas permanentes; este documento se concentra en el procedimiento de generación Selenium.

## Entradas obligatorias

Recibe las rutas equivalentes del repositorio QA. Si no hay una convención previa, usa:

- `qa-input/<HU>/user-story.md`: Historia de Usuario y criterios de aceptación en Markdown.
- `qa-input/<HU>/test-plan.md`: plan QA aprobado, con identificadores de caso, pasos y resultados esperados.
- `qa-input/<HU>/ui-selectors.json`: contrato versionado entregado por Desarrollo.
- `qa-input/<HU>/deployment-context.json`: JSON con `environment`, `baseUrl`, `buildId`, `applicationCommit` y estado de autorización.
- `qa-input/<HU>/test-data/`: datos sintéticos en JSON o CSV y reglas de preparación o limpieza.
- Archivo de build del repositorio, por ejemplo `build.gradle` o `build.gradle.kts`, con Java 21, JUnit 5 y Selenium disponibles.
- Lista explícita de casos que se generarán, por ejemplo `CP-004`.

La URL efectiva se inyecta mediante `BASE_URL`; no se copia al código fuente. Los valores de build y commit deben corresponder a esa URL.

## Precondiciones y bloqueos

Antes de escribir código, confirma:

- La Historia de Usuario y el plan tienen aprobación identificable.
- Cada caso solicitado tiene precondiciones, datos, pasos y resultado esperado.
- `ui-selectors.json` es válido y su `contractVersion` corresponde al handoff.
- `deployment-context.json` vincula URL, ambiente, build y commit. No deduzcas ninguno de esos datos.
- La ejecución remota MUST permanecer bloqueada hasta que QA autorice el destino, porque compilar localmente no concede acceso a otro sistema.
- El repositorio QA documenta un comando de Gradle finito, sin modo watch.

Si falta una entrada, si dos archivos señalan builds distintos o si un selector necesario no está publicado, detente y entrega la lista de bloqueos. No inspecciones el repositorio de Desarrollo para completar la información.

## Procedimiento

1. Lee la Historia de Usuario, el plan, el contrato de selectores, el contexto de despliegue y los datos. Registra los identificadores y versiones usados.
2. Construye una tabla temporal `caso → paso → selector → dato → assertion`. Marca como brecha cualquier paso sin selector o resultado observable.
3. Revisa las convenciones existentes de paquetes, fixtures, lifecycle de WebDriver y tareas Gradle. No agregues un framework paralelo.
4. Propón el árbol de archivos. Crea las clases de prueba bajo `src/test/java/demo/e2e/`. Añade clases de soporte o Page Objects únicamente cuando el repositorio ya use ese patrón o cuando varios casos compartan comportamiento estable.
5. Implementa Java 21 y JUnit 5. Obtén la URL de `BASE_URL` y falla con un mensaje claro si no está definida.
6. Convierte cada estrategia del contrato de forma literal: `id` a `By.id`, `data-testid` a `By.cssSelector("[data-testid='…']")` y `role` a un selector de rol combinado con la verificación del nombre accesible cuando el contrato lo incluya. No inventes selectores.
7. Usa `WebDriverWait` con condiciones explícitas para presencia, visibilidad o interacción. No uses `Thread.sleep`, XPath estructural, índices del DOM ni clases CSS internas.
8. Mantén cada caso independiente. Carga datos sintéticos desde la entrada y aplica la limpieza aprobada; no compartas estado mutable entre tests.
9. Añade captura de pantalla en los checkpoints indicados por el plan y en el manejador de fallo. Registra JUnit XML y metadata con HU, casos, ambiente, build, commit, `contractVersion`, navegador y hora.
10. Revisa el diff completo y ejecuta solo la compilación local con `./gradlew testClasses`. Corrige errores de compilación sin debilitar assertions.
11. Presenta el diff, la matriz de cobertura y el resultado de compilación. Espera autorización explícita de QA antes de invocar `e2eTest` contra `BASE_URL`.

## Archivos de salida

Salvo que el repositorio ya defina otras rutas, genera:

```text
src/test/java/demo/e2e/
├── Cp004CredencialesInvalidasTest.java
└── support/                         # solo si aplica
src/test/resources/demo/e2e/<HU>/
└── cp-004.json
build/evidence/e2e/<HU>/<CASO>/
└── <checkpoint>.png
build/evidence/e2e/run-metadata.json
build/test-results/e2eTest/           # JUnit XML
build/reports/tests/e2eTest/          # reporte Gradle
```

El código fuente y los fixtures se versionan. `build/` es evidencia generada y se conserva según la política del repositorio, no necesariamente en Git.

## Ejemplo de prompt

```text
Genera Selenium para CP-004 de HU-DEMO-001. Usa qa-input/HU-DEMO-001/test-plan.md,
ui-selectors.json, deployment-context.json y test-data/cp-004.json. Crea Java 21/JUnit 5
en src/test/java/demo/e2e, muestra el diff y compila. No ejecutes e2eTest hasta que QA
autorice el destino indicado por BASE_URL.
```

## Ejemplo de salida

Fragmento reducido para `CP-004`; los nombres provienen del contrato y los datos del fixture:

```java
private final By email = By.id("login-email");
private final By submit = By.cssSelector("[data-testid='login-submit']");
private final By alert = By.cssSelector("[role='alert']");

@Test
void shouldShowInvalidCredentialsMessageWhenCp004UsesInvalidUser() {
    driver.get(requireBaseUrl());
    wait.until(ExpectedConditions.visibilityOfElementLocated(email))
        .sendKeys(testData.invalidEmail());
    wait.until(ExpectedConditions.elementToBeClickable(submit)).click();

    WebElement message = wait.until(
        ExpectedConditions.visibilityOfElementLocated(alert));
    assertEquals("Credenciales inválidas", message.getAccessibleName());
}
```

La salida también incluye una fila de trazabilidad como `CP-004 → Cp004CredencialesInvalidasTest → contractVersion 1.2.0`.

## Validación

Ejecuta primero validaciones locales y finitas:

```bash
HU="${HU:?defina HU}"
python3 -m json.tool "qa-input/$HU/ui-selectors.json" >/dev/null
python3 -m json.tool "qa-input/$HU/deployment-context.json" >/dev/null
./gradlew testClasses
git diff --check -- src/test/java/demo/e2e src/test/resources/demo/e2e
```

Después de mostrar el diff y recibir autorización explícita para el destino remoto, QA puede ejecutar de forma separada:

```bash
BASE_URL="${BASE_URL:?defina BASE_URL con la URL autorizada}" \
  ./gradlew e2eTest --tests "demo.e2e.Cp004CredencialesInvalidasTest"
```

No escribas el valor de `BASE_URL` en documentación ni commits. La persona responsable lo obtiene del handoff o del pipeline aprobado.

## Manejo de fallos

- **Entrada ilegible o incompleta:** no generes el caso afectado; lista archivo, campo e impacto.
- **Selector ausente o incompatible:** registra una brecha del handoff y solicita una nueva versión de `ui-selectors.json`.
- **Build o commit no coincide con la URL:** bloquea la ejecución remota y solicita un contexto de despliegue corregido.
- **Compilación fallida:** corrige solo el código generado o reporta la dependencia faltante; no cambies el producto ni los criterios.
- **Fallo durante una ejecución autorizada:** conserva screenshot, JUnit XML y metadata; clasifica por separado posible producto, prueba o ambiente.
- **Autorización ausente:** termina después de la compilación y deja el comando remoto sin ejecutar.

## Límites y responsabilidades

- QA es propietario de la suite, de la ejecución remota, de la clasificación de fallos y de la certificación.
- Desarrollo entrega la aplicación, el contrato de selectores y los datos de despliegue; no genera esta suite como parte del handoff.
- No clones, construyas ni inicies el repositorio de Desarrollo.
- No despliegues, cambies ambientes ni amplíes acceso de red.
- No almacenes secretos, cookies de sesión, tokens, datos reales ni URLs sensibles en código, fixtures, screenshots o metadata.
- El código compilado no demuestra que el comportamiento remoto funcione y no certifica la Historia de Usuario.
