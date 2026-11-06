# Responsabilidades de Postman y Karate

## Postman

Usa Postman para:

- explorar una operación mientras se revisa el contrato;
- reproducir rápidamente un caso reportado;
- compartir una solicitud sanitizada con otro equipo;
- preparar una ejecución Newman separada cuando QA la autorice.

La colección puede incluir assertions ligeras para facilitar la reproducción. Su generación o importación no envía solicitudes.

## Karate

Usa Karate como única suite versionada de regresión de API en el pipeline. Karate conserva tags, trazabilidad, gates y evidencia repetible para los casos seleccionados como regresión.

## Evitar duplicación

Cuando un caso existe en ambos formatos:

1. Karate conserva la responsabilidad de regresión.
2. Postman declara que su copia sirve para exploración o reproducción.
3. Un cambio de contrato se aplica primero a la suite propietaria y después, si sigue aportando valor, a la solicitud compartible.
4. QA elimina una reproducción obsoleta en vez de mantener dos fuentes de verdad.

## Ejecución y evidencia

Newman puede ejecutar una colección solo cuando una persona lo invoca con un destino autorizado. JUnit y HTML son artefactos de esa ejecución posterior; la presencia de la colección no significa que exista un resultado.

Usa `BASE_URL` para el destino. Mantén el environment versionado como plantilla con `NO_SUMINISTRADO`; inyecta cualquier material de autenticación mediante el proveedor seguro aprobado y no lo exportes desde Postman.
