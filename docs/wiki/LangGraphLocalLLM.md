**Özet:** LangGraph ile otonom AI ekibi kurma rehberi — sıfır API maliyetiyle (Local LLM) çalışan, CoderAgent/ResearcherAgent gibi uzman agent'ların birbirini besleyen bir state machine oluşturuyor. Token maliyeti 6 kat artma yerine %80+ düşüyor.
**Kütüphaneler/Teknolojiler:** LangGraph, LangChain, Local LLM (LiteLLM proxy), Python, Claude Code
**Bağlantılar:** [[PythonMimarisi]], [[WatchYoutubePipeline]], [[ClaudeDesignAjans]]

## Mimari

```
Python tarafı               Claude Code tarafı
─────────────────          ──────────────────
Videoyu indir         →    Storyboard analizi
NLP ile parçala       →    Wiki sayfası yaz
Görselliği birleştir  →    Bilgi çıkar
```

> "Fyton tarafı sadece ameliyat yapıyor. Videoyu indir, NLP ile parçala, görselliği birleştir. Analizi yapacak olan ise Cloud Code."

## CoderAgent State Machine

```python
def run(self, state: AgentState):
    iteration = state.get("iteration", 0) + 1
    feedback_context = f"[Önceki denemeki hatalar: {state['feedback']}...]" if state.get("feedback") else ""
    system_prompt = f"Sen Senior bir Python geliştiricisin..."
    response_content = ""
    for chunk in self.llm.stream([SystemMessage(content=system_prompt)]):
        response_content += chunk.content
    return {"response_content": response_content}
```

## Token Tasarrufu

- Naive yaklaşım: Her frame'i ayrı ayrı gönder → 6 kat maliyet artışı
- Pipeline yaklaşımı: NLP ile seç + storyboard grid → %80+ düşüş
- Local LLM ile: API maliyeti = 0$

## Önemli Noktalar

- Terminal hataları altyazıda görünmez → `watch-youtube` bunu aşmak için görsel analiz kullanır
- Diagram geçişlerinde konuşmacı susar → sessizlik tespiti (Rule B) bu anları yakalar
- Feedback loop: agent bir önceki iterasyonun hatalarını bir sonraki prompt'a taşır
