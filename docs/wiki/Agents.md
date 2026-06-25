**Özet:** `agents.py`, üç uzman ajan içerir: web kazıyıcı ResearcherAgent, Python kodu üreten CoderAgent ve kodu denetleyen ReviewerAgent. Hepsi LangGraph `AgentState` üzerinden birbirine bağlıdır.
**Kütüphaneler/Teknolojiler:** LangChain, langchain-ollama, crawl4ai, Rich
**Bağlantılar:** [[AgentState]], [[Pipeline]], [[LangGraphLocalLLM]]

---

## `ResearcherAgent`

URL'i crawl4ai ile kazır, ham markdown'ı temizler ve state'e yazar.

```python
class ResearcherAgent:
    async def run(self, state: AgentState) -> dict:
        # crawl4ai ile sayfayı indir
        result = await crawler.arun(url=state["target_url"])
        raw = result.markdown.raw_markdown
```

**Giriş:** `state["target_url"]`
**Çıkış:** `state["scraped_data"]`, `state["iteration"] = 0`, `state["feedback"] = ""`

### Navigasyon Filtresi [GÜNCELLEME: 2026-06-25]

Ham markdown'dan navigasyon linklerini ayıklar; böylece LLM'e giden içerik gürültüden arındırılır:

```python
lines = raw.split("\n")
content_lines = [
    line for line in lines
    if not (line.strip().startswith("[") and "](" in line)          # [text](url) satırları
    and not (line.strip().startswith("* [") or line.strip().startswith("- ["))  # liste linkleri
]
markdown_content = "\n".join(content_lines).strip()
```

**Neden önemli:** Sidebar, header ve footer linkleri içeriğin %20-40'ını oluşturabilir; filtresiz gönderilirse token israfı ve gürültü artar.

---

## `CoderAgent`

LLM'e scraped_data + user_request gönderir, streaming Python kodu üretir.

```python
class CoderAgent:
    def __init__(self):
        self.llm = ChatOllama(model="gemma4:e4b", temperature=0.1)

    def run(self, state: AgentState) -> dict:
        iteration = state.get("iteration", 0) + 1
        feedback_context = f"\nÖnceki hata: {state['feedback']}..." if state.get("feedback") else ""
        # streaming ile çıktı üret
        for chunk in self.llm.stream([SystemMessage(content=system_prompt)]):
            response_content += chunk.content
        return {"final_code": response_content, "iteration": iteration}
```

**Giriş:** `state["scraped_data"][:10000]`, `state["user_request"]`, `state["feedback"]`
**Çıkış:** `state["final_code"]`, `state["iteration"]`
**Model:** `gemma4:e4b`, temperature=0.1 (yaratıcılık dengeli)

---

## `ReviewerAgent`

Üretilen kodu denetler; `ONAYLANDI` veya `REDDEDİLDİ: [neden]` döndürür.

```python
class ReviewerAgent:
    def __init__(self):
        self.llm = ChatOllama(model="gemma4:e4b", temperature=0)

    def run(self, state: AgentState) -> dict:
        response = self.llm.invoke([HumanMessage(content=prompt)]).content
        if "ONAYLANDI" in response.upper():
            return {"is_approved": True, "feedback": ""}
        return {"is_approved": False, "feedback": response}
```

**Giriş:** `state["user_request"]`, `state["final_code"]`
**Çıkış:** `state["is_approved"]` (bool), `state["feedback"]`
**Model:** `gemma4:e4b`, temperature=0 (deterministik karar)
