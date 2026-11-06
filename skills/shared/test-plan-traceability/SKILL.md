---
name: test-plan-traceability
description: Transcribe y relaciona una Historia de Usuario con su plan sin completar contenido ausente, elegir herramientas ni ejecutar pruebas. Úsalo antes de evaluar cobertura.
---

# Preparar trazabilidad entre Historia de Usuario y plan

## Propósito

Convertir fuentes entregadas por el equipo en una transcripción aprobada y una matriz auditable. Conserva el texto original, expone brechas y separa trazabilidad de selección de herramientas.

## Cuándo usarla

Úsala antes de desarrollo, automatización, handoff o revisión de cobertura. También aplica a PDF o imagen con transcripción controlada. No la uses para diseñar casos, cambiar criterios, elegir un framework ni producir evidencia de ejecución.

## Políticas relacionadas

Aplica `steering/core/dev-qa-workflow.md`, `steering/core/engineering-quality.md` y `steering/qa/test-automation-standards.md`.

## Recursos incluidos

- [Ejemplo de extracción aprobada con CA-06 y CP-004](examples/source-transcription.md)
- [Ejemplo de matriz CA-06 → CP-004](examples/traceability-matrix.md)
- [Plantilla reutilizable de matriz](templates/traceability-matrix.md)

## Entradas obligatorias

- `qa-input/<HU>/user-story.md`, `.pdf`, `.png` o `.jpg`.
- `qa-input/<HU>/test-plan.md`, `.pdf`, `.png` o `.jpg`.
- Identificador esperado de HU, estado y responsable de aprobación.
- Páginas y orden para fuentes visuales.
- Ruta de salida; por defecto `qa-artifacts/<HU>/traceability/`.

No trates una captura parcial como documento completo.

## Precondiciones y bloqueos

Confirma mismo alcance y versión, archivos completos y legibles e IDs presentes. Separa transcripción de interpretación. La transcripción MUST recibir aprobación explícita antes de crear la matriz, porque un error cambia la trazabilidad.

Ante texto ilegible, páginas ausentes, contradicciones o aprobación pendiente, detente y usa `ilegible`, `sin evidencia` o `no definido`; no completes huecos.

## Procedimiento

1. Inventaría ruta, formato, versión, páginas y procedencia de cada fuente.
2. Transcribe HU y plan por separado, conservando IDs, redacción, pasos y resultados.
3. Marca texto ilegible y contradicciones con ubicación exacta.
4. Extrae listas normalizadas de criterios y casos con referencia al origen.
5. Escribe `source-transcription.md` y `gaps.md`; solicita aprobación humana.
6. Registra quién aprobó, cuándo y qué versión.
7. Solo entonces relaciona cada criterio con cero o más casos usando IDs presentes.
8. Incluye casos sin criterio y criterios sin caso.
9. Usa `no definido` para nivel, owner o evidencia ausentes.
10. Genera matriz y resumen sin convertir `trazado` en `cubierto` o `aprobado`.
11. Revisa que cada ID de la matriz exista en la transcripción aprobada.

## Archivos de salida

```text
qa-artifacts/<HU>/traceability/
├── source-inventory.md
├── source-transcription.md
├── gaps.md
└── traceability-matrix.md
```

La matriz se crea solo después de aprobar la transcripción e incluye criterio, caso, nivel, owner, resultado, fuente y estado.

## Ejemplo de prompt

```text
Prepara la trazabilidad de HU-DEMO-001 desde user-story.md y test-plan.md. Primero
entrega transcripción y brechas. No crees la matriz hasta mi aprobación, no selecciones
Selenium, Karate u otra herramienta y no ejecutes pruebas.
```

## Ejemplo de salida

```markdown
| Criterio | Caso | Nivel | Owner | Estado |
|---|---|---|---|---|
| CA-06 | CP-004 | E2E web | QA | trazado |
```

La relación `CA-06 → CP-004` no demuestra automatización, ejecución, cobertura ni aprobación. Consulta el [ejemplo completo](examples/traceability-matrix.md).

## Lo que esta Skill no hace

- No genera Selenium, Karate ni JMeter.
- No ejecuta pruebas, aplicaciones, despliegues ni carga.
- No certifica una HU ni declara cobertura desde una relación documental.
- No selecciona automáticamente una herramienta.
- No corrige criterios, inventa casos ni completa texto ausente.

Cualquier recomendación de herramienta exige otra solicitud, comparación y revisión humana fuera de la matriz.

## Validación

Ejecuta comprobaciones locales y finitas:

```bash
HU="${HU:?defina HU}"
test -s "qa-artifacts/$HU/traceability/source-inventory.md"
test -s "qa-artifacts/$HU/traceability/source-transcription.md"
test -s "qa-artifacts/$HU/traceability/gaps.md"
git diff --check -- "qa-artifacts/$HU/traceability"
```

Valida la matriz solo después de registrar la aprobación y revisa manualmente que todos sus IDs estén en la transcripción.

## Manejo de fallos

- **Fuente ilegible:** registra página y zona; solicita una copia legible.
- **Página ausente:** marca fuente incompleta y no produzcas matriz.
- **ID duplicado o contradictorio:** conserva referencias y solicita corrección.
- **Elemento sin ID:** usa `no definido`; no asignes uno.
- **Aprobación ambigua:** solicita versión y persona aprobadora.
- **Relación no sustentada:** deja el elemento sin relación y explica la evidencia faltante.

## Límites y responsabilidades

- Producto conserva redacción y aprobación de criterios.
- QA conserva plan, casos y decisión sobre cobertura y herramientas.
- Quien prepara la matriz preserva fidelidad documental.
- No almacenes secretos, datos reales ni URLs sensibles.
- La trazabilidad no reemplaza ejecución, evidencia ni certificación.
