# RAG POC — Retrieval-Augmented Generation sobre Lemonade Server

POC de un sistema RAG completo corriendo sobre infraestructura local con AMD Ryzen AI Max+ y Lemonade Server como backend LLM.

## Hardware

| Componente | Detalle |
|------------|---------|
| Máquina | Bosgame M5 Mini PC |
| CPU | AMD Ryzen AI Max+ 395 (16c/32t Zen5) |
| RAM | 96-128 GB LPDDR5X unificada |
| GPU | Radeon 8060S (40 CUs RDNA 3.5, Vulkan) |
| LLM Server | Lemonade 9.3.2 (snap, systemd, puerto 8000) |

## Objetivo

Implementar un RAG funcional que:

1. Use Lemonade como backend LLM (API compatible con OpenAI)
2. Proporcione UI web accesible desde la red local
3. Soporte ingesta de documentos mixtos (PDF, DOCX, TXT, Markdown, código)
4. Use embeddings locales (sin APIs externas de pago)
5. Sea reproducible y con dependencias mínimas

## Fases del proyecto

| Fase | Documento | Descripción |
|------|-----------|-------------|
| 0 | [Entorno](docs/00-entorno.md) | Descripción del hardware/software y reconocimiento del sistema |
| 1 | [Arquitectura](docs/01-arquitectura.md) | Decisiones de arquitectura con justificación |
| 2 | [Implementación](docs/02-implementacion.md) | Pasos de implementación detallados |
| 3 | [Validación](docs/03-validacion.md) | Pruebas de humo y resultados |

## Quick start

```bash
# 1. Clonar el repositorio
git clone https://github.com/<tu-usuario>/ragpoc.git
cd ragpoc

# 2. Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Verificar que Lemonade está corriendo
curl -s http://localhost:8000/api/v1/models | python3 -m json.tool

# 4. Seguir las instrucciones en docs/02-implementacion.md
```

## Requisitos previos

- Linux con AMD Ryzen AI Max+ (o GPU compatible con Vulkan)
- Lemonade Server instalado y corriendo como servicio systemd
- Python 3.10+
- 96+ GB de RAM unificada (para cargar modelos grandes)
