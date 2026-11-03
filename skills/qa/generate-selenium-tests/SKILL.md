---
name: generate-selenium-tests
description: Genera pruebas de caja negra con Java 21, JUnit 5 y Selenium desde un plan QA aprobado, una URL y un contrato de selectores. Úsalo en el repositorio de QA sin requerir código fuente de la aplicación.
---

# Generar pruebas Selenium de caja negra

## Propósito

Crear scripts Selenium revisables y trazables sin acceder al repositorio de Desarrollo ni modificar la aplicación desplegada.

## Entradas obligatorias

- Historia de Usuario y plan QA aprobado.
- `ui-selectors.json` entregado por Desarrollo.
- `BASE_URL` del ambiente autorizado.
- Build y commit de aplicación asociados a esa URL.
- Datos sintéticos y casos seleccionados.
- Comando finito de compilación o prueba del repositorio QA.

Si falta una entrada, enumera el bloqueo. No busques la respuesta en el repositorio de Desarrollo.

## Procedimiento

1. Valida el JSON y relaciona cada paso del plan con un selector publicado. Reporta casos sin cobertura o contratos contradictorios antes de escribir código.
2. Genera Java 21 con JUnit 5 y Selenium siguiendo la estructura existente del repositorio QA.
3. Lee la URL desde `BASE_URL` o desde la propiedad documentada por el proyecto; no incrustes hosts, credenciales ni datos reales.
4. Usa roles, nombres accesibles o las estrategias del contrato. No derives XPath estructural ni selectores de clases CSS internas.
5. Sincroniza con `WebDriverWait` y condiciones explícitas. No uses `Thread.sleep`.
6. Mantén casos independientes y nombres trazables a sus identificadores del plan.
7. Captura screenshots en checkpoints definidos y al fallar. Conserva además los resultados JUnit XML y registra URL, build, commit y versión del contrato.
8. Presenta el diff para revisión. Compila con el comando finito del repositorio y ejecuta solo cuando el ambiente esté autorizado y disponible.

## Salidas esperadas

- Clases de prueba Java y Page Objects solo cuando el repositorio ya use ese patrón.
- Configuración parametrizada de `BASE_URL`.
- Screenshots y resultados JUnit en rutas documentadas.
- Matriz de casos generados, pendientes y selectores consumidos.

## Límites

- No accedas, clones, construyas ni inicies el repositorio de Desarrollo.
- No despliegues ni modifiques la aplicación o el ambiente.
- No cambies assertions para obtener verde ni declares certificación sin una ejecución revisada por QA.
- No ejecutes contra un destino remoto sin autorización explícita.
