# CONTEXTO DEL ENTORNO

Máquina: Bosgame M5 Mini PC
CPU: AMD Ryzen AI Max+ 395 (16c/32t Zen5)
RAM: 96-128 GB LPDDR5X unificada (CPU + iGPU comparten el mismo pool)
GPU: Radeon 8060S (40 CUs RDNA 3.5, backend Vulkan)
OS: Linux (no Ubuntu — verificar distro exacta antes de asumir gestores de paquetes)

## Servidor LLM existente: Lemonade

- Instalación: Snap (lemonade-server 9.3.2)
- Servicio: systemd nativo en /etc/systemd/system/lemonade.service
- Escucha: 0.0.0.0:8000
- API: compatible con OpenAI → base_url = http://localhost:8000/api/v1
- Backend de inferencia: Vulkan
- Contexto máximo: 32768 tokens
- NO usar Docker para Lemonade — ya está corriendo como servicio nativo

## Modelos disponibles en Lemonade

| Modelo                        | Cuantización | Tamaño   | Uso recomendado          |
|-------------------------------|--------------|----------|--------------------------|
| Qwen3-8B                      | Q4_1         | ~5.3 GB  | Iteración rápida / dev   |
| Qwen3-Coder-30B-A3B-Instruct  | Q4_K_M       | ~18.6 GB | Generación de código     |
| Qwen3-Next-80B-A3B-Instruct   | Q4_K_XL      | ~42.9 GB | Inferencia de máx calidad|

Con 96 GB de RAM unificada, el modelo 80B puede cargarse completamente.

---

# OBJETIVO

Implementar un RAG (Retrieval-Augmented Generation) POC completo sobre esta
infraestructura existente. El sistema debe:

1. Usar Lemonade como backend LLM (NO instalar Ollama ni otro servidor de inferencia)
2. Proporcionar UI web accesible desde la red local
3. Soportar ingesta de documentos mixtos: PDF, DOCX, TXT, Markdown, código fuente
4. Usar embeddings locales (sin llamadas a APIs externas de pago)
5. Ser reproducible y con dependencias mínimas

---

# RESTRICCIONES Y DECISIONES DE DISEÑO

- La API base es OpenAI-compatible: cualquier cliente que acepte `base_url` + `api_key`
  arbitraria puede conectarse a Lemonade sin modificaciones.
- El modelo de embeddings debe ser independiente del modelo de chat (Lemonade sirve
  modelos generativos, NO modelos de embeddings dedicados tipo nomic-embed-text).
  Evaluar: sentence-transformers local en Python, o un segundo proceso de embeddings.
- Preferencia por soluciones que no requieran Docker si el componente puede correr
  nativamente sin fricción. Si un componente tiene dependencias complejas, Docker es
  aceptable como excepción justificada.
- El stack debe ser mantenible por un arquitecto de software senior: código comprensible,
  sin "magic" innecesario.

---

# TAREAS PARA CLAUDE CODE

## Fase 0 — Reconocimiento (HACER PRIMERO)

Antes de escribir código, ejecuta los siguientes comandos para verificar el estado real
del entorno y no asumir nada:

```bash
# Verificar API de Lemonade
curl -s http://localhost:8000/api/v1/models | python3 -m json.tool

# Verificar distro y versión
cat /etc/os-release

# Verificar Python disponible
python3 --version && pip3 --version

# Verificar si hay conda/venv/uv
which conda || which uv || echo "solo pip"

# Espacio en disco
df -h /

# Verificar si chromadb o algún vector store ya está instalado
pip3 list 2>/dev/null | grep -E "chroma|faiss|qdrant|weaviate"
```

## Fase 1 — Decisión de arquitectura

Con los resultados del reconocimiento, proponer la arquitectura mínima viable:

- **Vector store**: ChromaDB (local, sin servidor) vs Qdrant (Docker) vs FAISS (in-memory)
  Criterio de selección: persistencia + facilidad de ingesta + soporte de metadata filtering

- **Embeddings**: sentence-transformers con modelo `all-MiniLM-L6-v2` o `bge-m3`
  (multilingüe, mejor para datos mixtos en español/inglés)

- **UI web**: Open WebUI (si soporta `base_url` custom para Lemonade)
  vs AnythingLLM (integración nativa con OpenAI-compatible backends y RAG propio)
  vs implementación Python mínima con Streamlit o FastAPI + UI simple

  INVESTIGAR: si Open WebUI permite configurar un embedding model externo separado
  del servidor Ollama, dado que Lemonade no sirve embeddings.

- **Orquestación RAG**: LlamaIndex vs LangChain vs implementación directa
  Para POC: evaluar LlamaIndex por su abstracción más limpia sobre vector stores.

## Fase 2 — Implementación mínima funcional

Implementar en este orden:

1. Script de verificación de conectividad con Lemonade
2. Pipeline de embeddings local (sentence-transformers)
3. Ingesta de documentos con chunking configurable
4. Almacenamiento en vector store persistente
5. Pipeline de consulta (embed query → search → context injection → Lemonade)
6. UI web o endpoint REST que una todo

## Fase 3 — Validación

Diseñar una prueba de humo que verifique el ciclo completo:
- Ingestar 2-3 documentos de prueba
- Realizar 3 consultas: una con respuesta en los docs, una ambigua, una fuera del corpus
- Medir: latencia de respuesta, relevancia del contexto recuperado, tokens consumidos

---

# MODELO A USAR DURANTE EL DESARROLLO

Para iteración rápida: Qwen3-8B (5.3 GB, respuesta más rápida)
Para validación final: Qwen3-Next-80B-A3B-Instruct (máxima calidad)

Parámetros de conexión:
- base_url: http://localhost:8000/api/v1
- api_key: "lemonade" (o cualquier string — Lemonade no valida el key)
- model: nombre exacto según output de /api/v1/models
