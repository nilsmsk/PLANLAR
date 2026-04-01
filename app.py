import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Bizim Planlar", page_icon="🗓️")

st.title("🗓️ 7 Kişilik Dev Kadro: Plan Panosu")

DOSYA = "planlar.csv"

# Tabloyu oluştur veya oku
if not os.path.exists(DOSYA):
    bos_tablo = pd.DataFrame(columns=["Kim", "Plan", "Tarih", "Katilanlar"])
    bos_tablo.to_csv(DOSYA, index=False)

df = pd.read_csv(DOSYA)

if "Katilanlar" not in df.columns:
    df["Katilanlar"] = ""
df['Katilanlar'] = df['Katilanlar'].fillna('')

# 1. BÖLÜM: YENİ PLAN EKLEME
with st.form("plan_formu", clear_on_submit=True):
    st.subheader("➕ Yeni Plan Ekle")
    col1, col2, col3 = st.columns(3)
    with col1:
        kim = st.text_input("Kim?")
    with col2:
        plan = st.text_input("Plan Nedir?")
    with col3:
        tarih = st.date_input("Ne Zaman?")
    
    ekle_butonu = st.form_submit_button("Plana Ekle!")

    if ekle_butonu:
        if kim and plan:
            yeni_veri = pd.DataFrame([{"Kim": kim, "Plan": plan, "Tarih": tarih, "Katilanlar": kim}])
            df = pd.concat([df, yeni_veri], ignore_index=True)
            df.to_csv(DOSYA, index=False)
            st.success("Plan eklendi!")
            st.rerun()
        else:
            st.warning("Lütfen isim ve plan kısımlarını doldur.")

st.divider()

# 2. BÖLÜM: TABLO GÖRÜNÜMÜ
st.subheader("📌 Güncel Planlarımız")

bugun = datetime.today().date()

# Tabloyu şık bir şekilde oluşturuyoruz
tablo_gorseli = "| Durum | Kim | Plan | Tarih | Katılanlar |\n|---|---|---|---|---|\n"

gelecek_planlar = [] # Katılma menüsü için liste

for index, row in df.iterrows():
    try:
        plan_tarihi = datetime.strptime(str(row['Tarih']), "%Y-%m-%d").date()
    except:
        plan_tarihi = bugun
        
    if plan_tarihi < bugun:
        # GEÇMİŞ PLANLAR (Üstü çizili)
        tablo_gorseli += f"| ❌ Geçmiş | ~~{row['Kim']}~~ | ~~{row['Plan']}~~ | ~~{row['Tarih']}~~ | ~~{row['Katilanlar']}~~ |\n"
    else:
        # GELECEK PLANLAR
        tablo_gorseli += f"| 🟢 Yaklaşan | **{row['Kim']}** | **{row['Plan']}** | {row['Tarih']} | {row['Katilanlar']} |\n"
        gelecek_planlar.append(f"{row['Plan']} ({row['Tarih']})")

# Tabloyu ekrana yansıt
st.markdown(tablo_gorseli)

st.divider()

# 3. BÖLÜM: PLANA KATILMA BUTONU
if gelecek_planlar:
    st.subheader("🙋‍♀️ Bir Plana Katıl")
    with st.form("katilma_formu", clear_on_submit=True):
        secilen_plan_metni = st.selectbox("Hangi plana katılıyorsun?", gelecek_planlar)
        katilacak_kisi = st.text_input("Senin Adın:")
        katil_btn = st.form_submit_button("Ben de Geliyorum!")
        
        if katil_btn:
            if katilacak_kisi:
                # Seçilen planı ayıkla
                secilen_plan_adi = secilen_plan_metni.rsplit(" (", 1)[0]
                
                # Tabloda o planı bul ve günvelle
                for index, row in df.iterrows():
                    if row['Plan'] == secilen_plan_adi:
                        mevcut = str(row['Katilanlar'])
                        if katilacak_kisi.lower() not in mevcut.lower():
                            yeni_liste = mevcut + ", " + katilacak_kisi if mevcut else katilacak_kisi
                            df.at[index, 'Katilanlar'] = yeni_liste
                            df.to_csv(DOSYA, index=False)
                            st.success("Plana katıldın!")
                            st.rerun()
                        else:
                            st.warning("Adın zaten bu listede var!")
            else:
                st.warning("Lütfen adını yaz.")
