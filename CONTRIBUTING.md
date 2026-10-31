# Contribuir

## Antes de proponer un cambio

1. Identifica si el contenido es global, propio de un rol o específico de un proyecto.
2. Mantén el contexto de una aplicación fuera de este repositorio.
3. Confirma el owner que revisará el activo.
4. Evita duplicar capacidades nativas de Kiro con un Skill.

## Flujo

1. Crea una rama.
2. Modifica el activo y, si aplica, el catálogo y los bundles.
3. Actualiza la versión y `CHANGELOG.md` cuando corresponda.
4. Ejecuta:

   ```bash
   python3 checks/validate.py
   ```

5. Prueba dry-run, apply y rollback contra un KIRO_HOME temporal.
6. Revisa el diff completo.
7. Abre un pull request con propósito, impacto, evidencia y rollback.

## Criterios para un Steering

- Regla estable y compartida.
- Lenguaje claro y accionable.
- Sin datos, rutas o comandos específicos de una persona.
- Sin duplicación con otro Steering.
- Alcance documentado.

## Criterios para un Skill

- Procedimiento especializado y repetible.
- Activadores, entradas, salidas y límites explícitos.
- Sin efectos implícitos.
- Sin secretos.
- Evaluado con entradas completas, incompletas y contradictorias.

## Commits

Usa conventional commits en inglés, por ejemplo:

```text
feat(steering): add accessibility baseline
fix(sync): reject unmanaged target collision
```
