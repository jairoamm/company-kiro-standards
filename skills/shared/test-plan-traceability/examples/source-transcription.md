# Transcripción sintética aprobada: HU-DEMO-001

## Control

- Historia de Usuario: `HU-DEMO-001`
- Versión de HU: `synthetic-1`
- Versión del plan: `synthetic-1`
- Estado de transcripción: `aprobada para el ejemplo`
- Persona aprobadora: `QA-SYNTHETIC`
- Fecha: `2026-11-05`

## Extracción de la Historia de Usuario

### CA-06

**Ubicación:** `user-story.md`, sección Criterios de aceptación, CA-06.

> Cuando una persona proporciona credenciales inválidas, la interfaz muestra el mensaje “Credenciales inválidas” sin crear una sesión.

## Extracción del plan

### CP-004

**Ubicación:** `test-plan.md`, caso CP-004.

- Precondición: formulario de acceso visible.
- Datos: correo con formato válido en dominio `.test` y valor de credencial sintético no provisionado.
- Pasos: completar ambos campos y enviar.
- Resultado esperado: aparece una alerta accesible con “Credenciales inválidas” y no existe sesión autenticada.
- Nivel declarado por la fuente: E2E web.
- Owner declarado por la fuente: QA.

## Brechas

No hay brechas de lectura en este ejemplo. Esta aprobación es sintética y no sustituye la aprobación de documentos de un proyecto.
