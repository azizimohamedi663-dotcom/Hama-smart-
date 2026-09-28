import streamlit as st
from streamlit.components.v1 import html
import sqlite3, pandas as pd, random, folium, math, os, time
from streamlit_folium import st_folium
from datetime import datetime

# ===== 1. SET PAGE - MARA 1 TU =====
st.set_page_config(page_title="HAMA SMART APP", page_icon="🚌", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>#MainMenu{visibility:hidden;}footer{visibility:hidden;}header{visibility:hidden;}.stDeployButton{display:none;}</style>""", unsafe_allow_html=True)

# ===== INSTALL BUTTON =====
install_code = """
<div id="hama-install" style="position:fixed; bottom:20px; left:15px; right:15px; background:linear-gradient(135deg,#FF6B00,#FF8C00); color:white; padding:18px; border-radius:20px; text-align:center; z-index:999999; box-shadow:0 10px 30px rgba(0,0,0,0.5); border:2px solid white; font-family:sans-serif;">
<div style="font-size:20px; font-weight:900;">📲 INSTALL HAMA APP</div>
<button id="installBtn" style="background:white; color:#FF6B00; border:none; padding:12px 35px; border-radius:25px; font-weight:900; margin-top:12px; font-size:16px; cursor:pointer;">INSTALL SASA</button>
<div style="font-size:10px; margin-top:8px; opacity:0.7;" onclick="document.getElementById('hama-install').style.display='none'">Funga X</div>
</div>
<script>let deferredPrompt; window.addEventListener('beforeinstallprompt',(e)=>{e.preventDefault();deferredPrompt=e;}); document.getElementById('installBtn').addEventListener('click', async()=>{if(deferredPrompt){deferredPrompt.prompt();const{outcome}=await deferredPrompt.userChoice;if(outcome==='accepted'){document.getElementById('hama-install').style.display='none';}deferredPrompt=null;}else{alert('Android: Bofya ⋮ > Install app\\niPhone: Share > Add to Home Screen');}});</script>
"""
html(install_code, height=150)

# ===== 2. CONFIG ZOTE KAMA ZILIVYO =====
NMB_ACC = "22810064566"
BASE_FEE = 15000
COMMISSION = 0.05

BEI_CONFIG = {
    "Pikipiki": {"bei": 8000, "max_kg": 50, "desc": "Mizigo midogo hadi 50kg"},
    "Bajaji": {"bei": 12000, "max_kg": 300, "desc": "Mizigo ya kati hadi 300kg"},
    "Pickup Small": {"bei": 18000, "max_kg": 1000, "desc": "Mizigo hadi Tani 1"},
    "Fuso Small": {"bei": 25000, "max_kg": 3500, "desc": "Mizigo hadi Tani 3.5"},
    "Fuso Big": {"bei": 35000, "max_kg": 10000, "desc": "Mizigo kubwa hadi Tani 10"},
}

VITUO_COORDS = {
    "Kariakoo": (-6.8291, 39.2683), "Posta": (-6.8166, 39.2883), "Ubungo": (-6.7900, 39.2050),
    "Mbagala": (-6.9176, 39.2736), "Tegeta": (-6.7200, 39.1600), "Mbezi": (-6.7500, 39.1500),
    "Kimara": (-6.7800, 39.1700), "Kigamboni": (-6.8100, 39.3400), "Msasani": (-6.7500, 39.2700),
    "Sinza": (-6.7750, 39.2000), "Manzese": (-6.8000, 39.2300), "Tabata": (-6.8500, 39.2200),
    "Chanika": (-6.9500, 39.1000), "Bunju": (-6.7000, 39.1800), "Kivukoni": (-6.8200, 39.2950),
    "Ilala": (-6.8300, 39.2500), "Temeke": (-6.8700, 39.2800), "Kinondoni": (-6.7700, 39.2500)
}
VITUO = list(VITUO_COORDS.keys())

conn = sqlite3.connect('hama_v69.db', check_same_thread=False)
c = conn.cursor()

# TABLE - NA COLUMNS ZOTE
c.execute("""CREATE TABLE IF NOT EXISTS drivers (
 id INTEGER PRIMARY KEY, jina TEXT, simu TEXT, aina TEXT, bei REAL,
 nida TEXT, gari TEXT, namba_gari TEXT, kituo TEXT, leseni TEXT,
 status TEXT DEFAULT 'Inahakikiwa', lat REAL, lng REAL, picha TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS orders (
 id TEXT PRIMARY KEY, mteja_name TEXT, mteja_phone TEXT, mzigo TEXT, kg REAL,
 from_kituo TEXT, to_kituo TEXT, driver_id INTEGER, driver_name TEXT,
 driver_phone TEXT, bei REAL, jumla REAL, status TEXT, time TEXT,
 mteja_lat REAL, mteja_lng REAL, malipo TEXT DEFAULT 'Haijalipiwa')""")
conn.commit()

def gen_id(): return "HAMA"+str(random.randint(10000,99999))
def calc_distance(lat1,lon1,lat2,lon2):
    R=6371; dlat=math.radians(lat2-lat1); dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R*2*math.asin(math.sqrt(a))

# ===== 3. MENU =====
menu = st.sidebar.radio("📱 MENU KUU", ["🛒 Mteja - Tuma Mzigo", " Dereva - Sajili Taarifa ZOTE", "📦 Dereva - Wallet & Oda Zangu LIVE", "🗺️ Ramani LIVE - Wote", "🔐 Admin - Oda + Madereva WOTE"])

# ========== MTEJA - KAMILI ==========
if menu=="🛒 Mteja - Tuma Mzigo":
    st.header("🛒 Tuma Mzigo - Chagua Dereva Aliyethibitishwa")
    col1,col2 = st.columns(2)
    with col1:
        b_name = st.text_input("Jina lako Kamili *")
        b_phone = st.text_input("Simu yako *")
        b_kg = st.number_input("Uzito wa Mzigo (kg)", min_value=1, value=100)
    with col2:
        b_mzigo = st.selectbox("Aina ya Mzigo", list(BEI_CONFIG.keys()))
        b_from = st.selectbox("Kutoka Kituo", VITUO)
        b_to = st.selectbox("Kwenda Kituo", VITUO)
        st.info(f"ℹ️ {BEI_CONFIG[b_mzigo]['desc']}")

    # CHAGUA DEREVA ALIYE APPROVED TU
    drivers = pd.read_sql("SELECT * FROM drivers WHERE status='Approved'", conn)
    if drivers.empty:
        st.warning(" Hakuna dereva aliyethibitishwa na Admin bado - Subiri Admin akubali madereva")
    else:
        # Filter kwa uzito
        suitable = []
        for _,d in drivers.iterrows():
            max_kg = BEI_CONFIG.get(d['aina'],{"max_kg":10000})["max_kg"]
            if b_kg <= max_kg:
                suitable.append(d)
        if not suitable:
            st.error(f"Mzigo wa {b_kg}kg ni mzito - Hakuna gari linalobeba")
        else:
            df_s = pd.DataFrame(suitable)
            df_s['label'] = df_s['jina']+" | "+df_s['aina']+" | No: "+df_s['namba_gari']+" | "+df_s['bei'].astype(str)+" TZS/km ✅"
            sel_label = st.selectbox(f"Dereva ({len(df_s)}) Walio Tayari:", df_s['label'])
            sel_row = df_s[df_s['label']==sel_label].iloc[0]

            lat1,lon1 = VITUO_COORDS[b_from]
            lat2,lon2 = VITUO_COORDS[b_to]
            dist = calc_distance(lat1,lon1,lat2,lon2)
            jumla = dist*float(sel_row['bei']) + BASE_FEE
            st.success(f" Umbali: {dist:.1f}km | Bei/km: {sel_row['bei']} | Jumla: TZS {jumla:,.0f} (incl. Base {BASE_FEE})")

            if st.button(" TUMA ODA KWA DEREVA - LIPA NMB", use_container_width=True, type="primary"):
                if not b_name or not b_phone:
                    st.error("Jaza jina na simu")
                else:
                    m_lat = lat1+random.uniform(-0.01,0.01)
                    m_lng = lon1+random.uniform(-0.01,0.01)
                    c.execute("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     (gen_id(), b_name, b_phone, b_mzigo, b_kg, b_from, b_to, int(sel_row['id']), sel_row['jina'], sel_row['simu'], float(sel_row['bei']), jumla, "Inasubiri Dereva", datetime.now().strftime("%Y-%m-%d %H:%M"), m_lat, m_lng, "Haijalipiwa"))
                    conn.commit()
                    st.balloons()
                    st.success(f"Oda imetumwa kwa {sel_row['jina']} ({sel_row['namba_gari']})! Nenda kalipie NMB Acc: {NMB_ACC}")

# ========== DEREVA SAJILI - KAMILI NA NIDA NA NAMBA GARI ==========
elif menu=="Dereva - Sajili Taarifa ZOTE":
    st.header("Sajili - Jaza Kila Kitu Admin Aone")
    with st.form("sajili_full"):
        c1,c2 = st.columns(2)
        with c1:
            jina = st.text_input("Jina Kamili *")
            simu = st.text_input("Simu *")
            nida = st.text_input("Namba ya NIDA * (20 tarakimu)")
            leseni = st.text_input("Namba ya Leseni")
        with c2:
            aina = st.selectbox("Aina ya Gari *", list(BEI_CONFIG.keys()))
            gari = st.text_input("Model (mfano: TVS King, Fuso Fighter)")
            namba_gari = st.text_input("Namba ya Gari/Pikipiki * (mfano: T123 ABC)")
            kituo = st.selectbox("Kituo chako *", VITUO)
            bei = st.number_input("Bei yako kwa km", value=BEI_CONFIG[aina]["bei"])
        submit = st.form_submit_button(" TUMA KWA ADMIN - NIDA NA GARI ZOTE")
        if submit:
            if not jina or not simu or not nida or not namba_gari:
                st.error("Jaza * zote - NIDA na Namba ya Gari lazima!")
            else:
                lat,lng = VITUO_COORDS[kituo]
                c.execute("INSERT INTO drivers (jina,simu,aina,bei,nida,gari,namba_gari,kituo,leseni,status,lat,lng) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                 (jina,simu,aina,bei,nida,gari,namba_gari,kituo,leseni,'Inahakikiwa',lat+random.uniform(-0.02,0.02),lng+random.uniform(-0.02,0.02)))
                conn.commit()
                st.success(" Umesajiliwa! Admin ataona NIDA yako na Namba ya Gari - Subiri Approval")

# ========== WALLET DEREVA - LIVE ==========
elif menu==" Dereva - Wallet & Oda Zangu LIVE":
    st.header(" Wallet - Oda Zangu LIVE")
    simu = st.text_input("Ingiza Simu yako uliyosajili")
    if simu:
        drv = pd.read_sql(f"SELECT * FROM drivers WHERE simu='{simu}'", conn)
        if drv.empty:
            st.error("Simu haijasajiliwa")
        else:
            d = drv.iloc[0]
            st.info(f"Karibu {d['jina']} | {d['gari']} {d['namba_gari']} | Status: {d['status']} | NIDA: {d['nida']}")
            if d['status']!='Approved':
                st.warning("Bado hujakubaliwa na Admin")
            else:
                orders = pd.read_sql(f"SELECT * FROM orders WHERE driver_id={int(d['id'])} ORDER BY time DESC", conn)
                if orders.empty:
                    st.write("Hakuna oda kwako bado - Mteja akichagua gari lako itaonekana hapa")
                else:
                    for _, o in orders.iterrows():
                        with st.container(border=True):
                            col1,col2 = st.columns([3,1])
                            with col1:
                                st.write(f"**📦 {o['id']}** - {o['mzigo']} {o['kg']}kg")
                                st.write(f"Kutoka {o['from_kituo']} → {o['to_kituo']} | Jumla TZS {o['jumla']:,.0f}")
                                st.write(f"Mteja: {o['mteja_name']} ☎️ {o['mteja_phone']}")
                                st.write(f"Status: `{o['status']}` | Malipo: {o['malipo']}")
                            with col2:
                                if st.button(f" Kubali", key=f"acc_{o['id']}"):
                                    c.execute(f"UPDATE orders SET status='Imekubaliwa na Dereva' WHERE id='{o['id']}'")
                                    conn.commit()
                                    st.rerun()
                                if st.button(f Imekamilika", key=f"done_{o['id']}"):
                                    c.execute(f"UPDATE orders SET status='Imekamilika' WHERE id='{o['id']}'")
                                    conn.commit()
                                    st.rerun()

# ========== RAMANI LIVE ==========
elif menu==" Ramani LIVE - Wote":
    st.header(" Ramani LIVE - Madereva na Mteja")
    m = folium.Map(location=[-6.82, 39.26], zoom_start=11)
    drv = pd.read_sql("SELECT * FROM drivers WHERE status='Approved'", conn)
    for _, d in drv.iterrows():
        folium.Marker([d['lat'], d['lng']], popup=f"{d['jina']}<br>{d['gari']} {d['namba_gari']}<br>{d['simu']}<br>NIDA:{d['nida']}", tooltip=f"{d['jina']} - {d['namba_gari']}", icon=folium.Icon(color='orange', icon='truck', prefix='fa')).add_to(m)
    ords = pd.read_sql("SELECT * FROM orders WHERE status!='Imekamilika'", conn)
    for _, o in ords.iterrows():
        folium.Marker([o['mteja_lat'], o['mteja_lng']], popup=f"Oda {o['id']}<br>{o['mteja_name']} {o['mteja_phone']}<br>{o['from_kituo']}->{o['to_kituo']}", tooltip=f"Oda {o['id']}", icon=folium.Icon(color='red', icon='box', prefix='fa')).add_to(m)
    st_folium(m, width=900, height=600)

# ========== ADMIN KAMILI - ANAONA KILA KITU ==========
elif menu==" Admin - Oda + Madereva WOTE":
    pw = st.text_input("Password ya Admin", type="password")
    if pw=="hama123":
        st.header(" Admin Dashboard - HAMA")

        tab1, tab2, tab3 = st.tabs([" Madereva + NIDA + Gari", "📦 Oda ZOTE", "🗺️ Ramani ya Admin"])

        with tab1:
            st.subheader("Madereva - Taarifa ZOTE")
            drivers = pd.read_sql("SELECT * FROM drivers ORDER BY id DESC", conn)
            if not drivers.empty:
                st.dataframe(drivers[["id","jina","simu","nida","gari","namba_gari","leseni","aina","kituo","bei","status"]], use_container_width=True)
                for _, d in drivers.iterrows():
                    with st.expander(f"{'✅' if d['status']=='Approved' else '⏳'} {d['jina']} | {d['namba_gari']} | {d['simu']} | NIDA: {d['nida']}"):
                        st.write(f"**Jina:** {d['jina']} | **Simu:** {d['simu']}")
                        st.write(f"**NIDA:** `{d['nida']}`")
                        st.write(f"**Gari Model:** {d['gari']} | **Namba ya Gari:** `{d['namba_gari']}`")
                        st.write(f"**Leseni:** {d['leseni']} | **Aina:** {d['aina']} | **Kituo:** {d['kituo']} | **Bei:** {d['bei']}")
                        st.write(f"**Status:** {d['status']}")
                        c1,c2,c3 = st.columns(3)
                        if c1.button(f" Kubali", key=f"ap_{d['id']}"):
                            c.execute(f"UPDATE drivers SET status='Approved' WHERE id={d['id']}")
                            conn.commit()
                            st.rerun()
                        if c2.button(f"❌ Kataa", key=f"rej_{d['id']}"):
                            c.execute(f"UPDATE drivers SET status='Rejected' WHERE id={d['id']}")
                            conn.commit()
                            st.rerun()
                        if c3.button(f" Futa", key=f"del_{d['id']}"):
                            c.execute(f"DELETE FROM drivers WHERE id={d['id']}")
                            conn.commit()
                            st.rerun()

        with tab2:
            st.subheader("Oda ZOTE - Zinazoenda kwa Madereva")
            orders = pd.read_sql("SELECT * FROM orders ORDER BY time DESC", conn)
            if not orders.empty:
                st.dataframe(orders, use_container_width=True)
                st.metric("Jumla ya Oda", len(orders))
                st.metric("Zinazosubiri Dereva", len(orders[orders['status']=='Inasubiri Dereva']))
                st.metric("Zimekubaliwa", len(orders[orders['status']=='Imekubaliwa na Dereva']))
            else:
                st.write("Hakuna oda")

        with tab3:
            st.subheader("Ramani ya Admin - Wote LIVE")
            m = folium.Map(location=[-6.82, 39.26], zoom_start=11)
            for _, d in pd.read_sql("SELECT * FROM drivers", conn).iterrows():
                color = 'green' if d['status']=='Approved' else 'gray'
                folium.Marker([d['lat'], d['lng']], tooltip=f"{d['jina']} {d['namba_gari']} {d['status']}", icon=folium.Icon(color=color)).add_to(m)
            for _, o in pd.read_sql("SELECT * FROM orders", conn).iterrows():
                folium.Marker([o['mteja_lat'], o['mteja_lng']], tooltip=o['id'], icon=folium.Icon(color='red')).add_to(m)
            st_folium(m, width=900, height=500)
