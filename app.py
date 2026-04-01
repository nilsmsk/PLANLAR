import streamlit as st
import pandas as pd
import os
from datetime import datetime, time

st.set_page_config(page_title="Bizim Planlar", page_icon="🗓️", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; }
    .plan-kart { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .countdown-text { color: #ff4b4b; font-weight: bold; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🗓️ 7 Kişilik Dev Kadro: Plan Panosu")

# 1. KİMLİK BÖLÜMÜ
st.info("💡 Önce ismini yaz, sonra butonlarla plana katıl!")
kullanici_adi = st.text_input("Sen Kimsin?:", placeholder="Örn: MERVE").strip().upper()

DOSYA = "planlar.csv"
# Sütunlara 'Saat' eklendi
if not os.path.exists(DOSYA):
    pd.DataFrame(columns=["Kim", "Plan", "Tarih", "Saat", "Katilanlar"]).to_csv(DOSYA, index=False)

df = pd.read_csv(DOSYA)
df['Katilanlar'] = df['Katilanlar'].fillna('').astype(str)
if 'Saat' not in df.columns: df['Saat'] = "12:00"

# --- SIRALAMA VE ZAMAN HESABI ---
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
        col1, col2 = st.columns(2)
        with col1: p_kim = st.text_input("Ekleyen Kim?").upper()
        with col2: p_adi = st.text_input("Plan Ne?").upper()
        
        col3, col4 = st.columns(2)
        with col3: p_tarih = st.date_input("Hangi Gün?")
        with col4: p_saat = st.time_input("Saat Kaçta?", value=time(19, 0)) # Varsayılan 19:00
        
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
for index, row in df.iterrows():
    p_zaman = row['Tam_Zaman']
    gecmis = row['Gecmis_Mi']
    
    # Geri sayım hesaplama
    kalan = p_zaman - simdi
    gun = kalan.days
    saat, mikro = divmod(kalan.seconds, 3600)
    dakika, _ = divmod(mikro, 60)
    
    plan_metni = f"~~{row['Plan']}~~" if gecmis else f"**{row['Plan']}**"
    
    with st.container():
        col_bilgi, col_katilanlar, col_butonlar = st.columns([3, 2, 2])
        
        with col_bilgi:
            durum = "❌" if gecmis else "🟢"
            st.markdown(f"{durum} {plan_metni}")
            st.markdown(f"📅 {row['Tarih']} | ⏰ {row['Saat']}  \n👤 Ekleyen: {row['Kim']}")
            
            # Geri sayımı buraya ekliyoruz
            if not gecmis:
                if gun > 0:
                    st.markdown(f"<p class='countdown-text'>⏳ Son {gun} gün, {saat} saat!</p>", unsafe_allow_html=True)
                elif saat > 0 or dakika > 0:
                    st.markdown(f"<p class='countdown-text'>🔥 ÇOK AZ KALDI: {saat} saat, {dakika} dk!</p>", unsafe_allow_html=True)
                else:
                    st.markdown("<p class='countdown-text'>🚀 ŞİMDİ BAŞLIYOR!</p>", unsafe_allow_html=True)
        
        with col_katilanlar:
            katilan_listesi = [x.strip().upper() for x in str(row['Katilanlar']).split(",") if x.strip()]
            katilan_listesi.sort()
            st.markdown("**👥 Katılanlar:**")
            if katilan_listesi:
                st.markdown("\n".join([f"- {isim}" for isim in katilan_listesi]))
            else:
                st.caption("Henüz kimse yok")

        with col_butonlar:
            if not gecmis:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Katıl", key=f"in_{index}"):
                        if kullanici_adi and kullanici_adi not in katilan_listesi:
                            katilan_listesi.append(kullanici_adi)
                            df.at[index, 'Katilanlar'] = ", ".join(katilan_listesi)
                            df.to_csv(DOSYA, index=False, columns=["Kim", "Plan", "Tarih", "Saat", "Katilanlar"])
                            st.rerun()
                with c2:
                    if st.button("❌ Ayrıl", key=f"out_{index}"):
                        if kullanici_adi in katilan_listesi:
                            katilan_listesi.remove(kullanici_adi)
                            df.at[index, 'Katilanlar'] = ", ".join(katilan_listesi)
                            df.to_csv(DOSYA, index=False, columns=["Kim", "Plan", "Tarih", "Saat", "Katilanlar"])
                            st.rerun()
            
            if st.button("🗑️ Planı Sil", key=f"del_{index}"):
                df = df.drop(index)
                df.to_csv(DOSYA, index=False, columns=["Kim", "Plan", "Tarih", "Saat", "Katilanlar"])
                st.rerun()
        st.divider()
