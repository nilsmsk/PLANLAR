import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime, time

st.set_page_config(page_title="Bizim Planlar", page_icon="🗓️", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; }
    .countdown-text { color: #ff4b4b; font-weight: bold; font-size: 0.9rem; }
    .kader-alani { background-color: #f0f2f6; padding: 20px; border-radius: 15px; border: 2px dashed #ff4b4b; margin-top: 30px;}
    </style>
    """, unsafe_allow_html=True)

st.title("🗓️ 7 Kişilik Dev Kadro: Plan Panosu")

# 1. KİMLİK BÖLÜMÜ
st.info("💡 Önce ismini yaz, sonra butonlarla plana katıl!")
kullanici_adi = st.text_input("Sen Kimsin?:", placeholder="ÖRN: MERVE").strip().upper()

DOSYA = "planlar.csv"
if not os.path.exists(DOSYA):
    pd.DataFrame(columns=["Kim", "Plan", "Tarih", "Saat", "Katilanlar"]).to_csv(DOSYA, index=False)

df = pd.read_csv(DOSYA)
df['Katilanlar'] = df['Katilanlar'].fillna('').astype(str)
if 'Saat' not in df.columns: 
    df['Saat'] = "19:00"

# --- ZAMAN VE SIRALAMA ---
simdi = datetime.now()
def zaman_hesapla(row):
    try:
        dt_str = f"{row['Tarih']} {row['Saat']}"
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    except: 
        return simdi

df['Tam_Zaman'] = df.apply(zaman_hesapla, axis=1)
df['Gecmis_Mi'] = df['Tam_Zaman'] < simdi
df = df.sort_values(by=['Gecmis_Mi', 'Tam_Zaman']).reset_index(drop=True)

# --- YENİ PLAN EKLEME ---
with st.expander("➕ Yeni Plan Oluştur"):
    with st.form("yeni_plan", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: p_kim = st.text_input("Ekleyen Kim?").upper()
        with c2: p_adi = st.text_input("Plan Ne?").upper()
        
        c3, c4 = st.columns(2)
        with c3: p_tarih = st.date_input("Hangi Gün?")
        with c4: p_saat = st.time_input("Saat?", value=time(19, 0)) 
        
        if st.form_submit_button("Sisteme Ekle"):
            if p_kim and p_adi:
                yeni = pd.DataFrame([{
                    "Kim": p_kim, 
                    "Plan": p_adi, 
                    "Tarih": p_tarih.strftime("%Y-%m-%d"), 
                    "Saat": p_saat.strftime("%H:%M"), 
                    "Katilanlar": p_kim
                }])
                df = pd.concat([df, yeni], ignore_index=True)
                df.to_csv(DOSYA, index=False, columns=["Kim", "Plan", "Tarih", "Saat", "Katilanlar"])
                st.rerun()

st.divider()

# --- PLAN LİSTESİ ---
komik_mesajlar = [
    "Tarkan gibi şımarma, erken gel!", 
    "Lvbel C5 modu açıldı, ortam fena olacak!", 
    "Mükremin Gezgin bile bu plana düşerdi!",
    "Biri 'Beni Yak Kendini Yak' mı dedi?",
    "Hadi bakalım, sahalara dönüyoruz!"
]

for index, row in df.iterrows():
    p_zaman = row['Tam_Zaman']
    gecmis = row['Gecmis_Mi']
    kalan = p_zaman - simdi
    
    with st.container():
        col_bilgi, col_katilanlar, col_butonlar = st.columns([3, 2, 2])
        
        with col_bilgi:
            durum = "❌" if gecmis else "🟢"
            st.markdown(f"{durum} **{row['Plan']}** \n📅 {row['Tarih']} | ⏰ {row['Saat']} | 👤 {row['Kim']}")
            if not gecmis:
                st.markdown(f"<p class='countdown-text'>⏳ Son {kalan.days} gün, {kalan.seconds//3600} saat!</p>", unsafe_allow_html=True)
        
        with col_katilanlar:
            katilanlar = [x.strip().upper() for x in str(row['Katilanlar']).split(",") if x.strip()]
            katilanlar.sort()
            st.markdown("**👥 Katılanlar:**")
            st.markdown("\n".join([f"- {i}" for i in katilanlar]) if katilanlar else "Henüz kimse yok")

        with col_butonlar:
            if not gecmis:
                btn1, btn2 = st.columns(2)
                with btn1:
                    if st.button("✅ Katıl", key=f"in_{index}"):
                        if kullanici_adi:
                            if kullanici_adi not in katilanlar:
                                katilanlar.append(kullanici_adi)
                                df.at[index, 'Katilanlar'] = ", ".join(katilanlar)
                                df.to_csv(DOSYA, index=False, columns=["Kim", "Plan", "Tarih", "Saat", "Katilanlar"])
                                st.toast(random.choice(komik_mesajlar))
                                st.rerun()
                        else:
                            st.warning("Önce ismini yaz!")
                with btn2:
                    if st.button("❌ Ayrıl", key=f"out_{index}"):
                        if kullanici_adi and kullanici_adi in katilanlar:
                            katilanlar.remove(kullanici_adi)
                            df.at[index, 'Katilanlar'] = ", ".join(katilanlar)
                            df.to_csv(DOSYA, index=False, columns=["Kim", "Plan", "Tarih", "Saat", "Katilanlar"])
                            st.rerun()
            
            if st.button("🗑️ Sil", key=f"del_{index}"):
                df = df.drop(index)
                df.to_csv(DOSYA, index=False, columns=["Kim", "Plan", "Tarih", "Saat", "Katilanlar"])
                st.rerun()
        st.divider()

# --- 4. ÖZELLİK:  KARAR VAKTİ ---
st.markdown("<div class='kader-alani'>", unsafe_allow_html=True)
st.subheader("🎡 KARAR VAKTİ")

c1, c2 = st.columns([2, 1])
with c1:
    soru = st.selectbox("Çözülmesi gereken diferansiyel denklem (Karar konusu):", 
                      ["Hesabı kim ödeyecek?", "Nereye gidelim?", "Günün fotoğrafçısı kim olsun?"])
with c2:
    st.write("") 
    st.write("")
    if st.button("🎰 KADERİ BELİRLE"):
        tum_kisiler = set()
        for k in df['Katilanlar']:
            for isim in k.split(","):
                if isim.strip(): tum_kisiler.add(isim.strip().upper())
        
        if tum_kisiler:
            secilen = random.choice(list(tum_kisiler))
            st.snow() 
            st.error(f"🎯 ANALİZ SONUCU: **{secilen}**")
            st.caption(f"Nümerik verilere göre '{soru}' sorusunun cevabı kesinlikle budur.")
        else:
            st.warning("Listede hiç kimse yok!")
st.markdown("</div>", unsafe_allow_html=True)
