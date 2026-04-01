import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Bizim Planlar", page_icon="🗓️")

st.title("🗓️ 7 Kişilik Dev Kadro: Plan Panosu")

DOSYA = "planlar.csv"

# Veri tabanını yükle veya oluştur
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
tablo_gorseli = "| Durum | Kim | Plan | Tarih | Katılanlar |\n|---|---|---|---|---|\n"
tum_planlar_listesi = [] # Silme ve Katılma menüleri için

for index, row in df.iterrows():
    try:
        plan_tarihi = datetime.strptime(str(row['Tarih']), "%Y-%m-%d").date()
    except:
        plan_tarihi = bugun
        
    plan_etiketi = f"{row['Plan']} ({row['Tarih']})"
    tum_planlar_listesi.append(plan_etiketi)

    if plan_tarihi < bugun:
        tablo_gorseli += f"| ❌ Geçmiş | ~~{row['Kim']}~~ | ~~{row['Plan']}~~ | ~~{row['Tarih']}~~ | ~~{row['Katilanlar']}~~ |\n"
    else:
        tablo_gorseli += f"| 🟢 Yaklaşan | **{row['Kim']}** | **{row['Plan']}** | {row['Tarih']} | {row['Katilanlar']} |\n"

st.markdown(tablo_gorseli)
st.divider()

# 3. BÖLÜM: PLANA KATILMA VE MANUEL SİLME
col_katil, col_sil = st.columns(2)

with col_katil:
    st.subheader("🙋‍♀️ Plana Katıl")
    with st.form("katilma_formu", clear_on_submit=True):
        # Sadece tarihi geçmemiş olanları filtreleyebiliriz ama kafa karışmasın diye hepsini gösteriyoruz
        secilen_plan_katil = st.selectbox("Hangi plana?", tum_planlar_listesi, key="katil_select")
        katilacak_kisi = st.text_input("Adın:")
        katil_btn = st.form_submit_button("Ben de Geliyorum!")
        
        if katil_btn and katilacak_kisi:
            secilen_ad = secilen_plan_katil.rsplit(" (", 1)[0]
            for idx, r in df.iterrows():
                if r['Plan'] == secilen_ad:
                    mevcut = str(r['Katilanlar'])
                    if katilacak_kisi.lower() not in mevcut.lower():
                        df.at[idx, 'Katilanlar'] = mevcut + ", " + katilacak_kisi if mevcut else katilacak_kisi
                        df.to_csv(DOSYA, index=False)
                        st.rerun()

with col_sil:
    st.subheader("🗑️ Planı Sil")
    with st.form("silme_formu", clear_on_submit=True):
        secilen_plan_sil = st.selectbox("Silinecek planı seç:", tum_planlar_listesi, key="sil_select")
        st.write("⚠️ Bu işlem geri alınamaz.")
        sil_btn = st.form_submit_button("Seçili Planı Sil")
        
        if sil_btn:
            # Seçilen planı bul ve tablodan kaldır
            silinecek_ad = secilen_plan_sil.rsplit(" (", 1)[0]
            df = df[df['Plan'] != silinecek_ad]
            df.to_csv(DOSYA, index=False)
            st.warning("Plan silindi!")
            st.rerun()
