import streamlit as st
import sqlite3, os, pandas as pd
from datetime import datetime

st.set_page_config(page_title="HAMA SMART", page_icon="🚚", layout="centered")

NMB = "22810064566"
NAME = "AZIZI FRENK MOHAMEDI"
BASE_FEE = 15000

conn = sqlite3.connect('hama.db', check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS drivers (id INTEGER PRIMARY KEY, jina TEXT, simu TEXT, aina TEXT, bei REAL)")
c.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, mteja TEXT, jumla REAL, status TEXT)")
conn.commit()

st.markdown("""
<style>
.orange {background:#FF6B00; padding:18px; border-radius:15px; color:white; text-align:center; margin-bottom:15px}
.orange h1 {color:white; margin:0}
.card {background:white; padding:12px; border-radius:12px; border:1px solid #eee; margin-bottom:10px; color:black}
.stButton>button {background:#FF6B00; color:white; border-radius:12px; height:50px; font-weight:bold; width:100%}
</style>
""", unsafe_allow_html=True)

# LOGO - TENGENEZWA NA CODE, SI PICHA
st.markdown("""
<div class="orange">
<h1>🚚 HAMA SMART</h1>
<p>House Mover • Dar es Salaam</p>
<p style="font-size:12px">NMB: 22810064566 - AZIZI FRENK MOHAMEDI</p>
</div>
""", unsafe_allow_html=True)

menu = st.selectbox("CHAGUA HUDUMA", ["🚚 Customer Booking", "📋 Driver List", "🧑‍✈️ Driver Registration", "📦 LIVE Map - Fuatilia", "💰 Admin"])

if menu == "🚚 Customer Booking":
    st.subheader("Book Your Move")
    st.caption("Reliable & fast movers at your doorstep")
    
    col1, col2 = st.columns(2)
    with col1:
        kutoka = st.text_input("From", placeholder="Msasani")
    with col2:
        kwenda = st.text_input("To", placeholder="Kariakoo")
    
    col3, col4 = st.columns(2)
    with col3:
        tarehe = st.date_input("Move Date")
    with col4:
        size = st.selectbox("Load Size", ["1 Bedroom", "2 Bedroom", "Few Items"])
    
    km = st.number_input("KM (Weka kama hujui)", 1.0, 500.0, 6.5)
    
    if st.button("Get Quotes"):
        st.session_state['km'] = km
        st.session_state['route'] = (kutoka, kwenda)
        st.success(f"Umbali {km} KM - Madereva 3 wapo karibu")

    if 'km' in st.session_state:
        km = st.session_state['km']
        c.execute("SELECT id,jina,bei FROM drivers")
        drivers = c.fetchall()
        if not drivers:
            st.info("Hakuna dereva bado. Jisajili kwanza kama dereva.")
        for did, jina, bei in drivers:
            jumla = km*bei + BASE_FEE
            with st.container(border=True):
                st.markdown(f"**{jina}** ⭐ 4.8 (124 trips)")
                st.markdown(f"Isuzu Truck • 2 Ton")
                st.markdown(f"**{bei:,.0f} TZS / km** - Jumla: **{jumla:,.0f}**")
                if st.button(f"Book {jina}", key=f"b{did}"):
                    st.session_state['sel'] = (jina, jumla)

    if 'sel' in st.session_state:
        jina, jumla = st.session_state['sel']
        st.divider()
        st.error(f"LIPA KAMILI {jumla:,.0f} TZS NMB {NMB}")
        kiasi = st.number_input("Kiasi ULICHOLIPA", 0, step=1000)
        ref = st.text_input("Reference NMB")
        if st.button("THIBITISHA ✅"):
            if kiasi < jumla:
                st.error(f"❌ NUSU HAIRUHUSIWI! Unatakiwa {jumla:,.0f}, umeweka {kiasi:,.0f}. Bado {jumla-kiasi:,.0f}")
            elif not ref:
                st.error("Weka Reference")
            else:
                st.balloons()
                st.success(f"✅ IMELIPIWA KAMILI! Dereva {jina} anakuja. Ref: {ref}")

elif menu == "📋 Driver List":
    st.subheader("3 Drivers Nearby")
    c.execute("SELECT jina,bei FROM drivers")
    for jina, bei in c.fetchall():
        with st.container(border=True):
            st.write(f"**{jina}** | {bei:,.0f} TZS/km | ETA 5 min")
            st.button(f"Book", key=f"dl{jina}")

elif menu == "🧑‍✈️ Driver Registration":
    st.subheader("Become a Driver Partner")
    jina = st.text_input("Full Name", placeholder="John Mwakinyo")
    simu = st.text_input("Phone Number", placeholder="0712 345 678")
    aina = st.selectbox("Vehicle Type", ["Isuzu Truck • 2 Ton", "Canter • 1.5 Ton", "Hino • 3 Ton", "Bajaji / Pickup"])
    bei = st.number_input("Price per km (TZS)", 500, 10000, 1200)
    st.caption("Recommended: 1100-1500 TZS/km")
    area = st.text_input("Operating Area", value="Dar es Salaam")
    if st.button("Register as Driver"):
        c.execute("INSERT INTO drivers (jina, simu, aina, bei) VALUES (?,?,?,?)",(jina, simu, aina, bei))
        conn.commit()
        st.success(f"Hongera {jina}! Bei {bei:,} imesajiliwa. Sasa upo kwenye list.")

elif menu == "📦 LIVE Map - Fuatilia":
    st.subheader("Fuatilia Mzigo LIVE")
    prog = st.slider("Safari %", 0, 100, 50)
    lat = -6.7924 + prog/100*0.5
    lon = 39.2083 + prog/100*0.5
    st.map(pd.DataFrame([{"lat":lat,"lon":lon}]), zoom=11)
    st.metric("Gari", f"{prog}% njiani")
    st.link_button("🗺️ Google Maps", f"https://maps.google.com/?q={lat},{lon}")

else:
    st.subheader("Admin - Faida Yangu 5%")
    st.metric("Mauzo", "0 TZS")
