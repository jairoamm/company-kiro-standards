---
inclusion: manual
name: dev-bug-resolution
description: Activa el modo Desarrollo para corregir un bug después de recibir el diagnóstico y el handoff de QA.
---

# Perfil Development: resolución de bugs

## Alcance

- Activa este Steering solo cuando estés actuando como Development y debas corregir un bug entregado por QA.
- Usa como entradas `bug-diagnosis.md` o `dev-intake.md`, la evidencia y el commit y build afectados. Trata cualquier borrador de QA rotulado `DRAFT — no aprobado` como una entrada, no como la Spec oficial.
- Verifica las conclusiones del diagnóstico contra el repositorio antes de modificar código.

## Corrección

- Crea, revisa y versiona la Bugfix Spec oficial en `.kiro/specs/<bug>/{bugfix,design,tasks}.md`. Conserva separados el síntoma, la causa confirmada, el comportamiento esperado y el alcance de la corrección.
- Reproduce el defecto y agrega una prueba de regresión en el nivel más bajo que lo demuestre.
- Ejecuta la prueba antes de cambiar código productivo y conserva la evidencia de la prueba roja por la causa esperada.
- Implementa el cambio mínimo que corrige la causa. No amplíes el alcance ni incluyas refactors no solicitados.
- Ejecuta la prueba focalizada y los gates existentes del proyecto, incluidos regresión relacionada, lint, análisis estático y build cuando estén disponibles.
- No debilites assertions, no elimines pruebas y no cambies el comportamiento esperado solo para obtener un resultado verde.
- Reconcilia las Specs afectadas con el comportamiento final. No reescribas requisitos para convertir el defecto anterior en comportamiento válido.
- Documenta en el handoff hacia QA la causa, el cambio, la evidencia roja y verde, los gates, el commit, el build y cualquier limitación pendiente.

## Límite de acceso

Este Steering guía el comportamiento de Kiro; no concede permisos ni sustituye controles de acceso. El repositorio debe aplicar permisos, protección de ramas, revisión por pull request y ownership con los mecanismos aprobados por la organización.
