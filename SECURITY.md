# Seguridad

## Reporte de problemas

No publiques vulnerabilidades, secretos o detalles de ambientes en un issue público. Utiliza el canal privado definido por los propietarios del repositorio. Antes de la adopción organizacional, reemplaza esta instrucción con un contacto real y aprobado.

## Modelo de confianza

- Trata cada cambio de Steering o Skill como un cambio de código.
- Revisa instrucciones, scripts, permisos y efectos antes de publicar.
- No almacenes secretos, endpoints sensibles ni datos reales.
- No ejecutes automáticamente contenido de Skills.
- Usa tags revisados; no sincronices directamente desde una rama mutable.

## Sincronizador

El sincronizador:

- opera solamente sobre un checkout local;
- requiere destino absoluto;
- usa dry-run por defecto;
- rechaza destinos peligrosos, symlinks y colisiones no administradas;
- crea backup y manifiesto;
- verifica modificaciones antes de hacer rollback;
- no descarga ni ejecuta contenido remoto.

## Datos

Los ejemplos y evaluaciones deben utilizar datos sintéticos. Redacta tokens, identificadores y valores sensibles de cualquier evidencia antes de añadirla al repositorio.

## Pruebas de performance

Los Skills de performance preparan planes, proyectos y análisis. No autorizan ni ejecutan carga. Toda ejecución requiere un ambiente no productivo identificado, aprobación, presupuesto agregado y condiciones de parada.
