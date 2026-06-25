---
name: ingest
description: Git diff çıktısını alıp değişen modüllere karşılık gelen wiki sayfalarını otomatik günceller veya yeni sayfa oluşturur. Tetikleyiciler: "wiki'yi güncelle", "son değişiklikleri kaydet", "ingest yap", "git diff'i wikiye yaz", "kod değişikliklerini belgele".
---

# INGEST: Git Diff → Wiki Güncelleme

Değişen Python modüllerini tarar, her dosya için `docs/wiki/` altındaki ilgili sayfayı bulur veya oluşturur. **wiki-schema** kurallarına uyar.

---

## Çalıştırma Adımları

### 1. Diff Al

```bash
# Son commit'ten bu yana değişen dosyalar
git -C ~/YouTubeAITeam diff HEAD~1 --name-only

# Tam diff (içerik analizi için)
git -C ~/YouTubeAITeam diff HEAD~1
```

Eğer `HEAD~1` yoksa (ilk commit):
```bash
git -C ~/YouTubeAITeam diff --cached --name-only
```

### 2. Değişen Dosyaları Sınıflandır

| Dosya tipi | Wiki davranışı |
|------------|---------------|
| `agents.py` | `Agents.md` sayfasını güncelle |
| `main.py` | `Pipeline.md` sayfasını güncelle |
| `state.py` | `AgentState.md` sayfasını güncelle |
| `output.py` | `OutputLayer.md` sayfasını güncelle |
| `requirements.txt` | `Dependencies.md` sayfasını güncelle |
| Yeni `.py` dosyası | Yeni PascalCase wiki sayfası oluştur |
| `docs/wiki/*.md` | Atla (wiki kendi kendini güncellemiyor) |

### 3. Her Değişen Modül İçin

1. İlgili wiki sayfasını oku (`docs/wiki/<ModuleName>.md`). Yoksa yeni oluştur.
2. Diff çıktısını analiz et:
   - **Eklenen fonksiyon/sınıf** → Yeni bölüm ekle
   - **Değişen mantık** → Mevcut bölümü güncelle, `[GÜNCELLEME: tarih]` tag'i ekle
   - **Silinen kod** → `[KALDIRILDI]` olarak işaretle, silme
3. Wiki-schema formatını koru:

```markdown
**Özet:** [Modülün güncel işlevi, max 3 cümle]
**Kütüphaneler/Teknolojiler:** [Kullanılan kütüphaneler]
**Bağlantılar:** [[İlgiliSayfa1]], [[İlgiliSayfa2]]

## Fonksiyonlar / Sınıflar

### `ClassName` veya `function_name()`
[Kısa açıklama — diff'ten türetilmiş]

## Son Değişiklik
- `YYYY-MM-DD`: [Ne değişti, neden önemli]
```

### 4. Index.md Güncelle

Yeni sayfa oluşturduysan `docs/wiki/Index.md`'ye ekle:
```markdown
- [[YeniSayfa]] — tek satır özet
```

### 5. Özet Rapor Ver

Kullanıcıya kısa bir özet sun:
```
✅ Güncellendi: Agents.md (ResearcherAgent navigasyon filtresi eklendi)
✅ Oluşturuldu: OutputLayer.md
⏭️  Atlandı: docs/wiki/Videos.md (wiki dosyası)
```

---

## Özel Durumlar

**`agents.py` değişirse:**
- Her `Agent` sınıfı için ayrı bölüm yaz
- `__init__` parametrelerini (model adı, temperature) belgele
- `run()` metodunun `state` girdisi ve çıktısını göster

**`main.py` değişirse:**
- LangGraph node bağlantılarını güncelle
- Conditional edge mantığını açıkla

**`requirements.txt` değişirse:**
- Eklenen/çıkarılan paketi ve neden eklendiğini kaydet

---

## Referanslar

- Wiki format kuralları: `docs/skills/wiki-schema/SKILL.md`
- Mevcut wiki durumu: `docs/wiki/Index.md`
- Agent tanımları: `AGENTS.md`
