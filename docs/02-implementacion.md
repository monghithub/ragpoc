# Fase 2 — Implementación

## Dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Dependencias principales:

| Paquete | Versión | Uso |
|---------|---------|-----|
| `openai` | 2.24.0 | Cliente para Lemonade (API compatible con OpenAI) |
| `chromadb` | 1.5.2 | Vector store embedded persistente |
| `sentence-transformers` | 5.2.3 | Embeddings locales (bge-m3) |
| `streamlit` | 1.54.0 | UI web |
| `pypdf` | 6.7.4 | Lectura de PDFs |
| `python-docx` | 1.2.0 | Lectura de DOCX |

## Estructura del código

```
src/
├── __init__.py
├── config.py          # Configuración central
├── embeddings.py      # Pipeline bge-m3
├── chunking.py        # Extracción de texto + chunking
├── vectorstore.py     # ChromaDB: ingesta y búsqueda
├── rag.py             # Pipeline RAG completo
└── app.py             # UI Streamlit
```

## Paso 1 — Configuración (`src/config.py`)

Centraliza todos los parámetros en un solo archivo:

```python
LEMONADE_BASE_URL = "http://localhost:8000/api/v1"
LEMONADE_API_KEY = "lemonade"          # Lemonade no valida el key
LEMONADE_MODEL = "Qwen3-8B-GGUF"      # Modelo por defecto (dev)

EMBEDDING_MODEL = "BAAI/bge-m3"       # 1024 dims, multilingüe
CHROMA_PERSIST_DIR = "./chroma_data"   # Persistencia en disco
CHUNK_SIZE = 512                       # Palabras por chunk
CHUNK_OVERLAP = 50                     # Overlap entre chunks
TOP_K = 5                             # Chunks a recuperar
```

Todos los valores se pueden sobreescribir con variables de entorno.

## Paso 2 — Pipeline de embeddings (`src/embeddings.py`)

Usa `sentence-transformers` con el modelo `BAAI/bge-m3`:

- El modelo se carga como singleton (solo una vez, ~1.1 GB en memoria)
- Genera vectores de **1024 dimensiones** normalizados
- Dos funciones: `embed_texts()` para batch y `embed_query()` para una sola query

## Paso 3 — Ingesta de documentos (`src/chunking.py`)

Soporta múltiples formatos:
- **PDF** vía `pypdf`
- **DOCX** vía `python-docx`
- **TXT, MD, código fuente** — lectura directa

El chunking divide el texto en fragmentos de `CHUNK_SIZE` palabras con `CHUNK_OVERLAP` palabras de overlap. Cada chunk incluye metadata:

```python
{
    "text": "contenido del chunk...",
    "metadata": {
        "source": "documento.pdf",
        "chunk_index": 0,
        "total_chunks": 15
    }
}
```

## Paso 4 — Vector store (`src/vectorstore.py`)

ChromaDB en modo embedded con persistencia a disco:

- `ingest_chunks()`: recibe chunks, genera embeddings, almacena en ChromaDB
- `search()`: embed de la query → búsqueda por distancia coseno → retorna top_k chunks
- `get_stats()`: retorna estadísticas de la colección

## Paso 5 — Pipeline RAG (`src/rag.py`)

Flujo completo en `query_rag()`:

1. **Retrieve**: busca chunks relevantes en ChromaDB
2. **Prompt**: construye el prompt inyectando contexto + system prompt
3. **Generate**: llama a Lemonade vía `openai.OpenAI(base_url=...)`
4. **Return**: respuesta + fuentes + métricas de uso de tokens

El system prompt instruye al LLM a:
- Responder basándose en el contexto proporcionado
- Declarar cuando no tiene la información
- Responder en el idioma de la pregunta

## Paso 6 — UI web (`src/app.py`)

Streamlit con dos áreas principales:

**Sidebar (izquierda):**
- Upload de documentos (multi-archivo)
- Botón de ingesta con progreso
- Métricas del vector store (chunks almacenados)
- Selector de modelo (Qwen3-8B / Qwen3-80B)
- Slider de top_k

**Área principal:**
- Chat interactivo con historial
- Cada respuesta muestra las fuentes utilizadas (expandible)
- Métricas de tokens consumidos

### Ejecución

```bash
source venv/bin/activate
streamlit run src/app.py
```

La UI estará disponible en `http://localhost:8501` y accesible desde la red local.

## Verificación de conectividad

```bash
source venv/bin/activate
python tests/test_connectivity.py
```

Verifica:
1. Que Lemonade responde y lista modelos
2. Que Lemonade genera respuestas de chat
3. Que bge-m3 genera embeddings (1024 dimensiones)
4. Que ChromaDB funciona en modo embedded

## Documentos de ejemplo

En `data/` hay 3 documentos para pruebas:
- `ejemplo-arquitectura.md` — Descripción de componentes RAG
- `ejemplo-lemonade.txt` — Información sobre Lemonade Server
- `ejemplo-hardware.txt` — Especificaciones del Bosgame M5
