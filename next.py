import streamlit as st
from streamlit.components.v1 import html
import sqlite3, pandas as pd, random, folium
from streamlit_folium import st_folium
from datetime import datetime

# LAZIMA IWE YA KWANZA PEKEE
st.set_page_config(page_title="HAMA SMART APP", page_icon="🚌", layout="wide")

conn = sqlite3.connect('hama_v69.db', check_same_thread=False)
c = conn.cursor()

VITUO_COORDS = {
    "Kariakoo": (-6.8291, 39.2683), "Posta": (-6.8166, 39.2883), "Ubungo": (-6.79, 39.205),
    "Mbagala": (-6.9176, 39.2736), "Tegeta": (-6.72, 39.16), "Mbezi": (-6.75, 39.15),
    "Kimara": (-6.78, 39.17), "Kigamboni": (-6.81, 39.34)
}
VITUO = list(VITUO_COORDS.keys())

# TABLE KAMILI NA NIDA + GARI
c.execute("""CREATE TABLE IF NOT EXISTS drivers (
 id INTEGER PRIMARY KEY, jina TEXT, simu TEXT, aina TEXT, bei REAL,
 nida TEXT, gari TEXT, namba_gari TEXT, kituo TEXT, leseni TEXT,
 status TEXT DEFAULT 'Inahakikiwa', lat REAL, lng REAL)""")

c.execute("""CREATE TABLE IF NOT EXISTS orders (
 id TEXT PRIMARY KEY, mteja_name TEXT, mteja_phone TEXT, mzigo TEXT,
 from_kituo TEXT, to_kituo TEXT, driver_id INTEGER, driver_name TEXT,
 bei REAL, status TEXT, time TEXT, mteja_lat REAL, mteja_lng REAL)""")
conn.commit()

def gen_id(): return "HAMA"+str(random.randint(1000,9999))

menu = st.sidebar.radio("MENU", ["🛒 Mteja - Tuma Mzigo", "👨‍✈️ Dereva - Sajili", "📦 Dereva - Wallet & Oda Zangu", "🗺️ Ramani LIVE", "🔐 Admin"])

