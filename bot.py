"""Gemini API ile konuşmayı yürüten katman.

Arayüz (app.py) burayı yalnızca iki fonksiyon üzerinden kullanır:
istemci_olustur() ve cevap_uret(). Böylece Streamlit kodu ile API kodu
birbirine karışmaz; modeli ya da sağlayıcıyı değiştirmek gerekirse
sadece bu dosyaya dokunulur.
"""

import os

from google import genai
from google.genai import errors, types

# Hızlı ve ücretsiz katmanda kullanılabilen güncel model.
MODEL = "gemini-2.5-flash"


class BotHatasi(Exception):
    """Kullanıcıya olduğu gibi gösterilebilecek, anlaşılır hata mesajı taşır.

    Amaç, API'den gelen teknik hataları ekrana ham hâliyle basmak yerine
    kullanıcının ne yapması gerektiğini söyleyen bir cümleye çevirmek.
    """


def istemci_olustur():
    """API anahtarını ortam değişkeninden okuyup Gemini istemcisini kurar."""
    anahtar = os.getenv("GOOGLE_API_KEY", "").strip()
    if not anahtar:
        raise BotHatasi(
            "GOOGLE_API_KEY bulunamadı. Proje klasöründeki .env.example dosyasını "
            ".env adıyla kopyalayıp kendi anahtarını yazman gerekiyor."
        )
    return genai.Client(api_key=anahtar)


def _gecmisi_cevir(gecmis):
    """Arayüzdeki mesaj listesini Gemini'nin beklediği biçime çevirir.

    Bizim tarafta roller "user" / "assistant", Gemini tarafında ise
    "user" / "model" olarak geçiyor; tek fark bu.
    """
    return [
        types.Content(
            role="user" if mesaj["rol"] == "user" else "model",
            parts=[types.Part(text=mesaj["metin"])],
        )
        for mesaj in gecmis
    ]


def cevap_uret(istemci, gecmis, sistem_talimati):
    """Konuşmanın tamamını modele gönderip cevabı metin olarak döndürür.

    Geçmişin tamamı her istekte yeniden gönderilir; botun önceki mesajları
    "hatırlamasının" tek sebebi bu. Model kendi başına bir şey saklamaz.
    """
    try:
        yanit = istemci.models.generate_content(
            model=MODEL,
            contents=_gecmisi_cevir(gecmis),
            config=types.GenerateContentConfig(
                system_instruction=sistem_talimati,
                temperature=0.8,
            ),
        )
    except errors.ClientError as hata:
        if hata.code == 429:
            raise BotHatasi(
                "İstek sınırına takıldın. Bir dakika bekleyip tekrar dene."
            ) from hata
        if hata.code in (400, 401, 403):
            raise BotHatasi(
                "API anahtarı geçersiz ya da yetkisiz görünüyor. "
                ".env dosyasındaki GOOGLE_API_KEY değerini kontrol et."
            ) from hata
        raise BotHatasi(
            f"İstek reddedildi (kod {hata.code}). Mesajı değiştirip tekrar deneyebilirsin."
        ) from hata
    except errors.ServerError as hata:
        raise BotHatasi(
            "Google tarafında geçici bir sorun var. Birazdan tekrar dene."
        ) from hata
    except Exception as hata:
        raise BotHatasi(
            "Modele bağlanılamadı. İnternet bağlantını kontrol edip tekrar dene."
        ) from hata

    metin = (yanit.text or "").strip()
    if not metin:
        # Güvenlik filtreleri devreye girdiğinde cevap boş dönebiliyor.
        raise BotHatasi(
            "Model bu mesaja cevap üretmedi. Soruyu farklı biçimde sormayı dene."
        )
    return metin
