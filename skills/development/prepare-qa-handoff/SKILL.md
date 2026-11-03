---
name: prepare-qa-handoff
description: Prepara y valida el handoff de una interfaz desde Desarrollo hacia QA, incluido el contrato versionado de selectores. Úsalo al cerrar una Historia de Usuario o antes de entregar un build a Testing.
---

# Preparar handoff para QA

## Propósito

Producir un handoff verificable desde el repositorio de Desarrollo sin asumir tareas de automatización ni certificación de QA.

## Entradas obligatorias

- Historia de Usuario y criterios implementados.
- Plan QA aprobado y casos relacionados.
- Frontend correspondiente al commit que se entregará.
- Identificador de build y URL autorizada, si ya existen.
- Datos sintéticos, resultados de gates y limitaciones conocidas.

## Procedimiento

1. Revisa la Historia de Usuario y el plan antes de inspeccionar la interfaz.
2. Inventaría los controles y estados observables que QA necesita. Prefiere semántica accesible y usa selectores dedicados solo cuando haga falta estabilidad adicional.
3. Crea o actualiza `qa-handoff/<HU>/ui-selectors.json` con `schemaVersion`, `contractVersion`, `historia` y `selectors`. Cada entrada debe incluir `nombre`, `pantalla`, `estado`, `estrategia`, `valor` y `casosRelacionados`.
4. Explica selectores reutilizados en estados mutuamente excluyentes y cualquier condición para que aparezcan.
5. Compara el contrato anterior. Si se retira, renombra o cambia el significado de un selector, incrementa la versión mayor y registra la migración.
6. Valida estáticamente que todos los selectores declarados existen en el frontend del commit entregado.
7. Genera un README de handoff con URL, build, commit, datos sintéticos, criterios, gates, versión del contrato y limitaciones. Marca como pendiente cualquier dato de despliegue ausente; no lo inventes.
8. Presenta archivos y resultados de validación para revisión antes de declarar el handoff listo.

## Salidas esperadas

- `qa-handoff/<HU>/ui-selectors.json` válido y versionado.
- README de handoff con procedencia y pendientes visibles.
- Resultado de la comprobación estática de selectores.
- Lista de cambios incompatibles o brechas, si existen.

## Límites

- No despliegues, inicies servicios ni cambies ambientes.
- No generes, ejecutes ni certifiques pruebas Selenium; QA mantiene esa suite.
- No declares certificación funcional a partir de pruebas de Desarrollo.
- No incluyas secretos, datos reales ni una causa técnica de defectos en el contrato de selectores.
