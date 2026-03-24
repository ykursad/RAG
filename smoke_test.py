from pathlib import Path

from app.config import get_settings
from app.services.rag_service import RagService

settings = get_settings()
service = RagService(settings)

test_file = Path("data/uploads/smoke_test.txt")
test_file.write_text(
    "RAG sistemleri önce ilgili bilgi parçalarını bulur. "
    "Ardından bu bağlamı kullanarak cevap üretir. "
    "Kaynaklı cevap üretmek güvenilirliği artırır.",
    encoding="utf-8",
)

print("1) Ingest başlıyor...")
ingest_result = service.ingest_document(test_file)
print("Ingest sonucu:", ingest_result)

print("\n2) Retrieve başlıyor...")
retrieve_result = service.retrieve("RAG sistemleri nasıl çalışır?", top_k=4)
print("Retrieve sonucu sayısı:", len(retrieve_result))

print("\n3) Answer başlıyor...")
answer_result = service.answer("RAG sistemleri nasıl çalışır?", top_k=4)
print("Final cevap:\n")
print(answer_result["answer"])
print("\nKaynak sayısı:", answer_result["source_count"])