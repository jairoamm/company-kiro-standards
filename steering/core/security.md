---
inclusion: always
---

# Seguridad y manejo de datos

- No escribas secretos, tokens, contraseñas ni credenciales en código, pruebas, prompts, logs o reportes. Usa el mecanismo de secretos aprobado por el proyecto.
- Trata toda entrada externa como no confiable. Valida formato, tamaño, rango y autorización en el límite donde ingresa.
- Conserva la autenticación y autorización existentes. No agregues bypasses ni debilites controles para facilitar desarrollo o pruebas.
- Aplica mínimo privilegio a identidades, permisos y accesos de automatización.
- Evita datos sensibles en errores, capturas y evidencias. Redacta cualquier valor que no sea necesario para diagnosticar.
- Usa datos completamente sintéticos en demos, talleres y pruebas compartidas.
- Mantén servicios y almacenamiento privados por defecto. No amplíes exposición de red sin una decisión explícita y revisada.
- Revisa dependencias nuevas, fija versiones siguiendo las convenciones del proyecto y explica por qué son necesarias.
- Las pruebas de carga solo pueden ejecutarse contra un objetivo no productivo autorizado, con tasa, duración, responsable y condiciones de parada definidos.
- Si falta información para aplicar una regla de seguridad, detente y solicita la decisión. No inventes una excepción.
