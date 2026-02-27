# Fase 1 — Decisiones de arquitectura

## Resumen de decisiones

| Componente | Elección | Alternativas descartadas |
|------------|----------|--------------------------|
| Vector store | ChromaDB (embedded) | Qdrant (Docker), FAISS (in-memory) |
| Embeddings | bge-m3 (sentence-transformers) | all-MiniLM-L6-v2 |
| UI web | Streamlit (custom) | Open WebUI, AnythingLLM |
| Orquestación RAG | Implementación directa | LlamaIndex, LangChain |

## Diagrama de componentes

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                          │
│              (upload docs + chat + contexto)             │
└───────────┬──────────────────────────┬──────────────────┘
            │                          │
            ▼                          ▼
┌───────────────────┐      ┌──────────────────────────┐
│  Ingesta pipeline │      │   Query pipeline          │
│                   │      │                            │
│  1. Cargar doc    │      │  1. Embed query (bge-m3)  │
│  2. Chunking      │      │  2. Search ChromaDB       │
│  3. Embed (bge-m3)│      │  3. Construir prompt      │
│  4. Store ChromaDB│      │  4. Llamar Lemonade       │
└───────────────────┘      └──────────────────────────┘
            │                          │
            ▼                          ▼
┌───────────────────┐      ┌──────────────────────────┐
│     ChromaDB      │      │    Lemonade Server        │
│  (persistencia    │      │  localhost:8000/api/v1    │
│   local en disco) │      │  (Qwen3-8B / Qwen3-80B)  │
└───────────────────┘      └──────────────────────────┘
```

## Justificación detallada

### Vector store: ChromaDB (embedded)

**Elegido porque:**
- Persistencia a disco con un solo argumento (`persist_directory`)
- Filtrado por metadata con cláusula `where` sobre cualquier campo
- Modo embedded: no requiere servidor, contenedor ni proceso aparte
- API Python simple y directa

**Descartados:**
- **FAISS:** Sin persistencia nativa ni filtrado por metadata. Requiere mantener estructuras auxiliares para metadatos. Diseñado para escala (billones de vectores), innecesario para un POC
- **Qdrant:** Requiere Docker como sidecar. Ofrece filtrado avanzado (booleano, rangos, geo) que no necesitamos en un POC. Complejidad operativa injustificada

**Riesgo:** ChromaDB 1.x tuvo problemas de compatibilidad con Python 3.13 (issues #5643, #4382). La versión 1.5.1 (febrero 2026) incluye wheels `cp39-abi3` que deberían funcionar. Verificar instalación limpia antes de depender de él; fallback: usar venv con Python 3.12.

### Embeddings: bge-m3

**Elegido porque:**
- Soporte multilingüe (100+ idiomas incluyendo español e inglés)
- Entrenado específicamente para retrieval multilingüe y cross-lingual
- MTEB score de 63.0 — significativamente superior a MiniLM en texto no inglés
- Vectores de 1024 dimensiones con opción de sparse + ColBERT para retrieval híbrido
- ~567M parámetros, ~1.1 GB en disco (fp16) — manejable en nuestra máquina con 96+ GB RAM

**Descartado:**
- **all-MiniLM-L6-v2:** 22M params, 80 MB, 384 dims. Extremadamente rápido pero entrenado primariamente en inglés. Calidad de retrieval en español degrada notablemente. Para datos mixtos español/inglés, no es viable

**Trade-off:** bge-m3 es ~10x más lento que MiniLM en CPU. En nuestro Ryzen AI Max+ 395 con GPU integrada RDNA 3.5, la diferencia se reduce. Para un POC con cientos de documentos, el tiempo de ingesta no es bloqueante.

### UI web: Streamlit (custom)

**Elegido porque:**
- Único camino que integra bge-m3 vía sentence-transformers sin fricción
- Control total sobre el pipeline: upload → ingesta → query → respuesta
- ~100-200 líneas de Python para un UI funcional
- Sin dependencias adicionales pesadas (no Docker, no Ollama, no Electron)

**Descartados:**
- **Open WebUI:** Su pipeline RAG requiere embeddings vía Ollama o endpoint `/v1/embeddings` compatible. Lemonade expone ese endpoint pero solo para modelos GGUF (no sentence-transformers). Usar bge-m3 requeriría instalar Ollama como servicio adicional solo para embeddings — contraproducente
- **AnythingLLM:** Embedder por defecto es MiniLM (inglés). No soporta modelos sentence-transformers arbitrarios (issue #3668 abierto, no resuelto). Mismo problema que Open WebUI

**Restricción clave:** Lemonade sirve modelos generativos vía llamacpp, NO modelos de embeddings de sentence-transformers. bge-m3 corre in-process en Python y no se expone como endpoint HTTP. Esto descarta cualquier UI que espere consumir embeddings vía API.

### Orquestación RAG: Implementación directa

**Elegido porque:**
- 3 dependencias core: `openai` + `chromadb` + `sentence-transformers`
- Pipeline transparente: embed → search → prompt → LLM en ~50-80 líneas
- Sin abstracciones de framework que oscurezcan el flujo
- Fácil de debuggear, explicar y modificar
- Si el POC escala, migrar a LlamaIndex es directo

**Descartados:**
- **LangChain:** Árbol de dependencias masivo. API inestable con cambios frecuentes entre versiones. Agentes, tools, memory — todo innecesario para un retrieve-then-generate simple
- **LlamaIndex:** Abstracciones más limpias que LangChain para RAG, pero aún impone un modelo mental propio (Nodes, ServiceContext, VectorStoreIndex) que añade indirección sin beneficio proporcional en un POC

## Stack final

```
sentence-transformers (bge-m3)    → embeddings locales
chromadb                          → vector store persistente
openai (client)                   → comunicación con Lemonade
streamlit                         → UI web
pypdf / python-docx               → carga de documentos
```

## Parámetros de conexión a Lemonade

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/api/v1",
    api_key="lemonade",  # Lemonade no valida el key
)

# Modelo para desarrollo rápido
model_dev = "Qwen3-8B-GGUF"

# Modelo para validación final
model_prod = "Qwen3-Next-80B-A3B-Instruct-GGUF"
```
