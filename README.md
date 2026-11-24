# Yapay Zekâ Sohbet Botu

Google Gemini API'sini kullanan, tarayıcıda çalışan bir sohbet botu.
Kullanıcı mesaj yazar, program konuşmanın tamamını seçili karakterin
talimatıyla birlikte modele gönderir, gelen cevap ekranda görünür.
Bot konuşma boyunca önceki mesajları hatırlar.

Kulüp örnek projesidir; kod bilerek sade tutulmuştur...

## Kurulum

1. Depoyu indir ve klasöre gir:

   ```bash
   git clone <repo-linki>
   cd Chat-Bot
   ```

2. Sanal ortam oluştur ve etkinleştir:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   source .venv/bin/activate   # macOS / Linux
   ```

3. Gereken paketleri kur:

   ```bash
   pip install -r requirements.txt
   ```

4. API anahtarını ayarla. `.env.example` dosyasını `.env` adıyla kopyala
   ve içine kendi anahtarını yaz:

   ```
   GOOGLE_API_KEY=senin_anahtarin
   ```

   Anahtarı ücretsiz olarak [Google AI Studio](https://aistudio.google.com/apikey)
   üzerinden alabilirsin.

5. Çalıştır:

   ```bash
   streamlit run app.py
   ```

   Tarayıcıda `http://localhost:8501` açılır.

## Dosyalar

| Dosya | Ne yapar |
|---|---|
| `app.py` | Streamlit arayüzü: sohbet alanı, mesaj kutusu, yan panel |
| `bot.py` | Gemini API çağrısı ve hata yönetimi |
| `karakterler.py` | Karakterlerin system prompt'ları |
| `.streamlit/config.toml` | Arayüz teması |
| `.env` | API anahtarı (repoya **girmez**) |
| `NOTLAR.md` | Projeyi yaparken tutulan notlar |

## Özellikler

- Konuşma geçmişini hatırlar ("Adım Ali" dedikten sonra "Adım neydi?" sorusuna doğru cevap verir)
- 4 hazır karakter; her biri botun üslubunu değiştirir
- Yeni sohbet butonu geçmişi temizler
- Cevap beklenirken "Yazıyor..." göstergesi
- Anahtar veya bağlantı sorununda uygulama çökmez, anlaşılır bir uyarı gösterir

## Yeni karakter eklemek

`karakterler.py` içindeki `KARAKTERLER` sözlüğüne bir madde ekle:

```python
"Meraklı Araştırmacı": {
    "aciklama": "Her cevabın ardından bir soru sorar.",
    "selamlama": "Merhaba! Bugün neyi kurcalıyoruz?",
    "talimat": "Sen meraklı bir araştırmacısın. ...",
},
```

Arayüz listeyi otomatik olarak okur, başka bir yeri değiştirmek gerekmez.

## Not

`.env` dosyası `.gitignore` içindedir. API anahtarını hiçbir zaman
GitHub'a yükleme; anahtar herkese açık bir repoda görünürse iptal et
ve yenisini oluştur.
