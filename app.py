"""Yapay Zekâ Sohbet Botu — Streamlit arayüzü.

Çalıştırmak için:  streamlit run app.py asdgausyd
"""

import streamlit as st
from dotenv import load_dotenv

import bot
from karakterler import KARAKTERLER, VARSAYILAN_KARAKTER

# .env dosyasındaki API anahtarını ortam değişkenlerine yükler.
# override=True sayesinde .env'i düzenleyip sayfayı yenilemek yeterli oluyor.
load_dotenv(override=True)

st.set_page_config(
    page_title="Sohbet Botu",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded",  # yan panel hep açık başlasın
)

# Sohbet alanını okunaklı bir genişlikte tutup kullanıcı ile bot
# mesajlarını görsel olarak ayırmak için küçük bir stil düzenlemesi.
st.markdown(
    """
    <style>
      .block-container { max-width: 820px; padding-top: 3rem; }

      /* Sağ üstteki "Deploy" butonunu ve üç nokta menüsünü gizle.
         Dikkat: araç çubuğunun tamamını ([data-testid="stToolbar"])
         gizlemiyoruz; kapatılan yan paneli geri açan düğme onun içinde. */
      [data-testid="stAppDeployButton"],
      [data-testid="stMainMenu"] { display: none; }

      .stChatMessage { border-radius: 14px; padding: 0.85rem 1.1rem; }

      /* Mesajların yanındaki avatar simgelerini gizle.
         display:none kullanıyoruz; öğe DOM'da kaldığı için aşağıdaki
         :has() seçicileri kullanıcı/bot ayrımını yapmaya devam ediyor. */
      .stChatMessage [data-testid^="stChatMessageAvatar"] { display: none; }

      /* Kullanıcı: hafif renkli zemin — Bot: sade çerçeve */
      .stChatMessage:has([data-testid="stChatMessageAvatarUser"]) {
          background: #f1f4f7;
      }
      .stChatMessage:has([data-testid="stChatMessageAvatarAssistant"]) {
          background: transparent;
          border: 1px solid #e4e7eb;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def istemci_getir():
    """Gemini istemcisini bir kez kurar, sonraki çalışmalarda aynısını verir."""
    return bot.istemci_olustur()


def sohbeti_sifirla():
    """Geçmişi temizler ve seçili karakterin selamlamasıyla yeniden başlatır."""
    karakter = KARAKTERLER[st.session_state.karakter]
    st.session_state.gecmis = [{"rol": "assistant", "metin": karakter["selamlama"]}]


# Streamlit her etkileşimde betiği baştan çalıştırır. Konuşmanın kaybolmaması
# için geçmişi session_state içinde tutuyoruz.
if "karakter" not in st.session_state:
    st.session_state.karakter = VARSAYILAN_KARAKTER
if "gecmis" not in st.session_state:
    sohbeti_sifirla()


# --- Yan panel: karakter seçimi ve yeni sohbet ---------------------------

with st.sidebar:
    st.subheader("Ayarlar")
    st.selectbox(
        "Karakter",
        options=list(KARAKTERLER),
        key="karakter",
        on_change=sohbeti_sifirla,
        help="Karakteri değiştirmek sohbeti sıfırdan başlatır.",
    )
    st.caption(KARAKTERLER[st.session_state.karakter]["aciklama"])

    st.divider()
    st.button("Yeni sohbet", on_click=sohbeti_sifirla, width="stretch")


# --- Sohbet alanı --------------------------------------------------------

st.title("Yapay Zekâ Sohbet Botu")
st.caption(f"{st.session_state.karakter} · Google Gemini ile çalışıyor")

# Anahtar yoksa uygulama çökmesin; ne yapılması gerektiğini yazıp dursun.
try:
    istemci = istemci_getir()
except bot.BotHatasi as hata:
    st.error(str(hata))
    st.stop()

for mesaj in st.session_state.gecmis:
    with st.chat_message(mesaj["rol"]):
        st.markdown(mesaj["metin"])

soru = st.chat_input("Mesajını yaz...")

if soru:
    st.session_state.gecmis.append({"rol": "user", "metin": soru})
    with st.chat_message("user"):
        st.markdown(soru)

    with st.chat_message("assistant"):
        with st.spinner("Yazıyor..."):
            try:
                cevap = bot.cevap_uret(
                    istemci,
                    st.session_state.gecmis,
                    KARAKTERLER[st.session_state.karakter]["talimat"],
                )
            except bot.BotHatasi as hata:
                # Hata olursa uygulama çökmez: kullanıcının yazdığı mesaj
                # ekranda kalır, uyarıyı görüp tekrar deneyebilir.
                st.warning(str(hata))
                cevap = None

        if cevap:
            st.markdown(cevap)
            st.session_state.gecmis.append({"rol": "assistant", "metin": cevap})
