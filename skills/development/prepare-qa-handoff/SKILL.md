---
name: prepare-qa-handoff
description: Prepara un handoff verificable de Desarrollo hacia QA con contrato de selectores, datos sintéticos, contexto del pipeline y limitaciones. Úsalo al cerrar una Historia de Usuario o entregar un build a Testing.
---

# Preparar handoff para QA

## Propósito

Empaquetar la información que QA necesita para validar una interfaz sin depender del repositorio de Desarrollo. El handoff identifica qué se implementó, cómo localizar estados observables y qué build está desplegado; no crea automatización Selenium ni certifica la entrega.

## Cuándo usarla

Úsala después de implementar y validar una Historia de Usuario con interfaz, antes de entregar un build a QA o cuando cambia un selector publicado. No la uses para desplegar, iniciar servicios, ejecutar pruebas remotas ni investigar un defecto reportado.

## Políticas relacionadas

Aplica `steering/development/ui-testability.md`, `steering/core/dev-qa-workflow.md`, `steering/core/security.md` y `steering/core/engineering-quality.md`. Este procedimiento materializa el handoff y no sustituye esas políticas.

## Entradas obligatorias

Proporciona:

- `product/<HU>/user-story.md` o la ruta equivalente: criterios de aceptación aprobados.
- `product/<HU>/test-plan.md` o referencia al plan QA aprobado y sus casos.
- Código frontend del commit que se entregará.
- Resultado de los gates locales documentados por el proyecto.
- Artefacto de pipeline o salida verificable con `environment`, `baseUrl`, `buildId`, `applicationCommit` y referencia de la ejecución.
- Datos completamente sintéticos y pasos de preparación o limpieza.
- Limitaciones conocidas y criterios implementados.

La URL autorizada, el build y el commit de aplicación provienen del pipeline que desplegó la entrega. Desarrollo los transcribe desde esa evidencia; no los calcula ni los inventa.

## Precondiciones y bloqueos

Confirma antes de declarar el handoff listo:

- La Historia de Usuario y el plan corresponden al mismo alcance.
- El frontend abierto está en el commit que reporta el pipeline.
- Los gates requeridos terminaron y su resultado está disponible.
- Cada selector publicado existe de forma estática en ese commit o su estado condicional está documentado.
- El pipeline desplegó correctamente el build en el ambiente indicado.
- Los datos son sintéticos y no contienen secretos.

Si todavía no existe despliegue, Desarrollo MAY preparar el contrato y los documentos con estado `pendiente`, pero el handoff queda bloqueado. No sustituyas URL, build o commit con valores locales.

## Procedimiento

1. Lee la Historia de Usuario y el plan. Construye la relación `criterio → caso → control o estado observable`.
2. Inspecciona el frontend del commit entregable. Prefiere roles, nombres y etiquetas accesibles; usa `data-testid` solo cuando la semántica no produzca un localizador estable.
3. Crea o actualiza `qa-handoff/<HU>/ui-selectors.json` con `schemaVersion`, `contractVersion`, `historia` y `selectors`.
4. Incluye en cada selector `nombre`, `pantalla`, `estado`, `estrategia`, `valor` y `casosRelacionados`. Para estrategia `role`, añade el nombre accesible cuando sea necesario distinguir elementos.
5. Compara el contrato con la versión anterior. Una adición compatible conserva la versión mayor; retirar, renombrar o cambiar el significado de un selector exige una versión mayor y una nota de migración.
6. Comprueba estáticamente que los selectores existen en el frontend. Documenta condiciones de aparición y selectores reutilizados en estados mutuamente excluyentes.
7. Obtén `baseUrl`, `buildId`, `applicationCommit`, ambiente y referencia de ejecución desde la salida del pipeline. Copia esos campos a `deployment-context.json` y conserva la procedencia. No uses una URL observada manualmente como sustituto.
8. Añade datos sintéticos mínimos bajo `test-data/` y documenta preparación, aislamiento, caducidad y limpieza en `test-data/README.md`.
9. Registra riesgos, funcionalidad no incluida y restricciones del ambiente en `known-limitations.md`.
10. Genera `README.md` con criterios implementados, gates, árbol del paquete, versión del contrato y enlaces relativos a todos los archivos.
11. Revisa el diff, valida JSON y ejecuta los gates locales finitos del proyecto. Presenta el resultado para revisión conjunta con QA.

