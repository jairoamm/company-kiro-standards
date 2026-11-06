---
name: generate-selenium-tests
description: Genera pruebas web de caja negra con Java 21, JUnit 5 y Selenium desde un plan QA aprobado y un handoff verificable. Úsalo para crear código y compilarlo; la ejecución remota exige autorización separada.
---

# Generar pruebas Selenium de caja negra

## Propósito

Convertir casos web aprobados en pruebas Selenium trazables sin inspeccionar el repositorio de Desarrollo ni modificar la aplicación. La Skill genera código y evidencia preparada; no ejecuta pruebas remotas ni certifica la Historia de Usuario.

## Cuándo usarla

Úsala cuando QA haya seleccionado recorridos web end-to-end y exista un handoff completo del mismo build. No la uses para pruebas unitarias, de API, de carga ni para descubrir selectores desde el DOM.

## Políticas relacionadas

Aplica `steering/qa/test-automation-standards.md`, `steering/qa/black-box-test-automation.md` y `steering/core/security.md`.

## Recursos incluidos

- [Ejemplo completo Java/JUnit de CP-004](examples/Cp004CredencialesInvalidasTest.java)
- [Contrato sintético usado por el ejemplo](examples/ui-selectors.json)
- [Plantilla reutilizable de test](templates/selenium-test.java.template)
- [Schema de `ui-selectors.json`](schemas/ui-selectors.schema.json)
- [Validador estático de selectores](scripts/validate_ui_selectors.py)

## Entradas obligatorias

- `qa-input/<HU>/user-story.md` y `qa-input/<HU>/test-plan.md`, aprobados.
- `qa-input/<HU>/ui-selectors.json`, entregado por Desarrollo.
- `qa-input/<HU>/deployment-context.json`, con ambiente, `BASE_URL`, build, commit y autorización.
- `qa-input/<HU>/test-data/`, con datos sintéticos y reglas de limpieza.
- Build existente con Java 21, JUnit 5 y Selenium.
- Lista explícita de casos, por ejemplo `CP-004`.

La URL se inyecta mediante `BASE_URL`; nunca se copia al código o a Git.

## Precondiciones y bloqueos

Confirma que HU y plan están aprobados; cada caso tiene pasos y resultado; el contrato de selectores es válido y versionado; y build, commit y destino coinciden. La ejecución remota MUST permanecer bloqueada hasta una autorización explícita de QA, porque compilar no concede acceso al destino.

Si falta una entrada, hay versiones contradictorias o falta un selector, detente y lista archivo, campo, caso e impacto. No inspecciones Desarrollo para completar el handoff.

## Procedimiento

1. Lee todas las entradas y registra HU, casos, build, commit y `contractVersion`.
2. Construye `caso → paso → selector → dato → assertion`; marca cada brecha.
3. Reutiliza paquetes, lifecycle de WebDriver y fixtures existentes; no agregues un framework paralelo.
4. Valida `ui-selectors.json` con el script incluido y convierte literalmente `id`, `data-testid` y `role`; no inventes localizadores.
5. Crea Java 21/JUnit 5 bajo la convención del repositorio. Usa la [plantilla](templates/selenium-test.java.template) solo como esqueleto.
6. Exige `BASE_URL`, usa `WebDriverWait` y evita `Thread.sleep`, XPath estructural, índices y clases internas.
7. Mantén cada caso independiente y carga solo datos sintéticos aprobados.
8. Añade screenshots en checkpoints o fallos y metadata de HU, caso, ambiente, build, commit, contrato y navegador.
9. Revisa el diff y ejecuta únicamente compilación local finita, por ejemplo `./gradlew testClasses`.
10. Presenta diff, trazabilidad y compilación. Espera autorización antes de cualquier `e2eTest`.

## Archivos de salida

```text
src/test/java/demo/e2e/Cp004CredencialesInvalidasTest.java
src/test/resources/demo/e2e/<HU>/cp-004.json
build/evidence/e2e/<HU>/<CASO>/
build/evidence/e2e/run-metadata.json
build/test-results/e2eTest/
```

Versiona código y fixtures. Trata `build/` según la política de evidencia del repositorio.

## Ejemplo de prompt

```text
Genera Selenium para CP-004 de HU-DEMO-001 desde el plan, ui-selectors.json,
deployment-context.json y datos aprobados. Muestra el diff y compila. No ejecutes
e2eTest hasta que QA autorice el destino indicado por BASE_URL.
```

## Ejemplo de salida

```java
private final By submit = By.cssSelector("[data-testid='login-submit']");
wait.until(ExpectedConditions.elementToBeClickable(submit)).click();
assertEquals("Credenciales inválidas", message.getAccessibleName());
```

La salida registra `CP-004 → Cp004CredencialesInvalidasTest → contractVersion 1.2.0`. El [ejemplo completo](examples/Cp004CredencialesInvalidasTest.java) muestra lifecycle, esperas y screenshot de fallo.

## Validación

Define `SKILL_DIR` como el directorio que contiene este `SKILL.md` y ejecuta solo comprobaciones locales:

```bash
HU="${HU:?defina HU}"
SKILL_DIR="${SKILL_DIR:?defina la ruta de generate-selenium-tests}"
python3 "$SKILL_DIR/scripts/validate_ui_selectors.py" \
  "qa-input/$HU/ui-selectors.json" \
  --schema "$SKILL_DIR/schemas/ui-selectors.schema.json"
python3 -m json.tool "qa-input/$HU/deployment-context.json" >/dev/null
./gradlew testClasses
git diff --check -- src/test/java/demo/e2e src/test/resources/demo/e2e
```

Una ejecución contra `BASE_URL` es una acción posterior y autorizada; no forma parte de esta validación.

## Manejo de fallos

- **Entrada incompleta:** no generes el caso afectado; lista campo e impacto.
- **Selector ausente o incompatible:** solicita una nueva versión del contrato.
- **Build, commit o destino inconsistente:** bloquea la ejecución remota.
- **Compilación fallida:** corrige solo el código generado o reporta la dependencia faltante.
- **Fallo en una ejecución autorizada posterior:** conserva evidencia sanitizada y clasifica producto, prueba o ambiente.
- **Autorización ausente:** termina después de compilar.

## Límites y responsabilidades

- QA mantiene suite, ejecución remota, clasificación y certificación.
- Desarrollo entrega aplicación, selectores y contexto de despliegue.
- No clones, construyas ni inicies el repositorio de Desarrollo.
- No despliegues, cambies ambientes ni amplíes acceso de red.
- No almacenes secretos, cookies, tokens, datos reales ni URLs sensibles.
- Una compilación correcta no demuestra comportamiento remoto ni certifica la HU.
