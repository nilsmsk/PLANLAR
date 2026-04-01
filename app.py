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

# --- YTÜ AMBLEM BÖLÜMÜ ---
col_bos1, col_logo, col_bos3 = st.columns([1, 0.8, 1])
with col_logo:
    # YTÜ Resmi Logosu
    st.image("https://upload.wikimedia.org/wikipedia/tr/b/be/Y%C4%B1ld%C4%B1z_Teknik_%C3%9Cniversitesi_Logosu.png", use_container_width=True)

st.title("🗓️ 7 Kişilik Dev Kadro: Plan Panosu")

# 1. KİMLİK BÖLÜMÜ
st.info("💡 Önce ismini yaz, sonra butonlarla plana katıl!")
kullanici_adi = st.text_input("Sen Kimsin?:", placeholder="Örn: MERVE").strip().upper()

DOSYA = "planlar.csv"
if not os.path.exists(DOSYA):
    pd.DataFrame(columns=["Kim", "Plan", "Tarih", "Katilanlar"]).to_csv(DOSYA, index=False)

df = pd.read_csv(DOSYA)
df['Katilanlar'] = df['Katilanlar'].fillna('').astype(str)

# --- SIRALAMA MANTIĞI ---
bugun_dt = pd.to_datetime('today').normalize()
df['Tarih_Gecici'] = pd.to_datetime(df['Tarih'], errors='coerce')
df['Gecmis_Mi'] = df['Tarih_Gecici'] < bugun_dt
df = df.sort_values(by=['Gecmis_Mi', 'Tarih']).drop(columns=['Tarih_Gecici', 'Gecmis_Mi']).reset_index(drop=True)

# --- YENİ PLAN EKLEME ---
with st.expander("➕ Yeni Plan Oluştur"):
    with st.form("yeni_plan", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1: p_kim = st.text_input("Ekleyen Kim?").upper()
        with col2: p_adi = st.text_input("Plan Ne?").upper()
        with col3: p_tarih = st.date_input("Tarih?")
        if st.form_submit_button("Sisteme Ekle"):
            if p_kim and p_adi:
                yeni = pd.DataFrame([{"Kim": p_kim, "Plan": p_adi, "Tarih": p_tarih, "Katilanlar": p_kim}])
                df = pd.concat([df, yeni], ignore_index=True)
                df.to_csv(DOSYA, index=False)
                st.rerun()

st.divider()

# --- PLAN LİSTESİ ---
bugun = datetime.today().date()

for index, row in df.iterrows():
    try:
        p_tarih = datetime.strptime(str(row['Tarih']), "%Y-%m-%d").date()
    except:
        p_tarih = bugun
    
    gecmis = p_tarih < bugun
    plan_metni = f"~~{row['Plan']}~~" if gecmis else f"**{row['Plan']}**"
    tarih_metni = f"~~{row['Tarih']}~~" if gecmis else f"{row['Tarih']}"
    
    katilan_listesi = [x.strip().upper() for x in row['Katilanlar'].split(",") if x.strip()]
    katilan_listesi.sort()
    katilanlar_alt_alta = "\n".join([f"- {isim}" for isim in katilan_listesi])

    with st.container():
        col_bilgi, col_katilanlar, col_butonlar = st.columns([3, 2, 2])
        
        with col_bilgi:
            durum = "❌" if gecmis else "🟢"
            st.markdown(f"{durum} {plan_metni}  \n📅 {tarih_metni}  \n👤 Ekleyen: {row['Kim']}")
        
        with col_katilanlar:
            st.markdown("**👥 Katılanlar:**")
            if katilanlar_alt_alta:
                st.markdown(katilanlar_alt_alta)
            else:
                st.caption("Henüz kimse yok")

        with col_butonlar:
            if not gecmis:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Katıl", key=f"in_{index}"):
                        if kullanici_adi:
                            if kullanici_adi not in katilan_listesi:
                                katilan_listesi.append(kullanici_adi)
                                df.at[index, 'Katilanlar'] = ", ".join(katilan_listesi)
                                df.to_csv(DOSYA, index=False)
                                st.rerun()
                        else: st.warning("İsim yaz!")
                with c2:
                    if st.button("❌ Ayrıl", key=f"out_{index}"):
                        if kullanici_adi and kullanici_adi in katilan_listesi:
                            katilan_listesi.remove(kullanici_adi)
                            df.at[index, 'Katilanlar'] = ", ".join(katilan_listesi)
                            df.to_csv(DOSYA, index=False)
                            st.rerun()
            
            if st.button("🗑️ Planı Sil", key=f"del_{index}"):
                df = df.drop(index)
                df.to_csv(DOSYA, index=False)
                st.rerun()
        st.divider()
