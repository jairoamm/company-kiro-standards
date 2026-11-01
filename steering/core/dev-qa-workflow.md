---
inclusion: always
---

# Flujo compartido entre desarrollo y calidad

- QA diseña el plan de pruebas durante el refinamiento o Backlog y lo relaciona con los criterios de aceptación.
- Desarrollo utiliza la Historia de Usuario y el plan de pruebas como entradas para el diseño y la implementación.
- Desarrollo mantiene las pruebas unitarias y de componente del código que modifica.
- QA mantiene la validación funcional, de servicios, end-to-end y de performance según el riesgo y la responsabilidad acordada.
- Cada criterio de aceptación debe tener un propietario, un nivel de prueba, un resultado esperado y una evidencia identificable.
- El handoff hacia Testing debe incluir commit, build, ambiente, pruebas pre-deploy, cobertura disponible, limitaciones y criterios implementados.
- Un bug debe registrar Historia de Usuario, criterio afectado, caso, pasos, esperado, observado, build, ambiente, datos, plataforma, reproducibilidad y evidencia.
- Separa hechos, hipótesis y causa confirmada. Una captura prueba el síntoma; no demuestra por sí sola la causa técnica.
- Antes de corregir un bug, reproduce el comportamiento y agrega la prueba de regresión en el nivel más bajo que pueda demostrarlo.
- La corrección debe ser mínima, revisada y acompañada por evidencia roja antes del cambio y verde después.
- Desarrollo entrega el nuevo build y la evidencia técnica. QA realiza una validación independiente antes de cerrar el bug o certificar la Historia de Usuario.
