---
name: test-plan-traceability
description: Transcribe y relaciona una Historia de Usuario con su plan de pruebas sin completar contenido ausente. Úsalo con entradas en texto, Markdown, PDF o imagen antes de crear una matriz de trazabilidad.
---

# Preparar trazabilidad entre Historia de Usuario y plan de pruebas

## Propósito

Convertir documentos entregados en una base revisable antes de generar cualquier matriz de criterios y casos.

## Entradas admitidas

- Historia de Usuario y plan como texto pegado o archivos Markdown.
- PDF legible.
- Imagen o captura legible.
- Identificador esperado de la Historia de Usuario, si se conoce.

## Procedimiento

1. Identifica por separado la Historia de Usuario y el plan, su formato y su procedencia.
2. Transcribe primero todo el contenido relevante. Conserva identificadores, criterios, casos, tablas y resultados esperados sin resumirlos ni corregirlos.
3. Marca cada fragmento que no pueda leerse como `[ilegible: ubicación]`. No deduzcas palabras, identificadores ni valores faltantes.
4. Señala páginas ausentes, referencias rotas, contradicciones y criterios o casos sin identificador. No inventes contenido para cerrar brechas.
5. Presenta la transcripción y la lista de brechas. Espera aprobación explícita antes de producir una matriz.
6. Tras la aprobación, genera una matriz que relacione criterio, caso, nivel, propietario, resultado esperado y referencia de origen. Usa `sin evidencia` o `no definido` cuando corresponda.
7. Mantén visibles los elementos sin relación en ambos sentidos y solicita corrección del documento fuente cuando impidan una decisión.

## Salidas esperadas

- Transcripción revisable con marcas de contenido ilegible.
- Lista de brechas y contradicciones.
- Matriz de trazabilidad aprobada, solo después de la confirmación humana.

## Límites

- No generes la matriz antes de que la transcripción sea aprobada.
- No uses conocimiento del producto para completar texto ilegible o ausente.
- No cambies criterios ni resultados esperados para hacerlos coincidir con pruebas existentes.
- No declares cobertura ni certificación cuando la fuente sea incompleta.
