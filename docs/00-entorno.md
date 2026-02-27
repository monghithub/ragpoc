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
| OS | Ubuntu 25.10 (Questing Quokka) |
| Kernel | Linux 6.17.0-14-generic |
| Python | 3.13.7 |
| pip | 25.1.1 |
| Gestores de entorno | Solo pip (sin conda ni uv) |
| LLM Server | Lemonade 9.3.2 (instalado vía snap) |
| Servicio | systemd nativo en `/etc/systemd/system/lemonade.service` |
| Endpoint | `http://localhost:8000/api/v1` (compatible con OpenAI) |
| Backend inferencia | Vulkan |
| Contexto máximo | 32768 tokens |
| Disco disponible | 1.4 TB libres de 1.9 TB (21% usado) |

## Modelos disponibles en Lemonade

Verificado con `curl -s http://localhost:8000/api/v1/models`:

| ID del modelo (API) | Checkpoint | Tamaño | Uso recomendado |
|---------------------|------------|--------|-----------------|
| `Qwen3-8B-GGUF` | `unsloth/Qwen3-8B-GGUF:Q4_1` | 5.25 GB | Iteración rápida / dev |
| `Qwen3-Next-80B-A3B-Instruct-GGUF` | `unsloth/Qwen3-Next-80B-A3B-Instruct-GGUF:...Q4_K_XL.gguf` | 45.1 GB | Inferencia de máx calidad |

> **Nota:** El modelo Qwen3-Coder-30B-A3B-Instruct mencionado en el seed prompt no está disponible actualmente en la API. Los modelos `extra.*` son referencias alternativas a los mismos checkpoints.

## Resultados del reconocimiento

### Verificación de la API de Lemonade

```bash
curl -s http://localhost:8000/api/v1/models | python3 -m json.tool
```

API respondiendo correctamente. 4 entradas en total (2 modelos principales + 2 referencias `extra.*` a los mismos checkpoints).

### Distro y versión del OS

```bash
cat /etc/os-release
```

```
PRETTY_NAME="Ubuntu 25.10"
VERSION="25.10 (Questing Quokka)"
ID=ubuntu
ID_LIKE=debian
```

### Python disponible

```bash
python3 --version && pip3 --version
```

```
Python 3.13.7
pip 25.1.1 from /usr/lib/python3/dist-packages/pip (python 3.13)
```

### Gestores de entorno

```bash
which conda || which uv || echo "solo pip"
```

```
solo pip
```

### Espacio en disco

```bash
df -h /
```

```
S.ficheros     Tamaño Usados  Disp Uso% Montado en
/dev/nvme0n1p2   1,9T   368G  1,4T  21% /
```

### Vector stores instalados

```bash
pip3 list 2>/dev/null | grep -E "chroma|faiss|qdrant|weaviate"
```

```
Ningún vector store instalado
```

## Resumen y observaciones para Fase 1

- **Lemonade funciona** y responde en el endpoint esperado
- **Modelos disponibles:** Qwen3-8B (dev) y Qwen3-Next-80B (calidad). El Coder-30B no está cargado
- **Ubuntu 25.10** con Python 3.13.7 — distro reciente, paquetes apt disponibles
- **Solo pip** como gestor — usaremos `python3 -m venv` para aislar dependencias
- **1.4 TB libres** — sin restricciones de disco
- **Sin vector stores previos** — instalación limpia, elegimos libremente
