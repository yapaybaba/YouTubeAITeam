**Özet:** `watch-youtube` CLI, YouTube videolarını storyboard JPEG'lerine dönüştürüp Vision LLM ile analiz eden bir pipeline. Transcript yoksa 30 saniyelik aralıklarla sentetik timestamp'ler üretiyor; keyword store'u TF-IDF ile kendi kendine öğrenerek güncelliyor.
**Kütüphaneler/Teknolojiler:** yt-dlp, ffmpeg, spaCy, Pillow, scikit-learn (TF-IDF), Groq Whisper API
**Bağlantılar:** [[WatchYoutubeKurulum]], [[ClaudeDesignAjans]], [[SentetikTimestamp]]

## Pipeline Adımları

1. **Transcript İndir** — yt-dlp ile VTT/SRT; başarısız olursa Groq Whisper; her ikisi de yoksa sentetik 30s intervallar
2. **Akıllı Timestamp Çıkar** — spaCy keyword eşleştirme (Rule A) + sessizlik boşluğu tespiti (Rule B)
3. **Frame Çıkar** — ffmpeg ile seçilen timestamp'lerde kare al
4. **Storyboard Derle** — Pillow ile grid layout; adaptif çözünürlük (720–1280px)

## Sentetik Timestamp Fallback

Transcript indirme 429 (Rate Limit) alırsa pipeline durmaz:
- `downloader.py`: `DownloadError` yakalanıp `(None, "none")` döndürülür
- `main.py`: Boş entries + `synthetic` source varsa video süresinden 30s aralıklarla timestamp üretilir

## Keyword Store (Kendi Kendine Öğrenme)

- `data/keyword_store.json` içinde saklanır
- Her video sonrası TF-IDF ile yeni keyword adayları çıkarılır
- Bigram threshold: 0.05 | Unigram threshold: 0.15
- 3+ görülme sonrası ağırlık 0.8'e çıkar ("promote")

## Grid Boyutları

| Frame | Grid | Cell |
|-------|------|------|
| 1 | 1×1 | 1280px |
| 3–4 | 2×2 | 960px |
| 7–9 | 3×3 | 720px |
| 13+ | 3×3 (çok sayfalı) | 720px |
