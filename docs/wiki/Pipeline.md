**Özet:** `main.py`, LangGraph `StateGraph` ile üç ajanı birbirine bağlar. ReviewerAgent ret ederse CoderAgent'a geri döner; max 3 denemede veya onayda sonlanır.
**Kütüphaneler/Teknolojiler:** LangGraph, asyncio, Rich
**Bağlantılar:** [[Agents]], [[AgentState]], [[LangGraphLocalLLM]]

---

## Graf Yapısı

```
researcher ──▶ coder ──▶ reviewer
                 ▲            │
                 │    REDDEDİLDİ (iteration < 3)
                 └────────────┘
                              │
                         ONAYLANDI / max iter
                              ▼
                             END
```

## Conditional Edge: `route_checker`

```python
def route_checker(state: AgentState):
    if state.get("is_approved"):
        return "end"
    elif state.get("iteration", 0) >= 3:
        # Maksimum 3 deneme — sonsuz döngü koruması
        return "end"
    return "coder"
```

**Önemli:** `iteration` sayacı CoderAgent içinde artırılır. 3. redde sistem durur ve final state raporlanır.

## Graf Kurulumu

```python
workflow = StateGraph(AgentState)
workflow.add_node("researcher", researcher.run)
workflow.add_node("coder", coder.run)
workflow.add_node("reviewer", reviewer.run)
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "coder")
workflow.add_edge("coder", "reviewer")
workflow.add_conditional_edges("reviewer", route_checker, {"end": END, "coder": "coder"})
app = workflow.compile()
```

## Varsayılan Test Parametreleri

```python
final_state = await app.ainvoke({
    "target_url": "https://ai.pydantic.dev/agents/",
    "user_request": "Pydantic AI ile basit bir RAG ajanı kodla",
})
```

## Final State Raporu

Pipeline tamamlandığında Rich console'a şunlar yazdırılır:
- Hedef URL
- Kazınan verinin ilk 300 karakteri
- Toplam deneme sayısı (iteration)
- Onay durumu (Geçti / Kaldı)
- Üretilen kodun karakter uzunluğu
