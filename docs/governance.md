# Gobierno de Steering y Skills

## Ownership

Cada activo del catálogo declara un grupo propietario genérico. Antes de usar el repositorio en una organización real, sustituye esos grupos por equipos existentes y configura `CODEOWNERS` con identidades válidas.

No se incluye un archivo `CODEOWNERS` con usuarios ficticios porque produciría una apariencia falsa de revisión automática.

## Flujo de cambio

```text
Rama de trabajo
→ pull request
→ validación automática
→ revisión del owner del dominio
→ revisión de seguridad cuando cambien herramientas o comandos
→ aprobación
→ merge
→ tag inmutable
→ piloto
→ adopción general
```

## Versionamiento

Usa versionamiento semántico:

- `PATCH`: aclaración sin cambio conductual o corrección compatible.
- `MINOR`: nuevo activo o nueva regla compatible.
- `MAJOR`: cambio que puede modificar significativamente el comportamiento o retirar activos.

`catalog.json` y todos los bundles publicados deben compartir la misma versión.

## Canales

- **candidate:** versión en evaluación por owners y equipos piloto.
- **stable:** versión aprobada para adopción general.
- **deprecated:** versión aún disponible con fecha de retiro.

El sincronizador trabaja sobre el checkout local proporcionado. El mecanismo organizacional que distribuye tags o artefactos debe verificar origen e integridad.

## Revisión requerida

### Steering

- Alcance suficientemente general.
- Ausencia de contradicciones.
- Regla accionable y verificable.
- Separación entre estándar de workspace, perfil personal por rol y contexto específico del proyecto.
- Impacto sobre desarrollo y QA revisado por ambos roles.

### Skills

- Activadores claros.
- Entradas y salidas definidas.
- Herramientas y efectos explícitos.
- Datos y secretos protegidos.
- Comportamiento fail-closed cuando falten autorizaciones.
- Evaluación con escenarios positivos, negativos y ambiguos.

## Deprecación

1. Marca el activo como `deprecated` en el catálogo.
2. Publica la alternativa y la fecha de retiro.
3. Mantén al menos una versión compatible durante la migración acordada.
4. Retíralo en una versión mayor.
5. No borres archivos de los computadores mediante una actualización implícita.

## Rollback

Cada instalación genera un backup local. El rollback restaura únicamente archivos tocados por esa instalación y se detiene si detecta modificaciones posteriores.

Para una regresión organizacional:

1. Suspende la promoción de la versión afectada.
2. Publica la versión estable anterior como recomendada.
3. Comunica alcance e impacto.
4. Pide rollback explícito a los consumidores afectados.
5. Corrige mediante un nuevo pull request; no reescribas un tag publicado.

## Métricas útiles

- Equipos y versiones instaladas.
- Tiempo desde propuesta hasta versión estable.
- Fallos de validación por categoría.
- Rollbacks.
- Skills activados y resultados revisados, si la plataforma lo mide sin datos sensibles.
- Incidentes causados por reglas obsoletas o contradictorias.

Las métricas de adopción no prueban por sí solas una mejora de calidad.
