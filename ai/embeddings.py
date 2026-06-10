from google import genai
from utils.config import GEMINI_API_KEY

EMBEDDING_MODEL = "gemini-embedding-001"


def generate_embedding(text: str) -> list[float]:
    """
    Generates an embedding vector for resume or job text.

    Params:
        text: Resume or job text

    Returns:
        Embedding vector
    """
    if not text:
        raise ValueError("Text is required to generate an embedding")

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config={
            "output_dimensionality": 768
        }
    )

    return response.embeddings[0].values
