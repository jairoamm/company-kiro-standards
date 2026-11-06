# Handoff sintético de HU-DEMO-001

**Estado:** listo para revisión de QA

**Contrato de selectores:** `1.2.0`

**Ejecución remota:** no autorizada por este paquete

Este paquete demuestra la estructura esperada con datos ficticios. El destino se recibe mediante `BASE_URL`; ningún valor de ambiente real se conserva aquí.

## Criterios y casos

| Criterio | Caso | Estado observable |
|---|---|---|
| CA-06 | CP-004 | Aparece una alerta accesible al rechazar credenciales inválidas |

## Gates declarados

- Compilación: aprobada en la ejecución sintética del pipeline.
- Pruebas unitarias: aprobadas en la misma ejecución.
- Revisión estática de selectores: completada sobre el commit declarado.

## Archivos

```text
qa-handoff/HU-DEMO-001/
├── README.md
├── deployment-context.json
├── ui-selectors.json
├── known-limitations.md
└── test-data/
    ├── README.md
    └── cp-004.json
```

- [Contexto de despliegue](deployment-context.json)
- [Contrato de selectores](ui-selectors.json)
- [Limitaciones conocidas](known-limitations.md)
- [Preparación y limpieza de datos](test-data/README.md)

QA debe revisar el paquete y autorizar por separado cualquier acceso al destino.
