import streamlit as st
import sqlite3, os, json, urllib.request, pandas as pd
from datetime import datetime

st.set_page_config(page_title="HAMA SMART", page_icon="🚚", layout="centered")

NMB_ACCOUNT_NUMBER = "22810064566"
NMB_ACCOUNT_NAME = "AZIZI FRENK MOHAMEDI"
COMMISSION_RATE = 0.05
BASE_FEE = 15000
AINA_ZA_MAGARI = ["Bajaji / Pickup Ndogo", "Toyota Hilux", "Canter Ndogo", "Fuso Kubwa"]

conn = sqlite3.connect('hama.db', check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS drivers (id INTEGER PRIMARY KEY, jina TEXT, simu TEXT, aina TEXT, namba_gari TEXT, picha_path TEXT, bei_km REAL, rating REAL, trips INTEGER, date TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, mteja TEXT, simu_mteja TEXT, kutoka TEXT, kwenda TEXT, km REAL, jumla REAL, commission REAL, payout REAL, driver_id INTEGER, status TEXT, date TEXT)")
conn.commit()

def get_km(a,b):
    try:
        def geocode(q):
            url=f"https://nominatim.openstreetmap.org/search?q={q.replace(' ','%20')}, Tanzania&format=json"
            req=urllib.request.Request(url, headers={'User-Agent':'HamaSmart/1.0'})
            with urllib.request.urlopen(req, timeout=10) as r:
                d=json.loads(r.read().decode())
                if d: return float(d[0]['lat']), float(d[0]['lon'])
            return None,None
        lat1,lon1=geocode(a); lat2,lon2=geocode(b)
        if lat1 and lat2:
            url=f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
            with urllib.request.urlopen(url, timeout=10) as r:
                d=json.loads(r.read().decode()); return d['routes'][0]['distance']/1000
    except: pass
    return 0

# --- DESIGN KAMA PICHA YAKO ---
st.markdown("""
<style>
div[data-testid="stImage"] {text-align: center;}
.orange-header {background:#FF6B00; padding:15px; border-radius:15px 15px 0 0; color:white; text-align:left}
.orange-header h2 {margin:0; color:white}
.card {background:white; border-radius:12px; padding:12px; box-shadow:0 2px 8px rgba(0,0,0,0.1); margin-bottom:10px; border:1px solid #eee; color:black}
.book-btn {background:#FF6B00; color:white; border-radius:8px; padding:6px 18px; font-weight:bold; border:none}
.stButton>button {background:#FF6B00; color:white; border-radius:10px; height:3em; font-weight:bold; width:100%}
</style>
""", unsafe_allow_html=True)

# LOGO
try:
    st.image("Hama smart.jpg", use_container_width=True)
except:
    st.image("logo.png", use_container_width=True)

try:
    st.image("image_20260920_054207.webp", use_container_width=True)
except:
    pass

st.markdown(f'<div class="orange-header"><h2>🚚 HAMA SMART</h2><small>House Mover • Dar es Salaam | NMB {NMB_ACCOUNT_NUMBER}</small></div>', unsafe_allow_html=True)

menu = st.radio("", ["Customer Booking", "Driver List", "Driver Registration", "Live Map"], horizontal=True, label_visibility="collapsed")

if menu == "Customer Booking":
    st.markdown("### Book Your Move")
    st.caption("Reliable & fast movers at your doorstep")
    with st.container(border=True):
        st.markdown("📍 **From**")
        kutoka = st.text_input("From", placeholder="Msasani, Dar es Salaam", label_visibility="collapsed")
        st.divider()
        st.markdown("📍 **To**")
        kwenda = st.text_input("To", placeholder="Kariakoo, Dar es Salaam", label_visibility="collapsed")

    col1, col2 = st.columns(2)
    with col1:
        move_date = st.date_input("Move Date")
    with col2:
        load_size = st.selectbox("Load Size", ["1 Bedroom", "2 Bedroom", "Few Items", "Full House"])

    if st.button("Get Quotes - TAFUTA BEI"):
        km = get_km(kutoka, kwenda)
        if km==0: km = st.number_input("Weka KM", 1.0, 500.0, 6.5)
        st.session_state['km'] = km
        st.session_state['route'] = (kutoka, kwenda)
        st.success(f"Umbali: {km:.1f} km - {len(c.execute('SELECT * FROM drivers').fetchall())} Drivers Nearby")
        st.switch_page = "Driver List" # hint

elif menu == "Driver List":
    if 'km' not in st.session_state:
        st.warning("Tafadhali anza Customer Booking kuweka From/To")
        st.stop()
    km = st.session_state['km']
    kutoka, kwenda = st.session_state['route']
    st.markdown(f"From {kutoka} → To {kwenda} • ~{km:.1f} km")
    st.markdown(f"### {len(c.execute('SELECT * FROM drivers').fetchall())} Drivers Nearby")

    c.execute("SELECT id,jina,simu,namba_gari,bei_km,rating,trips,aina FROM drivers")
    for did,jina,simu,ng,bei_km,rating,trips,aina in c.fetchall():
        jumla = km*bei_km + BASE_FEE
        if rating is None: rating=4.8
        if trips is None: trips=100
        with st.container(border=True):
            col1, col2, col3 = st.columns([1,2,1])
            with col1:
                st.markdown("🧑‍✈️")
            with col2:
                st.markdown(f"**{jina}**")
                st.caption(f"⭐ {rating} • ({trips} trips)")
                st.caption(f"{aina}")
                st.markdown(f"**{bei_km:,.0f} TZS / km**")
                st.caption(f"ETA 5 min • Msasani")
            with col3:
                if st.button("Book", key=f"book_{did}"):
                    st.session_state['selected'] = (did,jina,simu,jumla,km)

    if 'selected' in st.session_state:
        did,jina,simu,jumla,km = st.session_state['selected']
        st.divider()
        st.error(f"LIPA KAMILI {jumla:,.0f} TZS KWA NMB {NMB_ACCOUNT_NUMBER}")
        kiasi = st.number_input("Kiasi Ulicholipa (TZS)", 0, value=0, step=1000)
        ref = st.text_input("Reference NMB")
        if st.button("THIBITISHA MALIPO ✅"):
            if kiasi < jumla:
                st.error(f"❌ HAIRUHUSIWI NUSU! Takiwa {jumla:,.0f} umeweka {kiasi:,.0f}. Pungufu {jumla-kiasi:,.0f}")
            elif not ref:
                st.error("Weka Reference")
            else:
                c.execute("INSERT INTO orders (mteja,simu_mteja,kutoka,kwenda,km,jumla,commission,payout,driver_id,status,date) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                          ("Mteja", "07...", kutoka, kwenda, km, jumla, jumla*0.05, jumla*0.95, did, f"paid_{ref}", str(datetime.now())))
                conn.commit()
                st.balloons()
                st.success(f"Oda imethibitishwa! Dereva {jina} anakuja")
                st.link_button(f"WhatsApp {jina}", f"https://wa.me/255{simu[-9:]}")

elif menu == "Driver Registration":
    st.markdown("### Driver Registration")
    st.caption("Set your rate & start earning")
    jina=st.text_input("Full Name", placeholder="John Mwakinyo")
    simu=st.text_input("Phone Number", placeholder="+255 712 345 678")
    aina=st.selectbox("Vehicle Type", AINA_ZA_MAGARI)
    bei=st.number_input("Price per km (TZS)", 500, 10000, 1200, 50)
    st.caption(f"Recommended: 1100-1500 TZS/km")
    area=st.text_input("Operating Area", value="Dar es Salaam")
    avail=st.toggle("Available for bookings", value=True)
    picha=st.file_uploader("Picha ya Gari", type=['jpg','png','jpeg'])
    if st.button("Register as Driver"):
        path=""
        if picha:
            os.makedirs("picha_za_magari", exist_ok=True)
            path=f"picha_za_magari/{picha.name}"
            open(path,"wb").write(picha.getbuffer())
        c.execute("INSERT INTO drivers (jina,simu,aina,namba_gari,picha_path,bei_km,rating,trips,date) VALUES (?,?,?,?,?,?,?,?)",
                  (jina,simu,aina,"T123",path,bei,4.8,0,str(datetime.now())))
        conn.commit()
        st.success(f"Hongera {jina}! Umejisajili kwa {bei:,} TZS/km")

else: # Live Map
    st.markdown("### 📦 Fuatilia Mzigo LIVE")
    track = st.text_input("Weka Namba ya Oda")
    if track or True:
        prog = st.slider("Safari", 0, 100, 50)
        lat_cur = -6.7924 + (prog/100)*0.5
        lon_cur = 39.2083 + (prog/100)*0.5
        st.map(pd.DataFrame([{"lat":lat_cur,"lon":lon_cur}]), zoom=11)
        st.link_button("🗺️ Fungua Google Maps", f"https://maps.google.com/?q={lat_cur},{lon_cur}")
        st.metric("Gari Lipo", f"{prog}%", "Njiani")
