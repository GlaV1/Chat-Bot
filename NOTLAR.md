# Proje Notları

Projeyi yaparken tuttuğum notlar: ne öğrendim, nerede takıldım, nasıl çözdüm.
Yönergede istenen "notlar" kısmı bu dosya.
asdasdasdasdasdasd
---

## 1. Model aslında hiçbir şey hatırlamıyor

Başta "bot önceki mesajları hatırlasın" maddesini okuyunca modelde bir
hafıza ayarı olduğunu sandım. Öyle değilmiş. Model her isteği sıfırdan
görüyor; "hatırlama" tamamen bizim tarafımızda oluyor.

Yaptığım şey: her mesajda konuşmanın **tamamını** baştan gönderiyorum
(`bot.py` → `cevap_uret`). Yani 10. mesajda 10 mesajın hepsi tekrar gidiyor.

Bunun iki sonucu var:
- Sohbet uzadıkça her istek büyüyor, maliyet ve gecikme artıyor.
- Çok uzun sohbetlerde modelin bağlam sınırına takılırsın. Gerçek bir
  üründe eski mesajları özetleyip kısaltmak gerekir; bu proje için gerek yok.

## 2. Hangi kütüphane? (burada vakit kaybettim)

Gemini'nin Python kütüphanesinin iki ayrı sürümü var ve internetteki
örneklerin çoğu eskisini kullanıyor:

- `google-generativeai` → eski
- `google-genai` → güncel olan, `from google import genai`

Eski örnekten kopyaladığım kod `import` satırında patladı. Güncel olanı
kurup (`pip install google-genai`) dokümana bakınca düzeldi. Ders: kütüphane
adıyla `import` satırı birbirine benzemiyorsa, önce hangi sürümde olduğunu
kontrol et.

## 3. Streamlit her etkileşimde dosyayı baştan çalıştırıyor

Bu en şaşırtıcı kısımdı. Butona bastığında ya da mesaj yazdığında Streamlit
`app.py`'yi yukarıdan aşağı **tekrar** çalıştırıyor. Yani normal bir listede
tuttuğun konuşma her seferinde sıfırlanıyor.

Çözüm `st.session_state`. Oraya koyduğun şey yeniden çalışmalar arasında
yaşıyor:

```python
if "gecmis" not in st.session_state:
    sohbeti_sifirla()
```

Baştaki `if` önemli — onsuz her çalışmada geçmişi tekrar sıfırlardı.

## 4. Rol isimleri farklı: "assistant" ve "model"

Streamlit'in `st.chat_message()` fonksiyonu `"user"` / `"assistant"`
bekliyor. Gemini ise `"user"` / `"model"` istiyor. İkisini karıştırınca
API hata verdi.

Her yerde dönüştürmek yerine tek bir yere koydum: `bot.py` içindeki
`_gecmisi_cevir()`. Arayüz kendi isimlendirmesini kullanıyor, çeviri
sadece API'ye giderken bir kez yapılıyor.

## 5. Kullanıcı ve bot balonları aynı görünüyordu

Yönerge "mesajlar görsel olarak ayrı olsun" diyor ama Streamlit ikisini de
aynı stille çiziyor, sadece avatar farklı. Tarayıcıda incele (F12) ile
baktığımda avatarların `data-testid` özniteliği taşıdığını gördüm ve CSS'te
`:has()` ile balonu avatarına göre seçtim:

```css
.stChatMessage:has([data-testid="stChatMessageAvatarUser"]) { ... }
```

Ayrıca temayı `.streamlit/config.toml` içinde `light` olarak sabitledim.
Yoksa koyu tema kullanan birinde açık renk zemin + beyaz yazı okunmuyordu.

## 6. `use_container_width` uyarı verdi

`st.button(..., use_container_width=True)` yazınca kullanımdan kaldırıldığı
uyarısı geldi. Yenisi `width="stretch"` imiş. Streamlit sık sürüm
değiştirdiği için `requirements.txt` içine `streamlit>=1.50` yazdım.

## 7. Cevabın boş gelebildiğini fark etmemiştim

Güvenlik filtreleri devreye girdiğinde `yanit.text` boş ya da `None`
dönebiliyor. İlk hâlinde bu durumda ekrana bomboş bir balon çıkıyordu.
Şimdi boş cevabı da bir hata gibi ele alıp kullanıcıya "soruyu farklı
biçimde sor" diyorum.

## 8. Hataları kullanıcıya ham hâliyle göstermemek

İnterneti kapatıp denediğimde ekrana upuzun bir Python hata yığını
basıldı. Bunun yerine `bot.py` içinde kendi `BotHatasi` sınıfımı yazdım.
API'den gelen teknik hatayı yakalayıp kullanıcının anlayacağı bir cümleye
çeviriyorum:

- 429 → "İstek sınırına takıldın, bir dakika bekle"
- 401/403 → "Anahtar geçersiz, .env dosyasını kontrol et"
- bağlantı hatası → "İnternet bağlantını kontrol et"

Arayüz tarafı sadece `BotHatasi` yakalıyor, ne olduğuyla ilgilenmiyor.

Bir de şunu düzelttim: ilk yazdığımda hata olunca kullanıcının mesajını
geçmişten siliyordum. Denerken fark ettim ki bu, kişiyi yazdığını baştan
yazmaya zorluyor. Şimdi mesaj ekranda kalıyor, altında uyarı çıkıyor.

## 9. API anahtarı

Anahtarı doğrudan kodun içine yazmak en kolayı ama repoya öyle girerse
herkes görür. `python-dotenv` ile `.env` dosyasından okuyorum, `.env`'i de
ilk iş `.gitignore`'a ekledim. Repoda sadece `.env.example` var — içinde
anahtar yok, sadece hangi değişkenin gerektiğini gösteriyor.

Not: `.gitignore`'u sonradan eklersen dosya zaten takip edilmeye
başlanmışsa işe yaramıyor. Önce ekle.

---

## Sonraki adımlar (bu projede yapmadım)

- Cevabı akış hâlinde (streaming) kelime kelime yazdırmak
- Sohbeti dosyaya kaydedip sonra geri yüklemek
- Uzun sohbetlerde eski mesajları özetleyerek kısaltmak
