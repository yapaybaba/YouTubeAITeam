# OTONOM WIKI VE MİMARİ HAFIZA KURALLARI

Bu dosya, AI'ın `docs/wiki/` klasörüne yazarken uyması gereken kuralları içerir.
Claude Code bu dosyayı okuyarak wiki sayfası oluşturur veya günceller.

---

## 1. Temel Kurallar

- `docs/wiki/` klasörü AI'ın kalıcı hafızasıdır. Sadece `.md` dosyası üret.
- ASLA kod değiştirme veya silme. Sadece analiz et ve wiki'ye yaz.
- Yeni dosya/kavram oluştururken MUTLAKA `[[köşeli parantez]]` ile Obsidian linki ver.
- Mevcut sayfa eskimişse: üzerine yazma, `[GÜNCELLEME: YYYY-MM-DD]` ile bölüm ekle.
- Belirsiz veya çelişen bilgi bulunca `[FRICTION]` bloğu ekle, üzerine yazma.

---

## 2. Codebase Wiki Sayfası Formatı

Her Python modülü / bileşen sayfasının başına zorunlu frontmatter:

```markdown
**Özet:** Modülün ne yaptığını anlatan max 3 cümle.
**Kütüphaneler/Teknolojiler:** Kullanılan kütüphaneler (örn: LangChain, spaCy).
**Bağlantılar:** [[İlgiliSayfa1]], [[İlgiliSayfa2]]
```

Sayfa gövdesi şu bölümleri içermeli:

```markdown
## `ClassName` veya `function_name()`
[Kısa açıklama — girdi/çıktı/model]

## Son Değişiklik
- `YYYY-MM-DD`: [Ne değişti, neden önemli]
```

---

## 3. YouTube Video Wiki Sayfası Formatı

`watch-youtube` skill'inin ürettiği her analiz sayfasının başına zorunlu frontmatter:

```markdown
**Özet:** Videodan öğrenilen ana fikri anlatan max 3 cümle.
**Kütüphaneler/Teknolojiler:** Videoda gösterilen araçlar.
**Bağlantılar:** [[İlgiliSayfa1]], [[İlgiliSayfa2]]
**Kaynak Video:** [Başlık](https://www.youtube.com/watch?v=VIDEO_ID) {#VIDEO_ID}
**Transcript:** vtt / whisper / synthetic
**Kare sayısı:** N kare, M storyboard sayfası
```

### Timestamp Linkleri

NLP'nin seçtiği `SmartTimestamp.time_sec` değerlerinden timestamp linki üret.
`time_sec` değerini tam sayıya yuvarla:

```markdown
## Önemli Anlar

- [0:23](https://www.youtube.com/watch?v=VIDEO_ID&t=23s) — Pipeline başlatma komutu
- [1:05](https://www.youtube.com/watch?v=VIDEO_ID&t=65s) — NLP keyword extraction
- [3:10](https://www.youtube.com/watch?v=VIDEO_ID&t=190s) — Storyboard grid çıktısı
```

**Kural:** Sadece `watch-youtube` çıktısındaki gerçek timestamp'leri kullan. Tahmin etme.

### Keyword Store Bölümü

`watch-youtube` çıktısında `Learned keyword:` satırları varsa ekle:

```markdown
## Öğrenilen Keyword'ler

Bu videodan `data/keyword_store.json`'a eklenen yeni terimler:

| Keyword | Tip | TF-IDF Lift |
|---------|-----|-------------|
| `codebase` | unigram | 0.164 |
| `contain project` | bigram | 0.128 |
```

---

## 4. Videos.md Formatı

Her video için anchor'lı kayıt:

```markdown
### [Video Başlığı](https://www.youtube.com/watch?v=VIDEO_ID) {#VIDEO_ID}
- **ID:** `VIDEO_ID`
- **Analiz tarihi:** YYYY-MM-DD
- **Transcript:** vtt / whisper / synthetic
- **Kare sayısı:** N kare, M sayfa
- **Öğrenilen keyword'ler:** N yeni terim
- **Oluşturulan wiki sayfaları:** [[Sayfa1]], [[Sayfa2]]
- **Özet:** Tek cümlelik içerik özeti.
```

`[[Videos#VIDEO_ID]]` ile doğrudan o kayda link verebilirsin.

---

## 5. Index.md Yapısı

```markdown
# Wiki Index

## Pipeline & Araçlar
- [[WatchYoutubePipeline]] — watch-youtube CLI, NLP timestamp, Whisper fallback

## Mimari & Kavramlar  
- [[LangGraphLocalLLM]] — LangGraph + Local LLM, state machine

## Proje Bileşenleri
- [[Agents]] — ResearcherAgent, CoderAgent, ReviewerAgent
- [[AgentState]] — TypedDict, veri akış tablosu

## Sistem
- [[wiki_schema]] — Bu dosya: wiki yazma kuralları

## Video Kaydı
- [[Videos]] — Analiz edilen tüm videolar
```

---

## 6. Ingest Operasyonu (CLI)

`docs/skills/ingest/ingest.py` çalıştırıldığında:

```bash
python docs/skills/ingest/ingest.py --since HEAD~1 --wiki docs/wiki
```

Değişen Python modüllerine karşılık gelen wiki sayfaları güncellenir.
Modül → Wiki eşleştirmesi: `AGENTS.md` dosyasındaki tabloya bak.
