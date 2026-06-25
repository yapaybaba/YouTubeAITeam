**Özet:** `watch-youtube` CLI, YouTube altyazısını NLP ile analiz edip sadece önemli anlarda kare çeken, bunları Vision LLM'e sıkıştıran bir pipeline. Token maliyetini %80'in üzerinde düşürüyor; transcript yoksa Groq Whisper ile audio'dan üretiyor.
**Kütüphaneler/Teknolojiler:** yt-dlp, ffmpeg, spaCy, Pillow, scikit-learn (TF-IDF), Groq Whisper API (`whisper-large-v3-turbo`)
**Bağlantılar:** [[LangGraphLocalLLM]], [[PythonMimarisi]], [[SentetikTimestamp]]

## Pipeline Adımları

1. **Transcript İndir** — yt-dlp ile VTT/SRT; YouTube 429 verirse Groq Whisper (audio indir → `/openai/v1/audio/transcriptions`); her ikisi de yoksa sentetik 30s intervallar
2. **Akıllı Timestamp Çıkar** — spaCy keyword eşleştirme (Rule A) + sessizlik boşluğu tespiti (Rule B)
3. **Frame Çıkar** — ffmpeg ile seçilen timestamp'lerde kare al
4. **Storyboard Derle** — Pillow ile grid layout; adaptif çözünürlük (720–1280px)
5. **Vision LLM Analizi** — Claude Code storyboard'u okur, wiki sayfası yazar

## Akıllı Timestamp Mantığı (Transcript'ten)

> "Altyazıyı NLP ile analiz edip sadece ve sadece ekranda önemli bir şey olduğu anlarda fotoğraf çeken ve bunları akıllıya sıkıştıran bir pipeline."

- **Rule A:** `pipeline`, `terminal`, `diagram`, `code`, `chart` gibi deictic keyword'ler
- **Rule B:** Konuşmacının susdugu sessizlik boşlukları (diyagram geçişleri, slayt değişimleri)

## Whisper Entegrasyonu

Groq API dict-tabanlı segment döndürür — `seg.text` değil `seg["text"]` kullanılmalı:

```python
raw = seg["text"] if isinstance(seg, dict) else seg.text
start = seg["start"] if isinstance(seg, dict) else seg.start
```

## Sentetik Timestamp Fallback

429 → `(None, "none")` → `main.py`'de video süresine göre 30s intervallar:

```python
timestamps = [SmartTimestamp(time_sec=float(t), ...) for t in range(30, int(duration), 30)]
```

## Keyword Store (Kendi Kendine Öğrenme)

TF-IDF ile seçilen frame çevresindeki transcript segmentlerinden yeni keyword adayı çıkarılır.
- Bigram threshold: 0.05 | Unigram threshold: 0.15 | Promote: 3+ görülme → weight 0.8
