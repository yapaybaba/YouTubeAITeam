**Özet:** `AgentState`, LangGraph pipeline boyunca tüm ajanlar arasında akan tek veri yapısıdır. Her alan bir ajanın girdisi veya çıktısıdır; ajanlar state'i doğrudan değiştirmez, yeni dict döndürür.
**Kütüphaneler/Teknolojiler:** Python TypedDict, LangGraph
**Bağlantılar:** [[Agents]], [[Pipeline]]

---

## Tanım

```python
from typing import TypedDict

class AgentState(TypedDict):
    target_url: str      # ResearcherAgent girişi — kazınacak sayfa
    user_request: str    # CoderAgent girişi — ne yapılmasını istiyor?
    scraped_data: str    # ResearcherAgent çıktısı — temizlenmiş markdown
    final_code: str      # CoderAgent çıktısı — üretilen Python kodu
    feedback: str        # ReviewerAgent ret gerekçesi → CoderAgent'a geri döner
    is_approved: bool    # ReviewerAgent kararı — pipeline burada dallanır
    iteration: int       # Kaç kez CoderAgent çalıştı (max 3)
```

## Veri Akışı

| Alan | Yazan | Okuyan |
|------|-------|--------|
| `target_url` | Kullanıcı (ainvoke) | ResearcherAgent |
| `user_request` | Kullanıcı (ainvoke) | CoderAgent, ReviewerAgent |
| `scraped_data` | ResearcherAgent | CoderAgent |
| `final_code` | CoderAgent | ReviewerAgent |
| `feedback` | ReviewerAgent | CoderAgent (sonraki iterasyon) |
| `is_approved` | ReviewerAgent | `route_checker` |
| `iteration` | CoderAgent | `route_checker` (max 3 kontrolü) |

## Önemli Detay

`scraped_data` CoderAgent'a `[:10000]` ile kırpılarak gönderilir — context window sınırı aşılmasın diye. Ham veri state'te tam haliyle tutulur.
