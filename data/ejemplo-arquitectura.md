# Arquitectura del sistema RAG

## Componentes principales

Un sistema RAG (Retrieval-Augmented Generation) consta de dos pipelines:

### Pipeline de ingesta
1. **Carga de documentos**: Se leen archivos en múltiples formatos (PDF, DOCX, TXT, Markdown, código fuente).
2. **Chunking**: El texto se divide en fragmentos de tamaño configurable con overlap para mantener contexto.
3. **Embeddings**: Cada chunk se convierte en un vector numérico usando un modelo de embeddings (en este caso, bge-m3).
4. **Almacenamiento**: Los vectores se guardan en un vector store (ChromaDB) junto con metadata del documento.

### Pipeline de consulta
1. **Embedding de la query**: La pregunta del usuario se convierte en un vector.
2. **Búsqueda semántica**: Se buscan los chunks más similares en el vector store usando distancia coseno.
3. **Inyección de contexto**: Los chunks relevantes se inyectan en el prompt del LLM.
4. **Generación**: El LLM genera una respuesta basada en el contexto proporcionado.

## Ventajas del RAG
- Permite al LLM acceder a información actualizada sin reentrenamiento.
- Reduce las alucinaciones al anclar las respuestas en documentos reales.
- Es más económico que el fine-tuning para dominios específicos.
- Permite control granular sobre qué información está disponible.

## Limitaciones
- La calidad depende del chunking y del modelo de embeddings.
- Consultas muy ambiguas pueden recuperar contexto irrelevante.
- El contexto del LLM tiene un límite de tokens, lo que restringe cuántos chunks se pueden inyectar.
