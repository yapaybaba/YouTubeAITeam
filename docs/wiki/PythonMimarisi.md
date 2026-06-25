**Özet:** Video'da gösterilen Python mimarisi LangChain tabanlı bir state machine kullanıyor; SystemMessage ile context yönetimi, response_content ile çıktı toplama ve show_content ile görüntüleme adımları var. Multi-agent sistemde her agent kendi state'ini yönetiyor.
**Kütüphaneler/Teknolojiler:** Python, LangChain, Claude API (Anthropic), State Management
**Bağlantılar:** [[ClaudeDesignAjans]], [[WatchYoutubePipeline]]

## State Yönetimi

```python
system_prompt = f"..."
feedback_context = f"[Feedback] {state['feedback']}..." if state.get('feedback') else ""

for chunk in llm.stream([SystemMessage(...)]):
    response_content += chunk.content
    show_content(response_content)
```

## Mimari Özellikleri

- **State**: Her agent çağrısı arasında `state` dict ile veri taşınır
- **Streaming**: `llm.stream()` ile gerçek zamanlı çıktı
- **Feedback loop**: Önceki iterasyondan gelen feedback bir sonraki prompt'a eklenir
- **Local LLM uyumlu**: LangChain arayüzü sayesinde Claude veya local LLM ile çalışabilir (LiteLLM + Local LLM)
