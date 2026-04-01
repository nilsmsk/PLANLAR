import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Bizim Planlar", page_icon="🗓️", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; }
    .plan-kart { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🗓️ 7 Kişilik Dev Kadro: Plan Panosu")

# 1. KİMLİK BÖLÜMÜ
st.info("💡 Önce ismini yaz, sonra planlardaki butonlara tek tıkla katıl veya ayrıl!")
kullanici_adi = st.text_input("Sen Kimsin? (Butonları kullanmak için önce burayı doldur):", placeholder="Örn: Merve")

DOSYA = "planlar.csv"
if not os.path.exists(DOSYA):
    pd.DataFrame(columns=["Kim", "Plan", "Tarih", "Katilanlar"]).to_csv(DOSYA, index=False)

df = pd.read_csv(DOSYA)
df['Katilanlar'] = df['Katilanlar'].fillna('').astype(str)

# --- AKILLI SIRALAMA MANTIĞI ---
# Gelecek planları en üste, geçmiş planları en alta iter ve kendi içlerinde tarihe göre sıralar
bugun_dt = pd.to_datetime('today').normalize()
df['Tarih_Gecici'] = pd.to_datetime(df['Tarih'], errors='coerce')
df['Gecmis_Mi'] = df['Tarih_Gecici'] < bugun_dt
df = df.sort_values(by=['Gecmis_Mi', 'Tarih']).drop(columns=['Tarih_Gecici', 'Gecmis_Mi']).reset_index(drop=True)

# --- YENİ PLAN EKLEME ---
with st.expander("➕ Yeni Plan Oluştur"):
    with st.form("yeni_plan", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1: p_kim = st.text_input("Ekleyen Kim?")
        with col2: p_adi = st.text_input("Plan Ne?")
        with col3: p_tarih = st.date_input("Tarih?")
        if st.form_submit_button("Sisteme Ekle"):
            if p_kim and p_adi:
                yeni = pd.DataFrame([{"Kim": p_kim, "Plan": p_adi, "Tarih": p_tarih, "Katilanlar": p_kim}])
                df = pd.concat([df, yeni], ignore_index=True)
                
                # Yeni plan eklenince de listeyi tekrar düzgünce sıralayıp kaydet
                df['Tarih_Gecici'] = pd.to_datetime(df['Tarih'], errors='coerce')
                df['Gecmis_Mi'] = df['Tarih_Gecici'] < bugun_dt
                df = df.sort_values(by=['Gecmis_Mi', 'Tarih']).drop(columns=['Tarih_Gecici', 'Gecmis_Mi']).reset_index(drop=True)
                
                df.to_csv(DOSYA, index=False)
                st.rerun()

st.divider()

# --- PLAN LİSTESİ VE BUTONLAR ---
bugun = datetime.today().date()

for index, row in df.iterrows():
    try:
        p_tarih = datetime.strptime(str(row['Tarih']), "%Y-%m-%d").date()
    except:
        p_tarih = bugun
    
    gecmis = p_tarih < bugun
    plan_metni = f"~~{row['Plan']}~~" if gecmis else f"**{row['Plan']}**"
    tarih_metni = f"~~{row['Tarih']}~~" if gecmis else f"{row['Tarih']}"
    
    # Kart Tasarımı
    with st.container():
        col_bilgi, col_katil, col_ayril, col_sil = st.columns([4, 1.5, 1.5, 1])
        
        with col_bilgi:
            durum = "❌" if gecmis else "🟢"
            st.markdown(f"{durum} {plan_metni}  \n📅 {tarih_metni} | 👤 {row['Kim']}")
            st.caption(f"👥 Katılanlar: {row['Katilanlar']}")
        
        if not gecmis:
            with col_katil:
                if st.button("✅ Katıl", key=f"in_{index}"):
                    if kullanici_adi:
                        liste = [x.strip() for x in row['Katilanlar'].split(",") if x.strip()]
                        if kullanici_adi not in liste:
                            liste.append(kullanici_adi)
                            df.at[index, 'Katilanlar'] = ", ".join(liste)
                            df.to_csv(DOSYA, index=False)
                            st.rerun()
                    else: st.warning("İsim yaz!")
            
            with col_ayril:
                if st.button("❌ Ayrıl", key=f"out_{index}"):
                    if kullanici_adi:
                        liste = [x.strip() for x in row['Katilanlar'].split(",") if x.strip()]
                        if kullanici_adi in liste:
                            liste.remove(kullanici_adi)
                            df.at[index, 'Katilanlar'] = ", ".join(liste)
                            df.to_csv(DOSYA, index=False)
                            st.rerun()
        
        with col_sil:
            if st.button("🗑️", key=f"del_{index}", help="Planı sil"):
                df = df.drop(index)
                df.to_csv(DOSYA, index=False)
                st.rerun()
        st.divider()
