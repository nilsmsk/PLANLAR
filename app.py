import streamlit as st
import pandas as pd
import os

# Sayfa ayarları
st.set_page_config(page_title="Bizim Planlar", page_icon="🗓️")

st.title("Planın nedir? ")
st.write("Kim, nerede, ne zaman?")

# Veri dosyamızın adı (Hafıza)
DOSYA = "planlar.csv"

# Eğer hafıza dosyası yoksa, boş bir tablo oluştur
if not os.path.exists(DOSYA):
    bos_tablo = pd.DataFrame(columns=["Kim", "Plan", "Tarih"])
    bos_tablo.to_csv(DOSYA, index=False)

# Tabloyu oku
df = pd.read_csv(DOSYA)

# Yeni plan ekleme kutucukları
with st.form("plan_formu", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        kim = st.text_input("Kim?")
    with col2:
        plan = st.text_input("Plan Nedir?")
    with col3:
        tarih = st.date_input("Ne Zaman?")
    
    ekle_butonu = st.form_submit_button("Plana Ekle!")

    # Butona basıldığında yapılacaklar
    if ekle_butonu:
        if kim and plan:
            yeni_veri = pd.DataFrame([{"Kim": kim, "Plan": plan, "Tarih": tarih}])
            df = pd.concat([df, yeni_veri], ignore_index=True)
            df.to_csv(DOSYA, index=False)
            st.success("Plan başarıyla eklendi!")
            st.rerun()
        else:
            st.warning("Lütfen isim ve plan kısımlarını doldur.")

# Güncel planları göster
st.subheader("📌 Güncel Planlarımız")
st.dataframe(df, use_container_width=True, hide_index=True)
