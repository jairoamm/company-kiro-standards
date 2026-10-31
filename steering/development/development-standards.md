---
inclusion: always
---

# Estándares para desarrollo

- Sigue el lenguaje, framework, arquitectura y comandos ya configurados en el repositorio; no los deduzcas únicamente por la extensión del archivo.
- Implementa a partir de requisitos y criterios revisados. Expón dudas funcionales antes de codificar.
- Incluye pruebas unitarias o de componente para lógica nueva, ramas relevantes, límites y errores.
- Durante un bugfix, crea primero una reproducción automatizada que falle; no ajustes la prueba para que coincida con el defecto.
- Proporciona testabilidad: identificadores UI estables, errores estructurados, correlation IDs y fronteras sustituibles para dependencias externas.
- Ejecuta la prueba focalizada y la regresión relacionada. Si una suite no puede ejecutarse, explica la causa y el riesgo.
- Comparte con QA el resultado de cobertura y análisis estático disponible; no uses el porcentaje como sustituto de la cobertura de riesgos.
- Documenta en el ticket la causa confirmada, el cambio, las pruebas, el commit y el build listo para retest.
