from app.config import get_settings
from app.services.ollama_client import OllamaClient

client = OllamaClient(get_settings())

print("Healthcheck:", client.healthcheck())

emb = client.embed(["RAG sistemi nedir?"])
print("Embedding boyutu:", len(emb[0]))

answer = client.chat(
    system_prompt="Sen yardımcı bir asistansın.",
    user_prompt="RAG nedir? Kısa açıkla."
)

print("Chat cevabı:")
print(answer)