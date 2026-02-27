"""Script de verificación de conectividad con Lemonade."""

import sys
from openai import OpenAI

sys.path.insert(0, ".")
from src.config import LEMONADE_BASE_URL, LEMONADE_API_KEY, LEMONADE_MODEL


def test_lemonade_models():
    """Verifica que Lemonade responde y lista modelos."""
    client = OpenAI(base_url=LEMONADE_BASE_URL, api_key=LEMONADE_API_KEY)
    models = client.models.list()
    model_ids = [m.id for m in models.data]
    print(f"Modelos disponibles: {model_ids}")
    assert len(model_ids) > 0, "No hay modelos disponibles"
    print("PASS: Lemonade responde y tiene modelos cargados")


def test_lemonade_chat():
    """Verifica que Lemonade puede generar una respuesta."""
    import time
    client = OpenAI(base_url=LEMONADE_BASE_URL, api_key=LEMONADE_API_KEY)

    # Lemonade puede tardar en cargar el modelo la primera vez
    for attempt in range(3):
        response = client.chat.completions.create(
            model=LEMONADE_MODEL,
            messages=[{"role": "user", "content": "Responde solo 'OK' sin nada más."}],
        )
        answer = response.choices[0].message.content
        if answer is not None:
            break
        print(f"  Intento {attempt + 1}: respuesta None, esperando carga del modelo...")
        time.sleep(5)

    print(f"Respuesta de Lemonade ({LEMONADE_MODEL}): {answer!r}")
    assert answer is not None and len(answer) > 0, "Respuesta vacía tras 3 intentos"
    print("PASS: Lemonade genera respuestas correctamente")


def test_embeddings():
    """Verifica que el modelo de embeddings carga y genera vectores."""
    from src.embeddings import embed_texts
    vectors = embed_texts(["Esto es una prueba de embeddings"])
    assert len(vectors) == 1
    assert len(vectors[0]) > 0
    print(f"PASS: Embeddings generados ({len(vectors[0])} dimensiones)")


def test_chromadb():
    """Verifica que ChromaDB funciona en modo embedded."""
    import chromadb
    client = chromadb.EphemeralClient()
    collection = client.create_collection("test")
    collection.add(ids=["1"], documents=["test"], embeddings=[[0.1] * 384])
    assert collection.count() == 1
    print("PASS: ChromaDB funciona en modo embedded")


if __name__ == "__main__":
    print("=== Verificación de conectividad ===\n")

    tests = [test_lemonade_models, test_lemonade_chat, test_embeddings, test_chromadb]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"FAIL: {test.__name__} — {e}")
        print()

    print("=== Verificación completa ===")
