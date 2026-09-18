import streamlit as st
import sqlite3
import math
import urllib.request
import json
import os
from datetime import datetime

# --- DATABASE ---
conn = sqlite3.connect('hama.db', check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY, jina TEXT, simu TEXT, aina TEXT, namba_gari TEXT,
    picha_path TEXT, bei_km REAL, balance REAL DEFAULT 0, date TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY, mteja TEXT, simu_mteja TEXT,
    kutoka TEXT, kwenda TEXT, km REAL, jumla REAL, commission REAL, payout REAL,
    driver_id INTEGER, status TEXT, date TEXT)""")
conn.commit()

BEI_GARI = {
    "Bajaji / Pickup Ndogo (1200 TZS/km)": 1200,
    "Toyota Hilux (1800 TZS/km)": 1800,
    "Canter Ndogo (2500 TZS/km)": 2500,
    "Fuso Kubwa (3500 TZS/km)": 3500
}
BASE_FEE = 15000

def get_km_free(from_name, to_name):
    try:
        def geocode(q):
            url = f"https://nominatim.openstreetmap.org/search?q={q.replace(' ','%20')}, Dar es Salaam&format=json"
            req = urllib.request.Request(url, headers={'User-Agent': 'HamaSmart/1.0'})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
                if data: return float(data[0]['lat']), float(data[0]['lon'])
            return None, None
        lat1, lon1 = geocode(from_name)
        lat2, lon2 = geocode(to_name)
        if lat1 and lat2:
            url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
            with urllib.request.urlopen(url, timeout=10) as r:
                d = json.loads(r.read().decode())
                return d['routes'][0]['distance']/1000, lat1, lon1, lat2, lon2
    except:
        pass
    return 0,0,0,0,0

st.set_page_config(page_title="HAMA SMART", page_icon="🚚", layout="wide")
st.title("🚚 HAMA SMART - App ya Kuhamisha Mizigo")

menu = st.sidebar.selectbox("CHAGUA", ["Mteja - Oda Mpya", "Dereva - Jisajili", "Admin - Mapato Yangu"])

# --- MTEJA ---
if menu == "Mteja - Oda Mpya":
    st.header("Weka Oda Yako")
    c1, c2 = st.columns(2)
    mteja = c1.text_input("Jina lako")
    simu_mteja = c2.text_input("Namba ya simu ya kulipia")
    kutoka = c1.text_input("Kutoka wapi? (mf Sinza)")
    kwenda = c2.text_input("Kwenda wapi? (mf Mbezi)")
    aina_chaguo = st.selectbox("Chagua aina ya gari unayohitaji", list(BEI_GARI.keys()))

    if st.button("Pima Umbali na Bei"):
        if kutoka and kwenda:
            with st.spinner("Inapima barabara kwa OpenStreetMap..."):
                km, lat1, lon1, lat2, lon2 = get_km_free(kutoka, kwenda)
                if km == 0: # fallback
                    km = st.number_input("Andika KM kutoka Google Maps (kama net ni mbovu)", 1.0, 500.0, 12.0)
                else:
                    st.success(f"Umbali halisi: {km:.2f} KM")
                    st.markdown(f"[Angalia barabara kwenye Maps](https://www.google.com/maps/dir/{lat1},{lon1}/{lat2},{lon2})")

                bei_km = BEI_GARI[aina_chaguo]
                jumla = km * bei_km + BASE_FEE
                st.session_state['km'] = km
                st.session_state['jumla'] = jumla
                st.session_state['from'] = kutoka
                st.session_state['to'] = kwenda
                st.session_state['aina'] = aina_chaguo
                st.session_state['mteja'] = mteja
                st.session_state['simu_mteja'] = simu_mteja

                st.metric("JUMLA YA KULIPA", f"{jumla:,.0f} TZS", f"{km:.1f} km x {bei_km} + {BASE_FEE} base")
        else:
            st.warning("Jaza sehemu zote")

    if 'jumla' in st.session_state:
        if st.button(f"LIPA {st.session_state['jumla']:,.0f} TZS KWA M-PESA/TIGO"):
            jumla = st.session_state['jumla']
            commission = jumla * 0.15
            payout = jumla * 0.85
            c.execute("INSERT INTO orders (mteja, simu_mteja, kutoka, kwenda, km, jumla, commission, payout, status, date) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (st.session_state['mteja'], st.session_state['simu_mteja'], st.session_state['from'], st.session_state['to'], st.session_state['km'], jumla, commission, payout, 'paid', str(datetime.now())))
            conn.commit()
            st.balloons()
            st.success(f"✅ Malipo yamepokelewa! Dereva atakujia sasa. Oda #{c.lastrowid}")
            # Onyesha madereva
            c.execute("SELECT jina, namba_gari, picha_path FROM drivers WHERE aina=?", (st.session_state['aina'],))
            for d in c.fetchall():
                st.write(f"Dereva: {d[0]} - {d[1]}")
                if d[2] and os.path.exists(d[2]): st.image(d[2], width=200)

# --- DEREVA ---
elif menu == "Dereva - Jisajili":
    st.header("Jisajili Kama Dereva")
    jina = st.text_input("Jina kamili")
    simu = st.text_input("Namba ya simu")
    namba_gari = st.text_input("Namba ya gari (T123 ABC)")
    aina = st.selectbox("Aina ya gari lako", list(BEI_GARI.keys()))
    picha = st.file_uploader("Pakia Picha ya Gari lako", type=['jpg','png','jpeg'])

    if st.button("Jisajili"):
        path = ""
        if picha:
            os.makedirs("picha_za_magari", exist_ok=True)
            path = f"picha_za_magari/{namba_gari}_{picha.name}"
            with open(path, "wb") as f: f.write(picha.getbuffer())
        c.execute("INSERT INTO drivers (jina, simu, aina, namba_gari, picha_path, bei_km, date) VALUES (?,?,?,?,?,?,?)",
                  (jina, simu, aina, namba_gari, path, BEI_GARI[aina], str(datetime.now())))
        conn.commit()
        st.success(f"Umesajiliwa! {jina} - {aina}. Wateja watakuona sasa.")
        if path: st.image(path, width=300)

    st.subheader("Madereva Waliopo")
    c.execute("SELECT jina, simu, aina, namba_gari, picha_path, balance FROM drivers")
    for d in c.fetchall():
        col1, col2 = st.columns([1,2])
        if d[4] and os.path.exists(d[4]): col1.image(d[4], width=150)
        col2.write(f"**{d[0]}** | {d[2]} | {d[3]} | {d[1]}\nBalance: {d[5]:,.0f} TZS")

# --- ADMIN ---
else:
    st.header("Dashboard Yako (Mmiliki)")
    c.execute("SELECT SUM(commission), SUM(jumla), COUNT(*) FROM orders WHERE status='paid'")
    com, total, count = c.fetchone()
    com = com or 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Faida Yako (15%)", f"{com:,.0f} TZS")
    c2.metric("Mauzo Jumla", f"{(total or 0):,.0f} TZS")
    c3.metric("Oda Zilizolipwa", f"{count or 0}")

    st.subheader("Oda Zote")
    c.execute("SELECT id, mteja, kutoka, kwenda, km, jumla, date FROM orders ORDER BY id DESC")
    st.dataframe(c.fetchall(), use_container_width=True)