## Archivos de salida

```text
qa-handoff/<HU>/
├── README.md
├── deployment-context.json
├── ui-selectors.json
├── known-limitations.md
└── test-data/
    ├── README.md
    └── cp-004.json
```

`deployment-context.json` debe copiar la identidad del despliegue desde el pipeline y no debe contener credenciales. `README.md` marca el handoff como `pendiente` hasta que todos los campos obligatorios y gates estén verificados.

## Ejemplo de prompt

```text
Prepara el handoff de HU-DEMO-001 en qa-handoff/HU-DEMO-001. Usa el plan aprobado,
el frontend del commit actual y el artefacto deployment-context.json emitido por el pipeline.
Incluye selectores para CP-004, datos sintéticos y limitaciones. No generes Selenium,
no despliegues y no inventes URL, build ni commit si falta la evidencia del pipeline.
```

## Ejemplo de salida

Árbol abreviado:

```text
qa-handoff/HU-DEMO-001/
├── README.md
├── deployment-context.json
├── ui-selectors.json
├── known-limitations.md
└── test-data/cp-004.json
```

Contrato corto:

```json
{
  "schemaVersion": "1.0",
  "contractVersion": "1.2.0",
  "historia": "HU-DEMO-001",
  "selectors": [
    {
      "nombre": "mensajeCredencialesInvalidas",
      "pantalla": "login",
      "estado": "credenciales rechazadas",
      "estrategia": "role",
      "valor": "alert",
      "nombreAccesible": "Credenciales inválidas",
      "casosRelacionados": ["CP-004"]
    }
  ]
}
```

El README cita la referencia del pipeline como fuente de URL, build y commit. Si esa salida falta, muestra `Estado del handoff: bloqueado por contexto de despliegue`.

## Validación

Usa comandos locales, finitos y sin iniciar la aplicación:

```bash
HU="${HU:?defina HU}"
python3 -m json.tool "qa-handoff/$HU/ui-selectors.json" >/dev/null
python3 -m json.tool "qa-handoff/$HU/deployment-context.json" >/dev/null
git diff --check -- "qa-handoff/$HU"
npm test -- --run
```

Sustituye `npm test -- --run` por el gate finito ya documentado por el proyecto cuando use otra herramienta. Revisa además el diff de `ui-selectors.json` para detectar cambios incompatibles.

## Manejo de fallos

- **Salida del pipeline ausente:** conserva `Estado: pendiente`, enumera los campos faltantes y no declares listo el handoff.
- **Commit distinto:** detente; solicita un nuevo despliegue o la evidencia correcta.
- **Selector inexistente:** corrige el frontend o retira la entrada antes del handoff; no publiques un contrato falso.
- **Cambio incompatible:** incrementa la versión mayor y añade instrucciones de migración para QA.
- **Gate local fallido:** reporta comando y error; no ocultes el fallo ni entregues como aprobado.
- **Dato no sintético o secreto:** exclúyelo del paquete y solicita un reemplazo seguro.

## Límites y responsabilidades

- Desarrollo mantiene el frontend, sus pruebas unitarias o de componente y el contrato de selectores.
- El pipeline aporta URL autorizada, build, commit y referencia de despliegue.
- QA mantiene la suite Selenium, la ejecución independiente y la certificación funcional.
- No generes, modifiques ni ejecutes pruebas Selenium como parte de este procedimiento.
- No despliegues, inicies servicios ni cambies ambientes.
- No almacenes secretos, tokens, cookies, datos reales ni causas técnicas no confirmadas en el handoff.
- Un handoff completo habilita el trabajo de QA; no prueba por sí mismo que la Historia de Usuario esté aprobada.
