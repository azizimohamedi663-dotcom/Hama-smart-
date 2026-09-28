import streamlit as st
import sqlite3, pandas as pd, random, math, folium
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(page_title="HAMA SMART APP", page_icon="🚌", layout="wide")

# ===== LOGO YA NJANO - RUDISHWA =====
st.markdown('''
<div style="background:linear-gradient(135deg,#FF6B00,#FF8C00); padding:25px; border-radius:20px; text-align:center; color:white; margin-bottom:20px; box-shadow:0 8px 20px rgba(255,107,0,0.4);">
<h1 style="margin:0; font-size:38px; font-weight:900; letter-spacing:1px;">HAMA SMART APP</h1>
<p style="margin:8px 0 0 0; font-size:16px; opacity:0.95;">Dereva Anaweka Bei | Maoni | Live Map | Wallet</p>
</div>
''', unsafe_allow_html=True)

# ===== INSTALL BUTTON - SALAMA SASA - HAINA ERROR =====
st.markdown('''
<div id="hama-install" style="background:linear-gradient(135deg,#FF6B00,#FF8C00); color:white; padding:18px; border-radius:20px; text-align:center; border:2px solid white; box-shadow:0 10px 30px rgba(0,0,0,0.3); margin-bottom:20px;">
<div style="font-size:20px; font-weight:900;">📲 INSTALL HAMA APP</div>
<div style="font-size:13px; margin-top:5px;">Weka HAMA kwenye simu kama WhatsApp - Bure!</div>
<button onclick="alert('Android: Bofya ⋮ juu kulia > Install app \\n iPhone: Share > Add to Home Screen')" style="background:white; color:#FF6B00; border:none; padding:12px 35px; border-radius:25px; font-weight:900; margin-top:12px; font-size:16px; cursor:pointer;">INSTALL SASA</button>
<div style="font-size:11px; margin-top:8px; opacity:0.7; cursor:pointer;" onclick="this.parentElement.style.display='none'">Funga X</div>
</div>
''', unsafe_allow_html=True)

NMB_ACC = "22810064566"
BASE_FEE = 15000

BEI_CONFIG = {
    "Pikipiki": {"bei": 8000, "max_kg": 50},
    "Bajaji": {"bei": 12000, "max_kg": 300},
    "Pickup Small": {"bei": 18000, "max_kg": 1000},
    "Fuso Small": {"bei": 25000, "max_kg": 3500},
    "Fuso Big": {"bei": 35000, "max_kg": 10000},
}

VITUO_COORDS = {
    "Kariakoo": (-6.8291, 39.2683), "Posta": (-6.8166, 39.2883), "Ubungo": (-6.79, 39.205),
    "Mbagala": (-6.9176, 39.2736), "Tegeta": (-6.72, 39.16), "Mbezi": (-6.75, 39.15),
    "Kimara": (-6.78, 39.17), "Kigamboni": (-6.81, 39.34), "Msasani": (-6.75, 39.27),
    "Sinza": (-6.775, 39.20), "Manzese": (-6.80, 39.23), "Tabata": (-6.85, 39.22),
    "Chanika": (-6.95, 39.10), "Bunju": (-6.70, 39.18), "Ilala": (-6.83, 39.25),
    "Temeke": (-6.87, 39.28), "Kinondoni": (-6.77, 39.25)
}
VITUO = list(VITUO_COORDS.keys())

