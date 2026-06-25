# AGENTS.md — YouTubeAITeam Ajan ve Skill Tanımları

Bu dosya projedeki tüm ajanları, skill'leri ve rollerini tanımlar.
Claude Code bu dosyayı okuyarak hangi bileşenin ne yaptığını anlar.

---

## LangGraph Ajanları (`agents.py`)

### `ResearcherAgent`
- **Rol:** Web içeriği toplayıcı
- **Giriş:** `state["target_url"]` — kazınacak URL
- **Çıkış:** `state["scraped_data"]` — temizlenmiş markdown içerik
- **Model:** Ollama (direkt LLM kullanmaz, crawl4ai kullanır)
- **Özellik:** Navigasyon linklerini (`[text](url)` formatı) filtreler; sadece içerik satırlarını döndürür.

### `CoderAgent`
- **Rol:** Python kodu üretici
- **Giriş:** `state["scraped_data"]`, `state["user_request"]`, `state["feedback"]`
- **Çıkış:** `state["final_code"]`, `state["iteration"]`
- **Model:** `ChatOllama(model="gemma4:e4b", temperature=0.1)`
- **Özellik:** Feedback loop — önceki iterasyonun hatalarını prompt'a ekler, max iterasyon `state["iteration"]` ile izlenir.

### `ReviewerAgent`
- **Rol:** Kod denetçisi
- **Giriş:** `state["user_request"]`, `state["final_code"]`
- **Çıkış:** `state["is_approved"]` (bool), `state["feedback"]` (ret gerekçesi)
- **Model:** `ChatOllama(model="gemma4:e4b", temperature=0)`
- **Özellik:** Yalnızca `ONAYLANDI` veya `REDDEDİLDİ: [Nedenler]` döndürür. Temperature=0 — deterministik karar.

---

## LangGraph Akışı (`main.py`)

```
ResearcherAgent
      │
      ▼
CoderAgent
      │
      ▼
ReviewerAgent ──── ONAYLANDI ──▶ [Bitti]
      │
   REDDEDİLDİ
      │
      ▼
CoderAgent (feedback ile yeniden)
```

---

## Skill'ler (`docs/skills/`)

### `watch-youtube` skill
- **Konum:** `~/Watch_Youtube_Skill/.claude/skills/watch-youtube/SKILL.md`
- **Rol:** YouTube video → storyboard → wiki sayfası pipeline'ı
- **Tetikleyici:** Kullanıcı bir YouTube URL'i paylaştığında
- **Giriş:** YouTube URL
- **Çıkış:** `docs/wiki/<TopicName>.md`, `docs/wiki/Videos.md`, `docs/wiki/Index.md`
- **Bağımlılıklar:** `watch-youtube` CLI (`~/Watch_Youtube_Skill/`), ffmpeg, spaCy, Groq API (opsiyonel)
- **Pipeline:**
  ```
  URL → yt-dlp (transcript) → spaCy (NLP timestamp) → ffmpeg (frame) → Pillow (storyboard) → Vision LLM (wiki)
  ```

### `ingest` skill
- **Konum:** `docs/skills/ingest/SKILL.md`
- **Rol:** Git diff → wiki otomatik güncelleme
- **Tetikleyici:** Kod değişikliği commit'lendikten sonra, ya da kullanıcı "wiki'yi güncelle" / "ingest yap" dediğinde
- **Giriş:** `git diff HEAD~1` çıktısı
- **Çıkış:** Güncellenen veya yeni `docs/wiki/*.md` sayfaları
- **Modül → Wiki eşleştirme:**
  | Dosya | Wiki sayfası |
  |-------|-------------|
  | `agents.py` | `docs/wiki/Agents.md` |
  | `main.py` | `docs/wiki/Pipeline.md` |
  | `state.py` | `docs/wiki/AgentState.md` |
  | `output.py` | `docs/wiki/OutputLayer.md` |
  | `requirements.txt` | `docs/wiki/Dependencies.md` |

### `wiki-schema` skill
- **Konum:** `~/Watch_Youtube_Skill/.claude/skills/wiki-schema/SKILL.md`
- **Rol:** Wiki dosyası format kuralları ve operasyon tipleri (INGEST, QUERY, VIDEO_INGEST)
- **Kullanım:** `watch-youtube` ve `ingest` skill'leri bu kuralları referans alır

---

## AgentState (`state.py`)

```python
class AgentState(TypedDict):
    target_url: str        # ResearcherAgent girişi
    user_request: str      # Kullanıcının kodu ne yapmasını istediği
    scraped_data: str      # ResearcherAgent çıktısı
    final_code: str        # CoderAgent çıktısı
    is_approved: bool      # ReviewerAgent kararı
    feedback: str          # ReviewerAgent ret gerekçesi (CoderAgent'a geri döner)
    iteration: int         # Kaç kez denendi
```

---

## Dosya Ağacı

```
YouTubeAITeam/
├── agents.py              # ResearcherAgent, CoderAgent, ReviewerAgent
├── main.py                # LangGraph pipeline tanımı
├── state.py               # AgentState TypedDict
├── output.py              # CoderAgent demo çıktısı (Pydantic AI RAG örneği)
├── requirements.txt       # Python bağımlılıkları
├── AGENTS.md              # Bu dosya — ajan ve skill tanımları
├── PROGRESS.md            # İlerleme kaydı
└── docs/
    ├── wiki/              # Otonom bilgi grafiği (AI tarafından yazılır)
    │   ├── Index.md       # Ana harita
    │   ├── Videos.md      # Analiz edilen YouTube videoları
    │   ├── wiki_schema.md # Wiki yazma kuralları (bu projenin CLAUDE.md'si)
    │   └── *.md           # Modül ve video sayfaları
    └── skills/            # Bağımsız skill araçları
        └── ingest/
            ├── SKILL.md   # Claude Code talimatları (skill wrapper)
            └── ingest.py  # Git diff → wiki CLI aracı (çalıştırılabilir)

# Harici Skill'ler (ayrı repo)
~/Watch_Youtube_Skill/
├── watch_youtube/         # Python paketi
│   ├── main.py            # CLI entry point (watch-youtube komutu)
│   ├── downloader.py      # yt-dlp + Groq Whisper transcript
│   ├── analyzer.py        # spaCy NLP + TF-IDF keyword store
│   ├── extractor.py       # ffmpeg frame extraction
│   └── compiler.py        # Pillow storyboard grid
├── data/
│   └── keyword_store.json # TF-IDF öz-öğrenme verisi
└── .claude/skills/
    ├── watch-youtube/
    │   └── SKILL.md       # YouTube analiz skill talimatları
    └── wiki-schema/
        └── SKILL.md       # Wiki format kuralları (genel, tüm projeler için)
```
