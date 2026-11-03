---
inclusion: always
---

# Testabilidad de interfaces para el handoff a QA

- Antes de implementar o cambiar una interfaz, revisa la Historia de Usuario y el plan QA aprobado. Relaciona cada control y estado observable con sus casos.
- Prefiere roles, nombres y etiquetas accesibles. Cuando no sean suficientes, usa `data-testid` descriptivos y estables; no bases el contrato en clases CSS, posición en el DOM ni XPath estructural.
- Mantén en `qa-handoff/<HU>/ui-selectors.json` un contrato con `contractVersion`, Historia de Usuario y, para cada selector, `nombre`, `pantalla`, `estado`, `estrategia`, `valor` y `casosRelacionados`.
- Valida que cada selector del contrato exista en el frontend y que los estados condicionales estén explicados.
- Las adiciones compatibles conservan la versión mayor. Renombrar, retirar o cambiar el significado de un selector exige incrementar la versión mayor del contrato y comunicar la migración a QA.
- El handoff debe identificar URL autorizada, build, commit, datos sintéticos, criterios implementados, limitaciones conocidas y versión del contrato.
- Desarrollo conserva las pruebas unitarias y de componente que prueban la testabilidad entregada. QA conserva la automatización y la certificación funcional.
- Desarrollo no crea ni certifica suites Selenium como parte del handoff. Entrega el contrato para que QA genere y revise esas pruebas en su propio repositorio.
