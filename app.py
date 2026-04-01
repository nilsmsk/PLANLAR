import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Bizim Planlar", page_icon="🗓️")

st.title("🗓️ 7 Kişilik Dev Kadro: Plan Panosu")
st.write("Kim, nerede, ne zaman? Planları aşağıya ekleyin, herkes görsün!")

DOSYA = "planlar.csv"

# Tabloyu oluştur veya oku
if not os.path.exists(DOSYA):
    bos_tablo = pd.DataFrame(columns=["Kim", "Plan", "Tarih", "Katilanlar"])
    bos_tablo.to_csv(DOSYA, index=False)

df = pd.read_csv(DOSYA)

# Eski tabloyu bozmamak için güncelleme (önceki kodumuzda 'Katilanlar' sütunu yoktu)
if "Katilanlar" not in df.columns:
    df["Katilanlar"] = ""
df['Katilanlar'] = df['Katilanlar'].fillna('')

# YENİ PLAN EKLEME FORMU
with st.form("plan_formu", clear_on_submit=True):
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
            # Planı ekleyen kişi otomatik olarak katılanlara da eklenir
            yeni_veri = pd.DataFrame([{"Kim": kim, "Plan": plan, "Tarih": tarih, "Katilanlar": kim}])
            df = pd.concat([df, yeni_veri], ignore_index=True)
            df.to_csv(DOSYA, index=False)
            st.success("Plan başarıyla eklendi!")
            st.rerun()
        else:
            st.warning("Lütfen isim ve plan kısımlarını doldur.")

st.divider()
st.subheader("📌 Güncel Planlarımız")

bugun = datetime.today().date()

# Planları tek tek ekrana şık kartlar halinde yazdırıyoruz
for index, row in df.iterrows():
    try:
        plan_tarihi = datetime.strptime(str(row['Tarih']), "%Y-%m-%d").date()
    except:
        plan_tarihi = bugun # Tarih formatında hata olursa sistemi çökertmemek için
        
    if plan_tarihi < bugun:
        # 1. ÖZELLİK: GEÇMİŞ PLANLARIN ÜSTÜNÜ ÇİZ
        st.markdown(f"~~**{row['Plan']}** - {row['Tarih']} (Ekleyen: {row['Kim']})~~")
        st.caption(f"~~Katılanlar: {row['Katilanlar']}~~ *(Bu plan geçmiş)*")
        st.divider()
    else:
        # GELECEK PLANLAR VE 2. ÖZELLİK: KATILMA BUTONU
        st.markdown(f"🔥 **{row['Plan']}** - 📅 **{row['Tarih']}** (Ekleyen: {row['Kim']})")
        st.write(f"👥 **Katılanlar:** {row['Katilanlar']}")
        
        # Yan yana isim kutusu ve katılma butonu
        colA, colB = st.columns([3, 1])
        with colA:
            yeni_katilan = st.text_input("Sen de mi geliyorsun? Adını yaz:", key=f"isim_{index}")
        with colB:
            st.write("") # Butonu kutuyla hizalamak için boşluk
            st.write("")
            if st.button("Ben de Geliyorum!", key=f"btn_{index}"):
                if yeni_katilan:
                    mevcut = str(df.at[index, 'Katilanlar'])
                    # İsmi listede zaten yoksa ekle
                    if yeni_katilan.lower() not in mevcut.lower():
                        yeni_liste = mevcut + ", " + yeni_katilan if mevcut else yeni_katilan
                        df.at[index, 'Katilanlar'] = yeni_liste
                        df.to_csv(DOSYA, index=False)
                        st.rerun()
                    else:
                        st.warning("Adın zaten listede!")
                else:
                    st.warning("Lütfen önce adını yaz.")
        st.divider()
