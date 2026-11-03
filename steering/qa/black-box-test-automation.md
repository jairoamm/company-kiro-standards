---
inclusion: always
---

# Automatización QA de caja negra

- Trata la aplicación como una entrega desplegada. QA no accede, clona, construye ni inicia el repositorio de Desarrollo.
- Usa como entradas la Historia de Usuario, el plan QA aprobado, la URL autorizada, el build, el commit de aplicación, los datos de prueba y `ui-selectors.json`.
- Confirma antes de ejecutar que la URL corresponde al ambiente autorizado y registra URL, build, commit, versión del contrato y hora con la evidencia.
- Localiza controles por rol o nombre accesible cuando el plan lo permita; para estados ambiguos o dinámicos, usa únicamente selectores estables publicados en el contrato.
- Si un selector falta, cambió o contradice el comportamiento visible, registra una brecha del handoff. No inspecciones el código de Desarrollo para reconstruirlo.
- Mantén las pruebas independientes, con esperas explícitas y artefactos atribuibles a cada caso.
- El código generado o una suite compilada no certifican la Historia de Usuario. QA conserva la ejecución independiente, la clasificación de fallos y la decisión de certificación.
