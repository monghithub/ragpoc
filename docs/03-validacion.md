# Fase 3 — Validación

## Configuración del test

- **Modelo:** Qwen3-8B-GGUF (Q4_1, ~5.3 GB)
- **Embeddings:** bge-m3 (1024 dimensiones)
- **Vector store:** ChromaDB embedded (limpio, sin datos previos)
- **Script:** `tests/test_smoke.py`

## Documentos ingestados

| Documento | Chunks | Contenido |
|-----------|--------|-----------|
| `ejemplo-hardware.txt` | 1 | Specs del Bosgame M5 (CPU, GPU, RAM, disco) |
| `ejemplo-lemonade.txt` | 1 | Info sobre Lemonade Server (API, modelos, conexión) |
| `ejemplo-arquitectura.md` | 1 | Componentes de un sistema RAG (pipelines, ventajas, limitaciones) |

Total: **3 chunks** en el vector store.

## Resultados de las consultas

### 1. Consulta con respuesta en los docs

**Query:** *¿Cuántos CUs tiene la GPU Radeon 8060S?*

**Respuesta:**
> La GPU Radeon 8060S tiene **40 Compute Units (CUs)**, según la especificación del Bosgame M5 Mini PC.

| Métrica | Valor |
|---------|-------|
| Latencia | 44.1s |
| Tokens prompt | — |
| Tokens total | 1384 |
| Fuente principal | `ejemplo-hardware.txt` |

**Análisis:** Respuesta correcta y precisa. El sistema recuperó el chunk correcto como primera fuente y extrajo el dato exacto (40 CUs).

### 2. Consulta ambigua

**Query:** *¿Qué modelo es mejor?*

**Respuesta:**
> La elección del modelo depende del uso específico y las necesidades del usuario. Según el contexto proporcionado:
> - **Qwen3-8B (Q4_1)**: Ideal para desarrollo e iteración rápida debido a su tamaño más pequeño.
> - [continúa comparando con Qwen3-Next-80B...]

| Métrica | Valor |
|---------|-------|
| Latencia | 76.0s |
| Tokens total | 1878 |
| Fuente principal | `ejemplo-lemonade.txt` |

**Análisis:** Buen manejo de la ambigüedad. En lugar de inventar o elegir arbitrariamente, el sistema interpretó "modelo" en el contexto de los documentos (modelos LLM de Lemonade) y dio una comparación fundamentada con el contexto disponible.

### 3. Consulta fuera del corpus

**Query:** *¿Cuál es la receta de paella valenciana?*

**Respuesta:**
> No tengo información sobre la receta de paella valenciana, ya que el contexto proporcionado se centra en temas técnicos relacionados con servidores de inferencia LLM, arquitectura de sistemas RAG y especificaciones de hardware.

| Métrica | Valor |
|---------|-------|
| Latencia | 14.3s |
| Tokens total | 1379 |

**Análisis:** Comportamiento correcto. El sistema declara explícitamente que no tiene la información y explica el dominio de los documentos disponibles. No alucina.

## Resumen de métricas

| Métrica | Valor |
|---------|-------|
| Latencia promedio | **44.8s** |
| Tokens totales consumidos | **4641** |
| Modelo | Qwen3-8B-GGUF |
| Queries exitosas | 3/3 |

## Observaciones

1. **La latencia es alta** (~45s promedio) porque Qwen3-8B corre por inferencia Vulkan en la iGPU. La query fuera del corpus fue la más rápida (14s) porque la respuesta es corta. La query ambigua fue la más lenta (76s) por generar una respuesta más elaborada.

2. **El chunking es grueso** — con 512 palabras por chunk y documentos pequeños, cada documento cabe en un solo chunk. En un escenario real con documentos largos, el chunking producirá más fragmentos y la búsqueda semántica será más selectiva.

3. **El pipeline RAG funciona end-to-end:**
   - Ingesta: carga doc → chunk → embed (bge-m3) → store (ChromaDB) ✓
   - Query: embed query → search → inject context → Lemonade → respuesta ✓

4. **Robustez:** Se añadió lógica de reintentos en `src/rag.py` porque Lemonade ocasionalmente devuelve `choices: None` mientras recarga el modelo entre peticiones.

## Ejecución

```bash
# Limpiar datos previos
rm -rf chroma_data

# Ejecutar prueba de humo
source venv/bin/activate
python tests/test_smoke.py
```
