import streamlit as st
import sqlite3
import os, json, urllib.request
from datetime import datetime

# --- BADILISHA HAPA TU ---
NMB_ACCOUNT_NUMBER = "22810064566" # Weka Account Number yako ya NMB hapa
NMB_ACCOUNT_NAME = "AZIZI FRENK MOHAMEDI"
COMMISSION_RATE = 0.05 # 5% yako
BASE_FEE = 15000
AINA_ZA_MAGARI = ["Bajaji / Pickup Ndogo", "Toyota Hilux", "Canter Ndogo", "Fuso Kubwa"]

# --- DATABASE ---
conn = sqlite3.connect('hama.db', check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS drivers (id INTEGER PRIMARY KEY, jina TEXT, simu TEXT, aina TEXT, namba_gari TEXT, picha_path TEXT, bei_km REAL, date TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, mteja TEXT, simu_mteja TEXT, kutoka TEXT, kwenda TEXT, km REAL, jumla REAL, commission REAL, payout REAL, driver_id INTEGER, status TEXT, date TEXT)")
conn.commit()

def get_km(a,b):
    try:
        def geocode(q):
            url=f"https://nominatim.openstreetmap.org/search?q={q.replace(' ','%20')}, Dar es Salaam&format=json"
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

st.set_page_config(page_title="HAMA SMART", page_icon="🚚", layout="centered")
st.markdown("<style>.stButton>button{width:100%;height:3.5em;font-size:18px;font-weight:bold;border-radius:15px;background:#FF6B00;color:white} #MainMenu{visibility:hidden} footer{visibility:hidden}</style>", unsafe_allow_html=True)
st.title("🚚 HAMA SMART")
menu = st.selectbox("CHAGUA", ["🚚 Mteja - Oda Mpya", "🧑‍✈️ Dereva - Weka Bei Yako", "💰 Admin - 5% Yangu"])

if "Mteja" in menu:
    mteja=st.text_input("Jina lako"); simu_m=st.text_input("Namba yako")
    kutoka=st.text_input("Kutoka wapi?"); kwenda=st.text_input("Kwenda wapi?")
    aina_f=st.selectbox("Aina ya gari", AINA_ZA_MAGARI)
    if st.button("TAFUTA MADEREVA"):
        km=get_km(kutoka,kwenda)
        if km==0: km=st.number_input("Weka KM",1.0,500.0,12.0)
        st.session_state['km']=km; st.session_state['ft']=(kutoka,kwenda,mteja,simu_m); st.success(f"Umbali: {km:.1f} KM")
    if 'km' in st.session_state:
        km=st.session_state['km']; kutoka,kwenda,mteja_s,simu_s=st.session_state['ft']
        c.execute("SELECT id,jina,simu,namba_gari,bei_km,picha_path FROM drivers WHERE aina=?", (aina_f,))
        for d in c.fetchall():
            did,jina,simu,ng,bei_km,pp=d; jumla=km*bei_km+BASE_FEE; comm=jumla*COMMISSION_RATE
            with st.container(border=True):
                if pp and os.path.exists(pp): st.image(pp, use_container_width=True)
                st.write(f"**{jina}** | {ng} | Bei yake: **{bei_km:,.0f} /km**")
                st.metric("Jumla", f"{jumla:,.0f} TZS")
                if st.button(f"CHAGUA {jina}", key=f"c{did}"):
                    st.session_state['selected']=(did,jina,simu,jumla,km,kutoka,kwenda,mteja_s,simu_s,comm)
        if 'selected' in st.session_state:
            did,jina,simu,jumla,km,kutoka,kwenda,mteja_s,simu_s,comm=st.session_state['selected']
            st.divider(); st.error(f"LIPA NMB ACCOUNT: {NMB_ACCOUNT_NUMBER}")
            st.code(f"Benki: NMB\nJina: {NMB_ACCOUNT_NAME}\nAccount: {NMB_ACCOUNT_NUMBER}\nKiasi: {jumla:,.0f}\nKumb: HAMA-{mteja_s}")
            ref=st.text_input("Weka Reference ya NMB baada ya kulipa")
            if st.button("NIMELIPA - THIBITISHA"):
                if ref:
                    pay=jumla-comm
                    c.execute("INSERT INTO orders VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)",(mteja_s,simu_s,kutoka,kwenda,km,jumla,comm,pay,did,f'paid_{ref}',str(datetime.now())))
                    conn.commit(); st.balloons(); st.success(f"Oda #{c.lastrowid} imethibitishwa! Dereva {jina} anakuja. Ref: {ref}")
                    st.link_button(f"WhatsApp {jina}", f"https://wa.me/255{simu[-9:]}?text=Habari {jina}, nimelipa HAMA kutoka {kutoka} kwenda {kwenda}")

elif "Dereva" in menu:
    jina=st.text_input("Jina kamili"); simu=st.text_input("Simu 07.."); ng=st.text_input("Namba ya Gari")
    aina=st.selectbox("Aina ya gari lako", AINA_ZA_MAGARI)
    bei=st.number_input("WEKA BEI YAKO KWA KM 1 (TSH)", 500, 10000, 1500, 100, help="Wewe mwenyewe unaamua. Wengine wanaweka 1200, 1500, 2000")
    st.info(f"Ukisafirisha 10KM: Mteja atalipa {(10*bei+BASE_FEE):,} TZS. Wewe utapata 95% = {((10*bei+BASE_FEE)*0.95):,.0f} TZS")
    picha=st.file_uploader("Picha ya Gari", type=['jpg','png'])
    if st.button("JISAJILI NA BEI YANGU"):
        path=""
        if picha:
            os.makedirs("picha_za_magari", exist_ok=True); path=f"picha_za_magari/{ng}_{picha.name}"; open(path,"wb").write(picha.getbuffer())
        c.execute("INSERT INTO drivers VALUES (NULL,?,?,?,?,?,?,?)",(jina,simu,aina,ng,path,bei,str(datetime.now())))
        conn.commit(); st.success(f"Hongera {jina}! Bei yako {bei:,} TZS/km imesajiliwa.")

else:
    c.execute("SELECT SUM(commission),SUM(jumla),COUNT(*) FROM orders"); com,tot,cnt=c.fetchone()
    st.metric("Faida Yako 5%", f"{(com or 0):,.0f} TZS"); st.metric("Mauzo", f"{(tot or 0):,.0f} TZS")
    c.execute("SELECT mteja,kutoka,kwenda,jumla,commission,status,date FROM orders ORDER BY id DESC")
    st.dataframe(c.fetchall(), use_container_width=True)
