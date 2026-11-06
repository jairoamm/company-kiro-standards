---
name: prepare-synthetic-test-data
description: Guía a QA para preparar y revisar un borrador de test-data.json con datos exclusivamente sintéticos, trazables a una Historia de Usuario y su plan de pruebas, antes de generar automatización.
---

# Preparar datos sintéticos para automatización QA

## Propósito

Guiar a Kiro para que, cuando QA lo solicite, proponga un borrador trazable de datos sintéticos para los casos aprobados. QA es dueño del archivo `test-data.json`: revisa cada valor, solicita correcciones, aprueba el archivo y mantiene sus cambios. El archivo aprobado se prepara antes de generar Selenium, Karate o JMeter.

## Cuándo usarla

Úsala después de que QA haya revisado la Historia de Usuario y el plan de pruebas, y antes de generar scripts que consuman datos. También puede usarse para revisar un `test-data.json` existente cuando cambian casos o límites aprobados.

No la uses para extraer datos de ambientes, transformar datos de clientes, preparar estados de backend ni ejecutar automatización.

## Políticas relacionadas

Aplica `steering/core/security.md` y `steering/qa/test-automation-standards.md`. Cuando los datos alimenten pruebas de caja negra, aplica además `steering/qa/black-box-test-automation.md`. Los Steering fijan las reglas permanentes de seguridad y responsabilidad; esta Skill define el procedimiento puntual de preparación.

## Entradas obligatorias

Recibe estas entradas del mismo repositorio QA:

- `qa-input/<HU>/user-story.md`: Historia de Usuario, criterios y reglas de negocio revisados.
- `qa-input/<HU>/test-plan.md`: casos aprobados, identificadores de datos, resultados esperados y límites.
- Esquemas y limitaciones disponibles para la misma HU, por ejemplo `qa-input/<HU>/api-contract.json`, `qa-input/<HU>/ui-selectors.json`, `qa-input/<HU>/performance-inputs.json` o documentación versionada de formato, longitud y valores permitidos.
- Lista de casos que usarán cada dato y clasificación esperada: válido, inválido o límite.
- Convención existente de `test-data.json`, si el repositorio ya tiene una.

`user-story.md` y `test-plan.md` MUST existir y coincidir en la HU, porque Kiro no puede decidir reglas funcionales. Un esquema o límite es obligatorio cuando un caso depende de él; que no esté disponible es un bloqueo, no permiso para inferirlo.

## Precondiciones y bloqueos

Antes de proponer valores, confirma:

- QA identifica la HU, los casos incluidos y la versión revisada del plan.
- Cada categoría de dato se relaciona con un paso o una precondición del plan.
- Las reglas de formato y límites provienen de una entrada citada.
- Los valores pueden crearse desde cero y no derivan de una persona, cuenta, pedido o evento real.
- El repositorio no requiere secretos, tokens, cookies ni credenciales para representar el caso.

Detente si las fuentes se contradicen, falta un límite necesario, solo existe una muestra real o un caso presupone un estado de backend no provisionado. Presenta el archivo, campo, caso y owner que debe resolver cada bloqueo.

## Procedimiento

1. Lee `qa-input/<HU>/user-story.md`, `qa-input/<HU>/test-plan.md` y los esquemas o limitaciones disponibles. Registra qué fuente define cada formato y límite.
2. Construye una tabla temporal `caso → identificador de dato → categoría → restricción → resultado esperado`. No añadas un dato que no esté relacionado con un caso aprobado.
3. Separa valores de entrada de estados del sistema. Kiro MUST NOT inventar estados de backend porque un texto sintético no crea una cuenta, un permiso ni un registro persistido.
4. Si un caso requiere seed o provisión, registra el requisito y el caso bloqueado para Dev o plataforma. No marques ese estado como disponible en `test-data.json` hasta recibir un mecanismo y una confirmación verificables.
5. Crea valores desde cero. Para correos usa dominios reservados como `.test`; para nombres y usuarios usa identidades claramente ficticias. Kiro no copia ni anonimiza datos reales.
6. Incluye, solo cuando el plan los exija, representantes válidos, inválidos y de límite. Distingue el valor exacto del límite de los valores inmediatamente fuera de él.
7. Conserva el esquema existente del repositorio. Si no existe, propone un objeto JSON pequeño con `schemaVersion`, `story`, `classification` y grupos nombrados por dominio funcional.
8. Escribe únicamente el borrador `qa-input/<HU>/test-data.json`. No agregues datos a código, prompts guardados, logs ni evidencia.
9. Ejecuta solo la validación JSON finita de esta Skill y muestra el diff junto con la matriz de trazabilidad. No ejecutes Selenium, Karate, JMeter ni otro runner.
10. Solicita revisión humana obligatoria de QA. El archivo no queda aprobado para consumo hasta que QA confirme valores, casos, límites, clasificación sintética y requisitos de seed.

## Archivos de salida

La única salida versionada es:

```text
qa-input/<HU>/test-data.json
```

