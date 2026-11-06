---
name: test-plan-traceability
description: Transcribe, revisa y relaciona una Historia de Usuario con su plan de pruebas sin completar contenido ausente ni elegir herramientas automáticamente. Úsalo antes de implementar automatización o evaluar cobertura.
---

# Preparar trazabilidad entre Historia de Usuario y plan de pruebas

## Propósito

Convertir fuentes entregadas por el equipo en una transcripción aprobada y una matriz auditable entre criterios de aceptación y casos de prueba. Este procedimiento conserva el contenido original, hace visibles las brechas y separa trazabilidad de selección de herramientas.

## Cuándo usarla

Úsala cuando una Historia de Usuario y su plan deban compararse antes de desarrollo, automatización, handoff o revisión de cobertura. También aplica cuando las fuentes llegan como PDF o imagen y necesitan transcripción controlada.

No la uses para diseñar casos nuevos, cambiar criterios, recomendar un framework sin solicitud explícita ni producir evidencia de ejecución.

## Políticas relacionadas

Aplica `steering/core/dev-qa-workflow.md`, `steering/core/engineering-quality.md` y `steering/qa/test-automation-standards.md`. Este documento describe el procedimiento puntual y no repite sus reglas generales.

## Entradas obligatorias

Proporciona rutas legibles o contenido adjunto para:

- `qa-input/<HU>/user-story.md`, `.pdf`, `.png` o `.jpg`: Historia de Usuario y criterios.
- `qa-input/<HU>/test-plan.md`, `.pdf`, `.png` o `.jpg`: plan, casos y resultados esperados.
- Identificador esperado de la Historia de Usuario, por ejemplo `HU-DEMO-001`.
- Estado y responsable de aprobación de cada fuente.
- Ruta de salida solicitada; por defecto `qa-artifacts/<HU>/traceability/`.

Para PDF o imagen, indica páginas y orden. No uses una captura parcial como si fuera el documento completo.

## Precondiciones y bloqueos

Antes de construir la matriz:

- Confirma que la Historia de Usuario y el plan pertenecen al mismo alcance y versión.
- Verifica que las páginas o archivos esperados estén presentes y sean legibles.
- Identifica criterios y casos sin ID, pero no les asignes uno nuevo.
- Separa transcripción de interpretación.
- La transcripción MUST recibir aprobación explícita antes de crear la matriz, porque una lectura incorrecta cambiaría la trazabilidad.

Si hay texto ilegible, páginas ausentes, fuentes contradictorias o una transcripción aún no aprobada, detén la matriz y publica las brechas. Usa `[ilegible: <ubicación>]`, `sin evidencia` o `no definido`; no completes huecos con conocimiento del producto.

## Procedimiento

1. Inventaría cada fuente con ruta, formato, versión, páginas y procedencia.
2. Transcribe el contenido relevante de la Historia de Usuario y del plan por separado. Conserva identificadores, redacción, tablas, pasos y resultados esperados.
3. Marca texto ilegible y referencias rotas con su ubicación exacta. Registra contradicciones sin resolverlas por cuenta propia.
4. Extrae una lista normalizada de criterios y otra de casos, pero conserva un enlace a la ubicación original de cada elemento.
5. Escribe `source-transcription.md` y `gaps.md`. Presenta ambos para aprobación humana.
6. Espera una confirmación explícita. Registra quién aprobó, cuándo y qué versión revisó.
7. Después de la aprobación, relaciona cada criterio con cero o más casos usando únicamente los IDs y resultados presentes en las fuentes.
8. Incluye también casos sin criterio y criterios sin caso. No elimines filas para aparentar cobertura completa.
9. Registra nivel, propietario y tipo de evidencia solo cuando estén definidos. Escribe `no definido` cuando falten.
10. Genera `traceability-matrix.md` y un resumen de brechas. No conviertas el estado `trazado` en `cubierto` o `aprobado`; esos estados requieren evidencia adicional.
11. Revisa el diff y valida que todos los IDs de la matriz existan en la transcripción aprobada.

## Archivos de salida

```text
qa-artifacts/<HU>/traceability/
├── source-inventory.md
├── source-transcription.md
├── gaps.md
└── traceability-matrix.md     # solo después de aprobar la transcripción
```

Cada archivo debe indicar HU, versión de las fuentes y fecha de preparación. La matriz debe contener como mínimo: criterio, caso, nivel, propietario, resultado esperado, referencia de origen y estado de trazabilidad.

## Ejemplo de prompt

```text
Prepara la trazabilidad de HU-DEMO-001 con qa-input/HU-DEMO-001/user-story.md
y test-plan.md. Primero entrega transcripción y brechas. No generes la matriz hasta que
yo apruebe la transcripción y no selecciones Selenium, Karate ni otra herramienta.
```

## Ejemplo de salida

Después de aprobar la transcripción:

```markdown
| Criterio | Caso   | Nivel definido | Propietario | Resultado esperado                | Fuente                         | Estado  |
|----------|--------|----------------|-------------|-----------------------------------|--------------------------------|---------|
| CA-06    | CP-004 | E2E web        | QA          | Se muestra “Credenciales inválidas” | plan.md, CP-004; HU.md, CA-06 | trazado |
```

La fila demuestra la relación `CA-06 → CP-004`. No demuestra que `CP-004` esté automatizado, ejecutado o aprobado.

## Lo que esta Skill no hace

- No genera pruebas Selenium, Karate ni proyectos JMeter.
- No ejecuta pruebas, aplicaciones, despliegues ni carga.
- No certifica una Historia de Usuario ni declara cobertura a partir de una relación documental.
- No selecciona automáticamente una herramienta de automatización.
- No corrige criterios, inventa casos ni completa texto ausente.

Una fase de recomendación de herramienta puede añadirse únicamente mediante una solicitud separada y una revisión humana. Esa fase debe comparar alternativas, registrar supuestos y mantener la recomendación fuera de la matriz aprobada hasta que el equipo decida.

## Validación

Ejecuta comprobaciones locales y finitas sobre los artefactos:

```bash
HU="${HU:?defina HU}"
test -s "qa-artifacts/$HU/traceability/source-inventory.md"
test -s "qa-artifacts/$HU/traceability/source-transcription.md"
test -s "qa-artifacts/$HU/traceability/gaps.md"
git diff --check -- "qa-artifacts/$HU/traceability"
```

Genera y valida `traceability-matrix.md` solo después de registrar la aprobación de la transcripción. Además, revisa manualmente que cada ID de la matriz aparezca en `source-transcription.md`.

## Manejo de fallos

- **PDF o imagen ilegible:** registra página y zona; solicita una fuente legible.
- **Página o anexo ausente:** marca la fuente incompleta y no produzcas la matriz.
- **ID duplicado o contradictorio:** conserva ambas referencias y solicita corrección al owner.
- **Criterio o caso sin ID:** usa `no definido`; no asignes identificadores nuevos.
- **Aprobación ambigua:** solicita una confirmación que identifique versión y aprobador.
- **Relación no sustentada:** deja el elemento sin relación y explica qué evidencia falta.

## Límites y responsabilidades

- El owner del producto conserva la redacción y aprobación de criterios.
- QA conserva el plan, los casos y la decisión sobre cobertura y herramientas.
- Quien prepara la matriz conserva fidelidad documental y no cambia las fuentes.
- No almacenes secretos, datos reales ni URLs sensibles en transcripciones o matrices.
- La trazabilidad ayuda a revisar alcance; no reemplaza ejecución, evidencia ni certificación.
