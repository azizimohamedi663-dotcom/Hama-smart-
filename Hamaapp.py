import streamlit as st
import sqlite3, pandas as pd, random, time, math, os
from datetime import datetime

st.set_page_config(page_title="HAMA SMART APP", page_icon="🚚", layout="centered")

NMB_ACC = "22810064566"
BASE_FEE = 15000
COMMISSION = 0.05

BEI_CONFIG = {
    "Pikipiki": {"bei": 8000, "max_kg": 50},
    "Bajaji": {"bei": 12000, "max_kg": 300},
    "Pickup Small": {"bei": 18000, "max_kg": 1000},
    "Fuso Small": {"bei": 25000, "max_kg": 3500},
    "Fuso Big": {"bei": 35000, "max_kg": 10000},
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

conn = sqlite3.connect('hama_v681.db', check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS drivers (id INTEGER PRIMARY KEY, jina TEXT, simu TEXT, aina TEXT, bei REAL, nida TEXT, gari TEXT, kituo TEXT, lat_k REAL, lon_k REAL, picha_gari TEXT, verified INTEGER DEFAULT 0)")
c.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, mteja TEXT, simu_m TEXT, kutoka TEXT, kwenda TEXT, km REAL, jumla REAL, admin_pesa REAL, dereva_pesa REAL, status TEXT, driver_id INTEGER, lat_c REAL, lon_c REAL, ref TEXT, otp TEXT, date TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS wallets (driver_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, total_earned REAL DEFAULT 0)")
c.execute("CREATE TABLE IF NOT EXISTS admin_wallet (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0)")
c.execute("CREATE TABLE IF NOT EXISTS maoni (id INTEGER PRIMARY KEY, driver_id INTEGER, mteja TEXT, stars INTEGER, ujumbe TEXT, date TEXT)")
c.execute("INSERT OR IGNORE INTO admin_wallet (id,balance) VALUES (1,0)")
conn.commit()
os.makedirs("picha_madereva", exist_ok=True)

def distance_km(lat1,lon1,lat2,lon2):
    R=6371; dlat=math.radians(lat2-lat1); dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R*2*math.asin(math.sqrt(a))

st.markdown("<style>.orange{background:#FF6B00;padding:18px;border-radius:15px;color:white;text-align:center}.stButton>button{background:#FF6B00;color:white;border-radius:12px;height:48px;font-weight:bold;width:100%}</style><div class='orange'><h1>HAMA SMART APP</h1><p>Maoni | Live Map | Wallet | Admin Full Control</p></div>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("MENU", ["Mteja - Book", "Toa Maoni", "LIVE MAP", "Jisajili Dereva", "Dereva - Wallet", "Admin"])

if menu == "Mteja - Book":
    mteja=st.text_input("Jina lako"); simu_m=st.text_input("Simu 255...")
    col1,col2=st.columns(2)
    with col1: kutoka=st.selectbox("Kutoka", VITUO, index=8)
    with col2: kwenda=st.selectbox("Kwenda", VITUO, index=0)
    km=st.number_input("Umbali KM", 1.0, 100.0, 6.5)
    uzito=st.number_input("Uzito KG", 5, 10000, 30)
    fragile=st.checkbox("Fragile +10k"); wapakizi=st.checkbox("Wapakizi +20k")
    extra=0
    if fragile: extra+=10000
    if wapakizi: extra+=20000
    if uzito>500: extra+=(uzito-500)*50
    lat_c, lon_c = VITUO_COORDS.get(kutoka, (-6.7924, 39.2083))
    c.execute("SELECT id,jina,simu,aina,kituo,lat_k,lon_k,picha_gari FROM drivers WHERE verified=1")
    drivers=c.fetchall()
    if not drivers: st.warning("Hakuna dereva. Nenda Admin ukubali.")
    else:
        for did,jina,simu,aina,kituo,lat_k,lon_k,picha in drivers:
            conf=BEI_CONFIG.get(aina, {"bei":12000})
            jumla=km*conf["bei"]+BASE_FEE+extra
            c.execute("SELECT AVG(stars),COUNT(*) FROM maoni WHERE driver_id=?",(did,)); avg,cnt=c.fetchone(); rating = str(round(avg,1))+" ⭐ ("+str(cnt)+")" if avg else "Bado hana maoni"
            d_km=distance_km(lat_c, lon_c, lat_k, lon_k) if lat_k else 0
            with st.container(border=True):
                cA,cB=st.columns([1,2])
                with cA:
                    if picha and os.path.exists(picha): st.image(picha, width=110)
                    else: st.write("🚚")
                with cB:
                    st.write(jina+" | "+aina+" | "+kituo)
                    st.write(str(round(d_km,1))+" KM | "+str(int(jumla))+" TZS | "+rating)
                    if st.button("Chagua "+jina, key="chagua_"+str(did)):
                        st.session_state['order']=(did,jina,simu,jumla,km,kutoka,kwenda,mteja,simu_m,lat_c,lon_c)
        if 'order' in st.session_state:
            did,jina,simu_d,jumla,km,kutoka,kwenda,mteja,simu_m,lat_c,lon_c=st.session_state['order']
            st.divider()
            st.error("LIPA "+str(int(jumla))+" TZS -> NMB "+NMB_ACC)
            kiasi=st.number_input("Uliolipa", 0, step=1000); ref=st.text_input("Ref ya NMB")
            if st.button("THIBITISHA MALIPO"):
                if kiasi<jumla: st.error("Pungufu!")
                else:
                    otp=str(random.randint(1000,9999))
                    admin_pesa=jumla*COMMISSION; dereva_pesa=jumla-admin_pesa
                    c.execute("INSERT INTO orders (mteja,simu_m,kutoka,kwenda,km,jumla,admin_pesa,dereva_pesa,status,driver_id,lat_c,lon_c,ref,otp,date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(mteja,simu_m,kutoka,kwenda,km,jumla,admin_pesa,dereva_pesa,"pending_admin",did,lat_c,lon_c,ref,otp,str(datetime.now())))
                    conn.commit(); st.success("Oda "+str(c.lastrowid)+" OTP "+otp); st.balloons()

elif menu == "Toa Maoni":
    st.subheader("Mpe Dereva Nyota")
    c.execute("SELECT id,jina FROM drivers WHERE verified=1"); opts=c.fetchall()
    if opts:
        d_map={str(o[0])+" - "+o[1]: o[0] for o in opts}
        sel=st.selectbox("Chagua Dereva", list(d_map.keys())); did=d_map[sel]
        mteja_r=st.text_input("Jina lako"); stars=st.slider("Nyota",1,5,5); uj=st.text_area("Ujumbe mf: Alifika haraka")
        if st.button("Tuma Maoni"):
            c.execute("INSERT INTO maoni (driver_id,mteja,stars,ujumbe,date) VALUES (?,?,?,?,?)",(did,mteja_r,stars,uj,str(datetime.now()))); conn.commit(); st.success("Asante!")
    c.execute("SELECT d.jina,m.mteja,m.stars,m.ujumbe FROM maoni m JOIN drivers d ON m.driver_id=d.id ORDER BY m.id DESC LIMIT 10")
    for jina,mteja,s,u in c.fetchall(): st.write(jina+" | "+mteja+" | "+"⭐"*s+" "+u)

elif menu == "LIVE MAP":
    st.subheader("Madereva Live Dar")
    c.execute("SELECT jina,kituo,lat_k,lon_k,aina FROM drivers WHERE verified=1")
    rows=c.fetchall()
    if rows:
        df=pd.DataFrame(rows, columns=["jina","kituo","lat","lon","aina"])
        st.map(df, latitude="lat", longitude="lon")
        for r in rows: st.write(r[0]+" - "+r[1]+" - "+r[4])
    else: st.write("Hakuna dereva bado")

elif menu == "Jisajili Dereva":
    jina=st.text_input("Jina kamili"); simu=st.text_input("Simu 255..."); aina=st.selectbox("Aina ya gari", list(BEI_CONFIG.keys()))
    nida=st.text_input("NIDA 20"); gari=st.text_input("Namba ya gari")
    kituo=st.selectbox("Kituo unapopaki", VITUO)
    picha_cam=st.camera_input("Piga picha ya gari na plate")
    picha_up=st.file_uploader("Au upload picha", type=['jpg','png','jpeg'])
    if st.button("Tuma Maombi"):
        if len(nida)<10: st.error("NIDA fupi")
        elif not picha_cam and not picha_up: st.error("Piga picha ya gari")
        else:
            path="picha_madereva/"+simu+"_gari.jpg"
            if picha_cam:
                with open(path,"wb") as f: f.write(picha_cam.getbuffer())
            else:
                with open(path,"wb") as f: f.write(picha_up.getbuffer())
            lat_k, lon_k = VITUO_COORDS.get(kituo, (-6.7924, 39.2083))
            c.execute("INSERT INTO drivers (jina,simu,aina,bei,nida,gari,kituo,lat_k,lon_k,picha_gari,verified) VALUES (?,?,?,?,?,?,?,?,?,?,0)",(jina,simu,aina,BEI_CONFIG[aina]['bei'],nida,gari,kituo,lat_k,lon_k,path))
            conn.commit(); st.success("Umesajiliwa Kituo "+kituo+" Subiri Admin")

elif menu == "Dereva - Wallet":
    simu_d=st.text_input("Simu yako")
    if simu_d:
        c.execute("SELECT id,jina,kituo FROM drivers WHERE simu=? AND verified=1",(simu_d,)); dr=c.fetchone()
        if not dr: st.error("Huja-verifywa bado"); st.stop()
        did,jina,kituo=dr
        c.execute("SELECT balance,total_earned FROM wallets WHERE driver_id=?",(did,)); w=c.fetchone(); bal,tot=w if w else (0,0)
        st.metric("Balance", str(int(bal))); st.metric("Jumla", str(int(tot)))
        c.execute("SELECT AVG(stars),COUNT(*) FROM maoni WHERE driver_id=?",(did,)); avg,cnt=c.fetchone()
        if avg: st.success("⭐ "+str(round(avg,1))+" kutoka kwa wateja "+str(cnt))
        c.execute("SELECT id,mteja,jumla,dereva_pesa,status,otp FROM orders WHERE driver_id=? ORDER BY id DESC",(did,))
        for oid,mteja,jumla,d_pesa,status,otp in c.fetchall():
            with st.container(border=True):
                st.write("Oda "+str(oid)+" "+mteja+" "+str(int(jumla))+" Kwako "+str(int(d_pesa))+" - "+status)
                if "verified" in status:
                    code_in=st.text_input("Ingiza OTP "+str(oid), key="otp_"+str(oid))
                    if st.button("Maliza Mzigo "+str(oid), key="fin_"+str(oid)):
                        if code_in==otp:
                            c.execute("UPDATE orders SET status='completed' WHERE id=?",(oid,))
                            c.execute("INSERT INTO wallets (driver_id,balance,total_earned) VALUES (?,?,?) ON CONFLICT(driver_id) DO UPDATE SET balance=balance+?, total_earned=total_earned+?", (did,d_pesa,d_pesa,d_pesa,d_pesa))
                            c.execute("UPDATE admin_wallet SET balance=balance+? WHERE id=1", (jumla*COMMISSION,))
                            conn.commit(); st.success(str(int(d_pesa))+" imeingia")

else:
    pwd=st.text_input("Password Admin", type="password")
    if pwd=="hama123":
        c.execute("SELECT balance FROM admin_wallet WHERE id=1"); ab=c.fetchone()[0]; st.metric("Commission yako", str(int(ab)))
        st.divider(); st.write("Madereva Pending - Hawajakubaliwa")
        c.execute("SELECT id,jina,simu,aina,kituo,picha_gari FROM drivers WHERE verified=0")
        for i,j,s,a,kt,pg in c.fetchall():
            with st.container(border=True):
                st.write(j+" | "+s+" | "+a+" | "+kt)
                if pg and os.path.exists(pg): st.image(pg, width=180)
                c1,c2=st.columns(2)
                with c1:
                    if st.button("Kubali "+j, key="kubali_"+str(i)):
                        c.execute("UPDATE drivers SET verified=1 WHERE id=?",(i,)); conn.commit(); st.success("Amekubaliwa"); time.sleep(1); st.rerun()
                with c2:
                    if st.button("Futa Pending "+j, key="kataa_"+str(i)):
                        c.execute("DELETE FROM drivers WHERE id=?",(i,)); conn.commit(); st.success("Amefutwa"); st.rerun()
        st.divider(); st.write("Madereva Waliokubaliwa - Unaweza Kufuta Hapa")
        c.execute("SELECT id,jina,simu,aina,kituo FROM drivers WHERE verified=1")
        for i,j,s,a,kt in c.fetchall():
            col1,col2=st.columns([3,1])
            with col1: st.write(j+" | "+s+" | "+a+" | "+kt)
            with col2:
                if st.button("Futa", key="futa_verified_"+str(i)):
                    c.execute("DELETE FROM drivers WHERE id=?",(i,))
                    c.execute("DELETE FROM wallets WHERE driver_id=?",(i,))
                    c.execute("DELETE FROM maoni WHERE driver_id=?",(i,))
                    conn.commit(); st.success(j+" amefutwa"); time.sleep(1); st.rerun()
        st.divider()
        c.execute("SELECT id,mteja,jumla,ref FROM orders WHERE status='pending_admin'")
        for oid,mteja,jumla,ref in c.fetchall():
            st.write("Oda "+str(oid)+" "+mteja+" "+str(int(jumla))+" Ref "+ref)
            if st.button("Thibitisha Oda "+str(oid), key="thibi_"+str
