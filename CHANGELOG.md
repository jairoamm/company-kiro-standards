# Changelog

Todos los cambios relevantes de este proyecto se documentan aquí.

## [0.2.3] - Unreleased

### Added

- Skill QA `prepare-synthetic-test-data` para que Kiro proponga un borrador de `qa-input/<HU>/test-data.json` desde la HU, el plan y las limitaciones disponibles, con revisión y responsabilidad de QA.

### Changed

- Añadida la Skill al catálogo y al bundle QA; los tres bundles avanzan de forma compatible a `0.2.3`.
- Ampliado el validador para exigir la adopción QA y los límites de datos reales, estados de backend, ejecución y certificación.
- La Skill documenta la secuencia: preparar y revisar los datos antes de generar Selenium, Karate o JMeter.

## [0.2.2] - 2026-11-05

### Added

- Skill QA `generate-karate-tests` para generar features y runners JUnit desde contratos API aprobados, sin duplicar Postman ni inventar autenticación.
- Ejemplos pequeños y rutas de salida concretas para Selenium, Karate, trazabilidad, handoff y performance.

### Changed

- Reestructuradas todas las Skills como procedimientos operativos con activadores, entradas, bloqueos, pasos, validación finita, manejo de fallos y responsabilidades.
- Aclarada la trazabilidad `CA-06 → CP-004` y su separación respecto a la selección de herramientas, ejecución y certificación.
- Reforzado el handoff para obtener URL, build y commit exclusivamente de la evidencia del pipeline.
- Reforzadas las tres Skills de performance para exigir carga y umbrales aprobados, destino no productivo y revisión de JTL y `errorCount`.
- Ampliado el validador para exigir la estructura mínima de toda Skill catalogada y rechazar afirmaciones de ejecución o certificación autónoma e instrucciones de persistir secretos.

## [0.2.1] - 2026-11-03

### Added

- Perfiles globales manuales y separados para investigación QA y resolución Development de bugs.
- Guía de alcances, frontera de intercambio con acceso de solo lectura y flujo de handoff QA → Development.
- Validaciones para impedir que los perfiles personales entren en el catálogo o en bundles de workspace.

### Changed

- Documentados los bundles exclusivamente como assets de workspace instalados en `<repo>/.kiro/` mediante pull request.

## [0.2.0] - 2026-11-02

### Added

- Steering de testabilidad UI para Desarrollo y contrato versionado `ui-selectors.json`.
- Skill de Desarrollo para preparar el handoff hacia QA sin generar Selenium ni desplegar.
- Steering de automatización QA de caja negra y Skill para generar pruebas Selenium con Java 21 y JUnit 5.
- Skill compartida para transcribir y aprobar la trazabilidad antes de construir una matriz.
- Validación de activos obligatorios y separación de responsabilidades en los bundles `developer` y `qa`.

### Changed

- Documentado el consumo de estándares mediante release central, pull request y revisión en cada proyecto.

## [0.1.1] - 2026-11-01

### Changed

- Actualizada la terminología para usar “validación de QA” en los estándares compartidos.

## [0.1.0] - 2026-10-28

### Added

- Catálogo de Steering y Skills.
- Bundles `common`, `developer` y `qa`.
- Baseline de seguridad, calidad y colaboración Dev + QA.
- Tres Skills de preparación y análisis de performance con JMeter.
- Sincronizador local con dry-run, backup, manifiesto y rollback.
- Validación estática y documentación de gobierno.
