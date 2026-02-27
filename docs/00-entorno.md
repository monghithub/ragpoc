# Fase 0 — Entorno y reconocimiento

## Hardware

| Componente | Detalle |
|------------|---------|
| Máquina | Bosgame M5 Mini PC |
| CPU | AMD Ryzen AI Max+ 395 (16c/32t Zen5) |
| RAM | 96-128 GB LPDDR5X unificada (CPU + iGPU comparten el mismo pool) |
| GPU | Radeon 8060S (40 CUs RDNA 3.5, backend Vulkan) |

## Software base

| Componente | Detalle |
|------------|---------|
| OS | Linux (verificar distro exacta abajo) |
| LLM Server | Lemonade 9.3.2 (instalado vía snap) |
| Servicio | systemd nativo en `/etc/systemd/system/lemonade.service` |
| Endpoint | `http://localhost:8000/api/v1` (compatible con OpenAI) |
| Backend inferencia | Vulkan |
| Contexto máximo | 32768 tokens |

## Modelos disponibles en Lemonade

| Modelo | Cuantización | Tamaño | Uso recomendado |
|--------|-------------|--------|-----------------|
| Qwen3-8B | Q4_1 | ~5.3 GB | Iteración rápida / dev |
| Qwen3-Coder-30B-A3B-Instruct | Q4_K_M | ~18.6 GB | Generación de código |
| Qwen3-Next-80B-A3B-Instruct | Q4_K_XL | ~42.9 GB | Inferencia de máx calidad |

## Resultados del reconocimiento

> Los resultados de los comandos de verificación se documentarán aquí tras ejecutar la Fase 0.

### Verificación de la API de Lemonade

```bash
curl -s http://localhost:8000/api/v1/models | python3 -m json.tool
```

```
(pendiente)
```

### Distro y versión del OS

```bash
cat /etc/os-release
```

```
(pendiente)
```

### Python disponible

```bash
python3 --version && pip3 --version
```

```
(pendiente)
```

### Gestores de entorno

```bash
which conda || which uv || echo "solo pip"
```

```
(pendiente)
```

### Espacio en disco

```bash
df -h /
```

```
(pendiente)
```

### Vector stores instalados

```bash
pip3 list 2>/dev/null | grep -E "chroma|faiss|qdrant|weaviate"
```

```
(pendiente)
```
