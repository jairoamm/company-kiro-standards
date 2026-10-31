---
inclusion: always
---

# Calidad de ingeniería

- Inspecciona primero la estructura, documentación, comandos y convenciones existentes del repositorio.
- Realiza el cambio mínimo que satisface el requisito. Evita refactors y dependencias no solicitados.
- Mantén responsabilidades claras, nombres descriptivos y manejo explícito de errores.
- Revisa el diff completo antes de declarar terminado un cambio.
- Ejecuta las validaciones relevantes y reporta el comando, resultado y cualquier comprobación no ejecutada.
- No confundas código generado con comportamiento verificado. Una afirmación de calidad requiere una ejecución o evidencia concreta.
- Conserva compatibilidad con los contratos públicos salvo que el cambio aprobado indique lo contrario.
- Cuando una decisión sea ambigua o tenga impacto amplio, presenta opciones y solicita una decisión humana.
- No cambies expectativas, assertions o gates solamente para obtener un resultado verde.