# ========== 1. MTEJA ==========
if menu=="🛒 Mteja - Tuma Mzigo":
    st.header("🛒 Tuma Mzigo")
    col1,col2 = st.columns(2)
    with col1:
        b_name = st.text_input("Jina lako")
        b_phone = st.text_input("Simu yako")
        b_mzigo = st.selectbox("Mzigo", ["Pikipiki","Bajaji","Pickup Small","Fuso Small","Fuso Big"])
    with col2:
        b_from = st.selectbox("Kutoka", VITUO)
        b_to = st.selectbox("Kwenda", VITUO)

    drivers = pd.read_sql("SELECT * FROM drivers WHERE status='Approved'", conn)
    if drivers.empty:
        st.error("⚠️ Hakuna dereva aliyethibitishwa - Subiri Admin")
    else:
        drivers['label'] = drivers['jina']+" - "+drivers['gari']+" ("+drivers['namba_gari']+") - "+drivers['bei'].astype(str)
        sel = st.selectbox("Chagua Dereva", drivers['label'])
        sel_row = drivers[drivers['label']==sel].iloc[0]
        st.success(f"Umechagua: {sel_row['jina']} | Namba: {sel_row['namba_gari']} | Simu: {sel_row['simu']}")

        if st.button("📦 TUMA ODA KWA DEREVA", use_container_width=True):
            if not b_name or not b_phone:
                st.error("Jaza jina na simu")
            else:
                # Random location ya mteja karibu na kituo alichochagua
                lat,lng = VITUO_COORDS[b_from]
                c.execute("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                 (gen_id(), b_name, b_phone, b_mzigo, b_from, b_to, int(sel_row['id']), sel_row['jina'], float(sel_row['bei']), "Inasubiri Dereva", datetime.now().strftime("%Y-%m-%d %H:%M"), lat+random.uniform(-0.02,0.02), lng+random.uniform(-0.02,0.02)))
                conn.commit()
                st.balloons()
                st.success(f"✅ Oda imetumwa kwa {sel_row['jina']}!")

# ========== 2. DEREVA SAJILI - NA TAARIFA ZOTE ==========
elif menu=="👨‍✈️ Dereva - Sajili":
    st.header("👨‍✈️ Sajili kama Dereva - Jaza Taarifa ZOTE")
    with st.form("sajili"):
        jina = st.text_input("Jina Kamili *")
        simu = st.text_input("Namba ya Simu *")
        nida = st.text_input("Namba ya NIDA * (mfano: 19900101-12345-00001-12)")
        aina = st.selectbox("Aina ya Gari", ["Pikipiki","Bajaji","Pickup Small","Fuso Small","Fuso Big"])
        gari = st.text_input("Model ya Gari/Pikipiki (mfano: TVS, Fuso Fighter)")
        namba_gari = st.text_input("Namba ya Gari/Pikipiki * (mfano: T123 ABC)")
        leseni = st.text_input("Namba ya Leseni ya Udereva")
        kituo = st.selectbox("Kituo chako", VITUO)
        bei = st.number_input("Bei yako kwa km (TZS)", min_value=1000, value=8000)
        btn = st.form_submit_button("📤 TUMA KWA ADMIN AKUHAKIKI")

        if btn:
            if not jina or not simu or not nida or not namba_gari:
                st.error("Jaza * zote - NIDA na Namba ya Gari ni lazima!")
            else:
                lat,lng = VITUO_COORDS[kituo]
                c.execute("INSERT INTO drivers (jina,simu,aina,bei,nida,gari,namba_gari,kituo,leseni,status,lat,lng) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                 (jina,simu,aina,bei,nida,gari,namba_gari,kituo,leseni,'Inahakikiwa',lat+random.uniform(-0.01,0.01),lng+random.uniform(-0.01,0.01)))
                conn.commit()
                st.success("✅ Taarifa zako zimetumwa kwa Admin! Subiri akubali - Utapigiwa")

# ========== 3. DEREVA WALLET ==========
elif menu=="📦 Dereva - Wallet & Oda Zangu":
    st.header("📦 Oda Zangu (Dereva)")
    simu = st.text_input("Ingiza Simu yako ya Usajili")
    if simu:
        drv = pd.read_sql(f"SELECT * FROM drivers WHERE simu='{simu}'", conn)
        if drv.empty:
            st.error("Hujasajiliwa")
        else:
            st.info(f"Karibu {drv.iloc[0]['jina']} - {drv.iloc[0]['status']}")
            orders = pd.read_sql(f"SELECT * FROM orders WHERE driver_id={int(drv.iloc[0]['id'])}", conn)
            if orders.empty:
                st.write("Hakuna oda kwako")
            for _, o in orders.iterrows():
                with st.container(border=True):
                    st.write(f"**{o['id']}** - {o['mzigo']} - {o['from_kituo']}→{o['to_kituo']}")
                    st.write(f"Mteja: {o['mteja_name']} {o['mteja_phone']}")
                    st.write(f"Status: {o['status']}")
                    if st.button(f"Kubali {o['id']}", key=o['id']):
                        c.execute(f"UPDATE orders SET status='Imekubaliwa' WHERE id='{o['id']}'")
                        conn.commit()
                        st.rerun()

# ========== 4. RAMANI LIVE ==========
elif menu=="🗺️ Ramani LIVE":
    st.header("🗺️ Ramani LIVE - Madereva na Oda")
    m = folium.Map(location=[-6.82, 39.26], zoom_start=11)
    # Madereva
    for _, d in pd.read_sql("SELECT * FROM drivers WHERE status='Approved'", conn).iterrows():
        folium.Marker([d['lat'], d['lng']], tooltip=f"{d['jina']} - {d['namba_gari']} - {d['simu']}", icon=folium.Icon(color='orange', icon='truck', prefix='fa')).add_to(m)
    # Oda
    for _, o in pd.read_sql("SELECT * FROM orders WHERE status!='Imekamilika'", conn).iterrows():
        folium.Marker([o['mteja_lat'], o['mteja_lng']], tooltip=f"Oda {o['id']} - {o['mteja_name']}", icon=folium.Icon(color='red', icon='box', prefix='fa')).add_to(m)

    st_folium(m, width=700, height=500)
    st.info("🟠 Chungwa = Dereva | 🔴 Nyekundu = Oda ya Mteja - Ramani ina-update kila uki-refresh")

# ========== 5. ADMIN - ANAONA KILA KITU ==========
elif menu=="🔐 Admin":
    pw = st.text_input("Password", type="password")
    if pw=="hama123":
        st.header("🔐 Admin Dashboard")

        # DEREVA WOTE NA TAARIFA ZOTE
        st.subheader("👨‍✈️ Madereva - Na NIDA, Namba Gari, Leseni")
        drivers = pd.read_sql("SELECT * FROM drivers", conn)
        if not drivers.empty:
            st.dataframe(drivers[["id","jina","simu","nida","gari","namba_gari","leseni","kituo","bei","status"]], use_container_width=True)

            for _, d in drivers.iterrows():
                with st.expander(f"🔍 {d['jina']} - {d['simu']} - {d['status']}"):
                    st.write(f"**Jina:** {d['jina']}")
                    st.write(f"**Simu:** {d['simu']}")
                    st.write(f"**NIDA:** `{d['nida']}` - HII NDIO ULIOIKOSA")
                    st.write(f"**Gari:** {d['gari']} - **Namba:** `{d['namba_gari']}`")
                    st.write(f"**Leseni:** {d['leseni']}")
                    st.write(f"**Kituo:** {d['kituo']} - **Bei:** {d['bei']}")
                    c1,c2,c3 = st.columns(3)
                    if c1.button(f"✅ Kubali {d['id']}", key=f"ok_{d['id']}"):
                        c.execute(f"UPDATE drivers SET status='Approved' WHERE id={d['id']}")
                        conn.commit()
                        st.rerun()
                    if c2.button(f"❌ Kataa {d['id']}", key=f"no_{d['id']}"):
                        c.execute(f"UPDATE drivers SET status='Rejected' WHERE id={d['id']}")
                        conn.commit()
                        st.rerun()
                    if c3.button(f"🗑️ Futa {d['id']}", key=f"del_{d['id']}"):
                        c.execute(f"DELETE FROM drivers WHERE id={d['id']}")
                        conn.commit()
                        st.rerun()
        else:
            st.write("Hakuna dereva")

        st.divider()
        # ODA ZOTE ADMIN ANAZIONA
        st.subheader("📦 Oda ZOTE - Admin Anaziona")
        orders = pd.read_sql("SELECT * FROM orders ORDER BY time DESC", conn)
        if not orders.empty:
            st.dataframe(orders, use_container_width=True)
            st.map(pd.DataFrame({"lat":orders['mteja_lat'], "lon":orders['mteja_lng']}))
        else:
            st.write("Hakuna oda")
