**Özet:** `output.py`, CoderAgent'ın Pydantic AI + RAG mimarisi kullanarak ürettiği bir demo çıktısıdır. Proje için çalışan bir output formatlayıcı değil; RAG ajanı entegrasyon örneği olarak repository'e eklenmiştir.
**Kütüphaneler/Teknolojiler:** pydantic-ai, OpenAI API
**Bağlantılar:** [[Agents]], [[Pipeline]], [[LangGraphLocalLLM]]

---

## Dosyanın Niteliği

`output.py` iki farklı şeyi gösteriyor:

1. **CoderAgent'ın ürettiği kod örneği** — `main.py` pipeline'ının test çıktısı
2. **Pydantic AI + RAG entegrasyon deseni** — gelecekte kullanılabilecek referans mimari

## İçerdiği Bileşenler

### `KNOWLEDGE_BASE`
Statik metin listesi — gerçek uygulamada vektör DB (Pinecone, Chroma) ile değiştirilmeli:
```python
KNOWLEDGE_BASE = [
    "Pydantic, Python geliştiricileri için veri doğrulama aracıdır...",
    "RAG (Retrieval-Augmented Generation)..."
]
```

### `retrieve_context(query, knowledge_base, top_k=2)`
Basit keyword skoru ile en ilgili chunk'ları seçer. Üretim için **vektör benzerliği** ile değiştirilmeli.

### `RAGResponse` (Pydantic Model)
```python
class RAGResponse(BaseModel):
    answer: str          # LLM'in ürettiği nihai cevap
    source_context: str  # Hangi bağlamdan türetildiği
```

### `run_rag_agent(user_query)`
Retrieval → Augmentation → Generation döngüsünü çalıştırır.

## Dikkat Edilmesi Gereken Sorunlar

- `OPENAI_API_KEY` environment variable zorunlu — yoksa `pass` ile geçiyor (hata yutulur)
- `agent.invoke()` kullanımı güncel Pydantic AI API'sine uymayabilir — kontrol edilmeli
- Dosya direkt çalıştırılırsa 3 örnek sorgu çalışır — production için `main` bloğu düzenlenmeli

## Statü

Bu dosya aktif pipeline'ın parçası değil. `main.py` pipeline'ı `output.py`'yi import etmiyor.
