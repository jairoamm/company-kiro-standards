---
inclusion: always
---

# Estándares para calidad y automatización

- Diseña casos desde los criterios y riesgos. Registra precondiciones, datos, pasos, resultado esperado, prioridad, plataforma y evidencia.
- Usa Postman para exploración o reproducción y una única suite versionada para regresión de API. No mantengas escenarios equivalentes en dos frameworks.
- Reserva Selenium o Appium para recorridos críticos. Prefiere identificadores estables y Page Objects; evita XPath frágiles y esperas fijas.
- Las pruebas deben ser independientes, repetibles y capaces de limpiar o aislar sus datos.
- Conserva el build, ambiente, versión del runner, hora y artefactos de cada ejecución.
- Un fallo de automatización no implica automáticamente un defecto de producto. Clasifica producto, prueba o ambiente con evidencia.
- No ocultes inestabilidad mediante reintentos ilimitados ni cambies una assertion para conseguir verde.
- Define performance a partir de un objetivo medible. Si faltan umbrales o capacidad autorizada, prepara el plan y solicita decisiones; no inventes carga.
- Kiro puede preparar código y análisis, pero Selenium, Appium, Karate y JMeter producen la evidencia ejecutada y una persona revisa la conclusión.
