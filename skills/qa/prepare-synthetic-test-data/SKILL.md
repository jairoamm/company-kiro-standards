---
name: prepare-synthetic-test-data
description: Guía a QA para preparar y revisar un borrador de test-data.json con datos exclusivamente sintéticos y trazables antes de generar automatización.
---

# Preparar datos sintéticos para automatización QA

## Propósito

Guiar a Kiro, cuando QA lo solicite, para proponer un borrador trazable de datos sintéticos. QA es dueño del archivo, revisa cada valor, lo aprueba y mantiene sus cambios. El archivo aprobado se prepara antes de Selenium, Karate o JMeter.

## Cuándo usarla

Úsala después de revisar la HU y el plan, o para actualizar un borrador cuando cambian casos o límites. No la uses para obtener datos de ambientes, transformar datos de clientes, provisionar backend ni ejecutar automatización.

## Políticas relacionadas

Aplica `steering/core/security.md`, `steering/qa/test-automation-standards.md` y, para caja negra, `steering/qa/black-box-test-automation.md`.

## Recursos incluidos

- [Ejemplo completo de `test-data.json`](examples/test-data.json)
- [Schema del contrato](schemas/test-data.schema.json)
- [Validador estático sin dependencias externas](scripts/validate_test_data.py)

## Entradas obligatorias

- `qa-input/<HU>/user-story.md` y `qa-input/<HU>/test-plan.md`, revisados y de la misma HU.
- Esquemas o limitaciones versionadas que definan formato, longitud y valores permitidos.
- Casos que usarán cada dato y su categoría: válido, inválido o límite.
- Convención existente de `test-data.json`, si la hay.

Un esquema o límite es obligatorio cuando un caso depende de él. Su ausencia bloquea el dato; Kiro no puede inventar reglas funcionales.

## Precondiciones y bloqueos

Confirma que cada dato corresponde a un paso aprobado, que sus restricciones citan una fuente y que puede crearse desde cero. Los valores no pueden derivar de personas, cuentas, pedidos o eventos reales.

Detente ante fuentes contradictorias, límites ausentes, una muestra real como única entrada o un estado de backend no provisionado. Informa archivo, campo, caso y owner responsable.

## Procedimiento

1. Lee HU, plan y restricciones; registra la fuente de cada formato y límite.
2. Construye `caso → dato → categoría → restricción → resultado esperado`.
3. Separa entradas de estados persistidos. Kiro MUST NOT inventar estados de backend.
4. Registra cualquier seed requerido para Dev o plataforma y deja bloqueado el caso hasta recibir evidencia verificable.
5. Crea valores desde cero; usa identidades ficticias y dominios `.test` para correos.
6. Incluye valores válidos, inválidos o de límite solo cuando el plan los exija.
7. Conserva el esquema existente o usa el [schema incluido](schemas/test-data.schema.json) como contrato inicial aprobado por QA.
8. Escribe únicamente `qa-input/<HU>/test-data.json` y no dupliques datos en código o logs.
9. Ejecuta el validador estático y muestra diff y trazabilidad. No ejecutes pruebas.
10. Solicita revisión humana obligatoria; Kiro propone un borrador, pero QA decide su aprobación.

## Archivos de salida

```text
qa-input/<HU>/test-data.json
```

La conversación puede incluir trazabilidad y bloqueos; no crea otro catálogo ni archivos de seed.

## Ejemplo de prompt

```text
Usa prepare-synthetic-test-data para proponer qa-input/HU-DEMO-001/test-data.json
desde la HU, el plan y sus límites. Usa solo datos ficticios, muestra trazabilidad y diff,
y no inventes estados de backend ni ejecutes pruebas.
```

## Ejemplo de salida

```json
{
  "schemaVersion": "1.0",
  "story": "HU-DEMO-001",
  "classification": "synthetic",
  "cases": ["CP-004"],
  "records": []
}
```

El [ejemplo completo](examples/test-data.json) añade registros y fuentes sin afirmar que exista una cuenta remota.

## Revisión humana obligatoria

QA comprueba relación con casos, fuentes de límites, origen ficticio, dominios `.test`, requisitos de seed y alcance del diff. Una validación verde o el silencio no equivalen a aprobación.

## Lo que esta Skill no hace

- No obtiene, copia, enmascara ni anonimiza datos reales. Kiro no copia ni anonimiza datos reales.
- No inventa estados de backend, formatos, límites, cuentas ni permisos.
- No crea ni ejecuta seeds; registra la necesidad para Dev o plataforma.
- No genera Selenium, Karate o JMeter.
- No ejecuta pruebas ni accede a ambientes.
- No certifica una HU ni reemplaza la revisión humana obligatoria.

## Validación

Define `SKILL_DIR` como el directorio de esta Skill y ejecuta solo comprobaciones estáticas:

```bash
HU="${HU:?defina HU}"
SKILL_DIR="${SKILL_DIR:?defina la ruta de prepare-synthetic-test-data}"
DATA_FILE="qa-input/$HU/test-data.json"
python3 "$SKILL_DIR/scripts/validate_test_data.py" "$DATA_FILE" \
  --schema "$SKILL_DIR/schemas/test-data.schema.json"
git diff --check -- "$DATA_FILE"
```

La validación comprueba el contrato declarado. No demuestra estado remoto ni aprueba los datos.

## Manejo de fallos

- **HU o plan ausente:** no propongas el archivo.
- **Fuentes contradictorias:** lista reglas, fuentes y casos; QA decide la corrección.
- **Límite ausente:** bloquea solo los datos afectados; no asignes un valor predeterminado.
- **Muestra real:** recházala y solicita reglas o schema; no la copies ni anonimices.
- **Estado de backend:** registra seed o provisión para Dev o plataforma.
- **JSON inválido:** corrige estructura sin alterar reglas y repite una vez la validación.
- **Revisión pendiente:** conserva el estado de borrador y no lo entregues a Skills de generación.

## Límites y responsabilidades

- QA es dueño del archivo, su revisión, aprobación y mantenimiento.
- Kiro propone un borrador trazable y aplica correcciones solicitadas.
- Dev o plataforma aporta provisión verificable cuando se requiere estado persistido.
- No almacenes secretos, tokens, cookies, credenciales ni datos reales.
- Un JSON válido es un insumo preparado; no ejecuta automatización ni certifica resultados.