conn = sqlite3.connect('hama_v69.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS drivers (
 id INTEGER PRIMARY KEY, jina TEXT, simu TEXT, aina TEXT, bei REAL,
 nida TEXT, gari TEXT, namba_gari TEXT, kituo TEXT, leseni TEXT,
 status TEXT DEFAULT 'Inahakikiwa', lat REAL, lng REAL)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders (
 id TEXT PRIMARY KEY, mteja_name TEXT, mteja_phone TEXT, mzigo TEXT, kg REAL,
 from_kituo TEXT, to_kituo TEXT, driver_id INTEGER, driver_name TEXT,
 driver_phone TEXT, bei REAL, jumla REAL, status TEXT, time TEXT,
 mteja_lat REAL, mteja_lng REAL)''')
conn.commit()

def gen_id():
    return "HAMA" + str(random.randint(10000,99999))

def calc_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R*2*math.asin(math.sqrt(a))

menu = st.sidebar.radio("MENU", ["Mteja - Tuma Mzigo", "Dereva - Sajili", "Dereva - Wallet Oda Zangu", "Ramani LIVE", "Admin"])

if menu == "Mteja - Tuma Mzigo":
    st.header("Tuma Mzigo")
    b_name = st.text_input("Jina lako")
    b_phone = st.text_input("Simu yako")
    b_kg = st.number_input("Uzito kg", min_value=1, value=100)
    b_mzigo = st.selectbox("Aina ya Mzigo", list(BEI_CONFIG.keys()))
    b_from = st.selectbox("Kutoka", VITUO)
    b_to = st.selectbox("Kwenda", VITUO)
    drivers = pd.read_sql("SELECT * FROM drivers WHERE status='Approved'", conn)
    if drivers.empty:
        st.warning("Hakuna dereva aliyethibitishwa")
    else:
        df_s = drivers.copy()
        df_s['label'] = df_s['jina'] + " | " + df_s['namba_gari'] + " | " + df_s['bei'].astype(str)
        sel_label = st.selectbox("Chagua Dereva", df_s['label'])
        sel_row = df_s[df_s['label']==sel_label].iloc[0]
        lat1, lon1 = VITUO_COORDS[b_from]
        lat2, lon2 = VITUO_COORDS[b_to]
        dist = calc_distance(lat1, lon1, lat2, lon2)
        jumla = dist * float(sel_row['bei']) + BASE_FEE
        st.success(f"Jumla TZS {jumla:,.0f}")
        if st.button("TUMA ODA KWA DEREVA", use_container_width=True):
            if not b_name or not b_phone:
                st.error("Jaza jina na simu")
            else:
                m_lat = lat1 + random.uniform(-0.01, 0.01)
                m_lng = lon1 + random.uniform(-0.01, 0.01)
                order_id = gen_id()
                c.execute("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (order_id, b_name, b_phone, b_mzigo, b_kg, b_from, b_to, int(sel_row['id']), sel_row['jina'], sel_row['simu'], float(sel_row['bei']), jumla, "Inasubiri Dereva", datetime.now().strftime("%Y-%m-%d %H:%M"), m_lat, m_lng))
                conn.commit()
                st.balloons()
                st.success(f"Oda {order_id} imetumwa kwa {sel_row['jina']}")

elif menu == "Dereva - Sajili":
    st.header("Sajili Dereva")
    with st.form("sajili"):
        jina = st.text_input("Jina Kamili")
        simu = st.text_input("Simu")
        nida = st.text_input("NIDA")
        aina = st.selectbox("Aina ya Gari", list(BEI_CONFIG.keys()))
        gari = st.text_input("Model")
        namba_gari = st.text_input("Namba ya Gari")
        leseni = st.text_input("Leseni")
        kituo = st.selectbox("Kituo", VITUO)
        bei = st.number_input("Bei kwa km", value=8000)
        btn = st.form_submit_button("TUMA KWA ADMIN")
        if btn:
            if not jina or not simu or not nida or not namba_gari:
                st.error("Jaza Jina, Simu, NIDA na Namba ya Gari")
            else:
                lat, lng = VITUO_COORDS[kituo]
                c.execute("INSERT INTO drivers (jina,simu,aina,bei,nida,gari,namba_gari,kituo,leseni,status,lat,lng) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (jina, simu, aina, bei, nida, gari, namba_gari, kituo, leseni, 'Inahakikiwa', lat+random.uniform(-0.02,0.02), lng+random.uniform(-0.02,0.02)))
                conn.commit()
                st.success("Umesajiliwa - Subiri Admin")

elif menu == "Dereva - Wallet Oda Zangu":
    st.header("Oda Zangu")
    simu = st.text_input("Ingiza Simu yako")
    if simu:
        drv = pd.read_sql("SELECT * FROM drivers WHERE simu=?", conn, params=(simu,))
        if drv.empty:
            st.error("Hujasajiliwa")
        else:
            d = drv.iloc[0]
            st.info(f"Karibu {d['jina']} - {d['namba_gari']} - NIDA {d['nida']}")
            orders = pd.read_sql("SELECT * FROM orders WHERE driver_id=?", conn, params=(int(d['id']),))
            for _, o in orders.iterrows():
                with st.container(border=True):
                    st.write(f"{o['id']} - {o['mzigo']} - {o['status']}")
                    if st.button(f"Kubali {o['id']}", key=o['id']):
                        c.execute("UPDATE orders SET status='Imekubaliwa' WHERE id=?", (o['id'],))
                        conn.commit()
                        st.rerun()

elif menu == "Ramani LIVE":
    st.header("Ramani LIVE")
    m = folium.Map(location=[-6.82, 39.26], zoom_start=11)
    for _, d in pd.read_sql("SELECT * FROM drivers WHERE status='Approved'", conn).iterrows():
        folium.Marker([d['lat'], d['lng']], tooltip=f"{d['jina']} {d['namba_gari']}", icon=folium.Icon(color='orange')).add_to(m)
    for _, o in pd.read_sql("SELECT * FROM orders", conn).iterrows():
        folium.Marker([o['mteja_lat'], o['mteja_lng']], tooltip=f"Oda {o['id']}", icon=folium.Icon(color='red')).add_to(m)
    st_folium(m, width=800, height=500)

elif menu == "Admin":
    pw = st.text_input("Password", type="password")
    if pw == "hama123":
        drivers = pd.read_sql("SELECT * FROM drivers", conn)
        st.dataframe(drivers[["id","jina","simu","nida","gari","namba_gari","leseni","status"]], use_container_width=True)
        for _, d in drivers.iterrows():
            with st.expander(f"{d['jina']} - {d['namba_gari']} - NIDA {d['nida']}"):
                c1, c2, c3 = st.columns(3)
                if c1.button("Kubali", key=f"ok_{d['id']}"):
                    c.execute("UPDATE drivers SET status='Approved' WHERE id=?", (d['id'],))
                    conn.commit()
                    st.rerun()
                if c2.button("Kataa", key=f"no_{d['id']}"):
                    c.execute("UPDATE drivers SET status='Rejected' WHERE id=?", (d['id'],))
                    conn.commit()
                    st.rerun()
                if c3.button("Futa", key=f"del_{d['id']}"):
                    c.execute("DELETE FROM drivers WHERE id=?", (d['id'],))
                    conn.commit()
                    st.rerun()
        st.dataframe(pd.read_sql("SELECT * FROM orders", conn), use_container_width=True)
