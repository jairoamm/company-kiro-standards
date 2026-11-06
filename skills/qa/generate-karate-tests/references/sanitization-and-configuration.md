# Configuración y sanitización de Karate

Esta referencia complementa el procedimiento principal. Ajusta cada opción a la versión de Karate y a las convenciones ya presentes en el repositorio.

## Destino

Lee el destino en tiempo de ejecución. La configuración puede priorizar la propiedad Java y usar `BASE_URL` como alternativa:

```javascript
function fn() {
  var baseUrl = karate.properties['baseUrl'] || java.lang.System.getenv('BASE_URL');
  if (!baseUrl) {
    karate.fail('BASE_URL debe identificar el destino autorizado');
  }

  karate.configure('logPrettyRequest', false);
  karate.configure('logPrettyResponse', false);
  karate.configure('report', { showLog: false, showAllSteps: true });
  return { baseUrl: baseUrl };
}
```

No añadas un host predeterminado. Que el archivo compile sin `BASE_URL` no autoriza una solicitud.

## Autenticación

- Usa solamente el proveedor seguro aprobado por el proyecto.
- Inyecta referencias en tiempo de ejecución; no copies valores al feature, `karate-config.js`, fixtures o comandos compartidos.
- No imprimas headers de autorización, cookies ni respuestas de autenticación.
- Si el mecanismo no está documentado, bloquea la ejecución en vez de crear uno.

## Evidencia sanitizada

1. Desactiva logs de request y response cuando puedan contener material sensible. `logPrettyRequest=false` solo cambia formato; no sustituye `showLog=false`.
2. Conserva en reportes únicamente campos funcionales necesarios para demostrar la assertion.
3. Redacta tokens, cookies, identificadores sensibles y payloads antes de adjuntar evidencia.
4. Revisa JUnit XML, HTML y metadata, porque cada formato puede conservar mensajes distintos.
5. Si un plugin o versión ofrece un modificador HTTP aprobado, pruébalo con fixtures sintéticos antes de confiar en él.

## Separación de fases

La compilación local puede validar sintaxis y runner. La ejecución contra `BASE_URL` requiere autorización explícita y produce evidencia en una fase posterior. Ninguna configuración convierte la generación en autorización.