Kiro presenta además, en la conversación, la matriz de trazabilidad, los bloqueos y el diff para revisión. No crea un segundo catálogo de datos ni archivos de seed.

## Ejemplo de prompt

```text
Usa prepare-synthetic-test-data para proponer un borrador de
qa-input/HU-DEMO-001/test-data.json. Lee user-story.md, test-plan.md y las
limitaciones disponibles. Incluye solo los datos de los casos aprobados,
explica válido, inválido y límite, y usa correos .test e identidades ficticias.
No copies ni anonimices datos reales, no inventes estados de backend y no
inicies las pruebas. Muéstrame la trazabilidad y el diff para revisión de QA.
```

## Ejemplo de salida

Fragmento breve basado en `HU-DEMO-001`:

```json
{
  "schemaVersion": "1.0",
  "story": "HU-DEMO-001",
  "classification": "synthetic",
  "email": {
    "valid": "ana.demo@example.test",
    "invalid": "ana.demo"
  },
  "username": {
    "valid": "ana_demo",
    "tooShort": "ad"
  }
}
```

`email.valid` usa el dominio reservado `.test`; `email.invalid` cubre el formato inválido; `username.valid` es ficticio; y `username.tooShort` cubre el valor de dos caracteres inmediatamente por debajo del límite mínimo de tres definido por la HU. El ejemplo no afirma que esos usuarios existan en un backend.

## Revisión humana obligatoria

QA debe comprobar antes de aprobar:

- cada clave se relaciona con un caso e identificador del plan;
- cada formato y límite cita una fuente disponible;
- los valores son ficticios y no se derivaron de datos reales;
- los correos sintéticos usan `.test`;
- ningún valor presupone un estado de backend sin seed confirmado;
- el diff contiene solo `qa-input/<HU>/test-data.json`.

La aprobación debe quedar en el mecanismo de revisión del repositorio. El silencio, una validación JSON verde o la propuesta de Kiro no equivalen a aprobación.

## Validación

Ejecuta validaciones locales, estáticas y finitas; no inician runners ni realizan conexiones:

```bash
HU="${HU:?defina el identificador de la HU}"
DATA_FILE="qa-input/$HU/test-data.json"
test -f "$DATA_FILE"
python3 -m json.tool "$DATA_FILE" >/dev/null
python3 - "$DATA_FILE" "$HU" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
story = sys.argv[2]
data = json.loads(path.read_text(encoding="utf-8"))
if data.get("story") != story:
    raise SystemExit("story no coincide con la ruta solicitada")
if data.get("classification") != "synthetic":
    raise SystemExit("classification debe ser synthetic")

def strings(value):
    if isinstance(value, dict):
        for nested in value.values():
            yield from strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from strings(nested)
    elif isinstance(value, str):
        yield value

for value in strings(data):
    if "@" in value and not value.rsplit("@", 1)[1].endswith(".test"):
        raise SystemExit("todo correo sintético debe usar un dominio .test")
PY
git diff --check -- "$DATA_FILE"
```

La validación comprueba sintaxis y reglas declaradas del archivo. No demuestra que exista un estado remoto ni aprueba los datos en nombre de QA.

## Manejo de fallos

- **HU o plan ausente:** no propongas el archivo; solicita la ruta y versión revisada.
- **Fuentes contradictorias:** lista la regla, las fuentes y los casos afectados; QA decide cuál corregir.
- **Esquema o límite ausente:** bloquea únicamente los datos que dependan de esa definición; no inventes un valor predeterminado.
- **Muestra real como única entrada:** recházala y solicita reglas o un esquema; no la copies, enmascares ni anonimices.
- **Estado de backend requerido:** registra la necesidad de seed o provisión para Dev o plataforma y deja el caso bloqueado.
- **JSON inválido:** corrige la estructura del borrador sin cambiar reglas funcionales y repite una vez la validación estática.
- **Revisión QA pendiente:** conserva el archivo como borrador y no lo presentes a las Skills de generación.

## Lo que esta Skill no hace

- No obtiene, copia, enmascara ni anonimiza datos reales.
- Kiro no inventa estados de backend, formatos, límites, cuentas ni permisos.
- No crea ni ejecuta seeds; registra esa necesidad para Dev o plataforma.
- No genera pruebas Selenium, Karate o JMeter.
- No ejecuta pruebas, no accede a ambientes y no produce evidencia de ejecución.
- No certifica una Historia de Usuario ni reemplaza la aprobación de QA.

## Límites y responsabilidades

- QA es dueño del archivo, de su revisión, de su aprobación y de su mantenimiento.
- Kiro propone un borrador trazable y aplica las correcciones que QA solicite; no asume la responsabilidad ni la aprobación.
- Dev o plataforma proporciona un mecanismo de seed o provisión cuando un caso necesita estado persistido.
- No almacenes secretos, tokens, cookies, credenciales ni datos reales en `test-data.json`, comentarios, commits, logs o evidencia.
- No uses el archivo para afirmar que una cuenta existe o que un ambiente está listo.
- Un JSON válido es un insumo preparado. No ejecuta automatización y no certifica resultados.
