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

conn = sqlite3.connect('hama_v69.db', check_same_thread=False)
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
    R=6371
    dlat=math.radians(lat2-lat1)
    dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R*2*math.asin(math.sqrt(a))

st.markdown("<style>.orange{background:#FF6B00;padding:18px;border-radius:15px;color:white;text-align:center}.stButton>button{background:#FF6B00;color:white;border-radius:12px;height:48px;font-weight:bold;width:100%}</style><div class='orange'><h1>HAMA SMART APP</h1><p>Dereva Anaweka Bei | Maoni | Live Map | Wallet</p></div>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("MENU", ["Mteja - Book", "Toa Maoni", "LIVE MAP", "Jisajili Dereva", "Dereva - Wallet", "Admin"])

if menu == "Mteja - Book":
    mteja=st.text_input("Jina lako")
    simu_m=st.text_input("Simu 255...")
    col1,col2=st.columns(2)
    with col1:
        kutoka=st.selectbox("Kutoka", VITUO, index=8)
    with col2:
        kwenda=st.selectbox("Kwenda", VITUO, index=0)
    km=st.number_input("Umbali KM", 1.0, 100.0, 6.5)
    uzito=st.number_input("Uzito KG", 5, 10000, 30)
    fragile=st.checkbox("Fragile +10k")
    wapakizi=st.checkbox("Wapakizi +20k")
    extra=0
    if fragile:
        extra+=10000
    if wapakizi:
        extra+=20000
    if uzito>500:
        extra+=(uzito-500)*50
    lat_c, lon_c = VITUO_COORDS.get(kutoka, (-6.7924, 39.2083))
    c.execute("SELECT id,jina,simu,aina,bei,kituo,lat_k,lon_k,picha_gari FROM drivers WHERE verified=1")
    drivers=c.fetchall()
    if not drivers:
        st.warning("Hakuna dereva. Nenda Admin ukubali.")
    else:
        for did,jina,simu,aina,bei_d,kituo,lat_k,lon_k,picha in drivers:
            jumla=km*bei_d+BASE_FEE+extra
            c.execute("SELECT AVG(stars),COUNT(*) FROM maoni WHERE driver_id=?",(did,))
            avg,cnt=c.fetchone()
            rating = str(round(avg,1))+" STAR ("+str(cnt)+")" if avg else "Bado hana maoni"
            d_km=distance_km(lat_c, lon_c, lat_k, lon_k) if lat_k else 0
            with st.container(border=True):
                cA,cB=st.columns([1,2])
                with cA:
                    if picha and os.path.exists(picha):
                        st.image(picha, width=110)
                    else:
                        st.write("TRUCK")
                with cB:
                    st.write(jina+" | "+aina+" | Bei "+str(int(bei_d))+"/KM")
                    st.write(kituo+" | "+str(round(d_km,1))+" KM | "+str(int(jumla))+" TZS")
                    st.write(rating)
                    if st.button("Chagua "+jina, key="chagua_"+str(did)):
                        st.session_state['order']=(did,jina,simu,jumla,km,kutoka,kwenda,mteja,simu_m,lat_c,lon_c)
        if 'order' in st.session_state:
            did,jina,simu_d,jumla,km,kutoka,kwenda,mteja,simu_m,lat_c,lon_c=st.session_state['order']
            st.divider()
            st.error("LIPA "+str(int(jumla))+" TZS -> NMB "+NMB_ACC)
            kiasi=st.number_input("Uliolipa", 0, step=1000)
            ref=st.text_input("Ref ya NMB")
            if st.button("THIBITISHA MALIPO"):
                if kiasi<jumla:
                    st.error("Pungufu!")
                else:
                    otp=str(random.randint(1000,9999))
                    admin_pesa=jumla*COMMISSION
                    dereva_pesa=jumla-admin_pesa
                    c.execute("INSERT INTO orders (mteja,simu_m,kutoka,kwenda,km,jumla,admin_pesa,dereva_pesa,status,driver_id,lat_c,lon_c,ref,otp,date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(mteja,simu_m,kutoka,kwenda,km,jumla,admin_pesa,dereva_pesa,"pending_admin",did,lat_c,lon_c,ref,otp,str(datetime.now())))
                    conn.commit()
                    st.success("Oda "+str(c.lastrowid)+" OTP "+otp)
                    st.balloons()

elif menu == "Toa Maoni":
    st.subheader("Mpe Dereva Nyota")
    c.execute("SELECT id,jina FROM drivers WHERE verified=1")
    opts=c.fetchall()
    if opts:
        d_map={str(o[0])+" - "+o[1]: o[0] for o in opts}
        sel=st.selectbox("Chagua Dereva", list(d_map.keys()))
        did=d_map[sel]
        mteja_r=st.text_input("Jina lako")
        stars=st.slider("Nyota",1,5,5)
        uj=st.text_area("Ujumbe mf: Alifika haraka")
        if st.button("Tuma Maoni"):
            c.execute("INSERT INTO maoni (driver_id,mteja,stars,ujumbe,date) VALUES (?,?,?,?,?)",(did,mteja_r,stars,uj,str(datetime.now())))
            conn.commit()
            st.success("Asante!")
    c.execute("SELECT d.jina,m.mteja,m.stars,m.ujumbe FROM maoni m JOIN drivers d ON m.driver_id=d.id ORDER BY m.id DESC LIMIT 10")
    for jina,mteja,s,u in c.fetchall():
        st.write(jina+" | "+mteja+" | "+str(s)+" stars - "+u)

elif menu == "LIVE MAP":
    st.subheader("Madereva Live Dar")
    c.execute("SELECT jina,kituo,lat_k,lon_k,aina,bei FROM drivers WHERE verified=1")
    rows=c.fetchall()
    if rows:
        df=pd.DataFrame(rows, columns=["jina","kituo","lat","lon","aina","bei"])
        st.map(df, latitude="lat", longitude="lon")
        for r in rows:
            st.write(r[0]+" - "+r[1]+" - "+r[4]+" - "+str(int(r[5]))+" TZS/KM")
    else:
        st.write("Hakuna dereva bado")

elif menu == "Jisajili Dereva":
    jina=st.text_input("Jina kamili")
    simu=st.text_input("Simu 255...")
    aina=st.selectbox("Aina ya chombo cha usafiri", list(BEI_CONFIG.keys()))
    bei_default=BEI_CONFIG[aina]['bei']
    bei_yangu=st.number_input("Weka Bei yako kwa KM (TZS)", 1000, 100000, bei_default, step=500)
    st.info("Bei ya system kwa "+aina+" ni "+str(bei_default)+" TZS/KM, wewe umeweka "+str(bei_yangu))
    nida=st.text_input("NIDA 20")
    gari=st.text_input("Namba ya gari")
    kituo=st.selectbox("Kituo unapopaki", VITUO)
    picha_cam=st.camera_input("Piga picha ya gari na plate")
    picha_up=st.file_uploader("Au upload picha", type=['jpg','png','jpeg'])
    if st.button("Tuma Maombi"):
        if len(nida)<10:
            st.error("NIDA fupi")
        elif not picha_cam and not picha_up:
            st.error("Piga picha ya gari")
        else:
            path="picha_madereva/"+simu+"_gari.jpg"
            if picha_cam:
                with open(path,"wb") as f:
                    f.write(picha_cam.getbuffer())
            else:
                with open(path,"wb") as f:
                    f.write(picha_up.getbuffer())
            lat_k, lon_k = VITUO_COORDS.get(kituo, (-6.7924, 39.2083))
            c.execute("INSERT INTO drivers (jina,simu,aina,bei,nida,gari,kituo,lat_k,lon_k,picha_gari,verified) VALUES (?,?,?,?,?,?,?,?,?,?,0)",(jina,simu,aina,bei_yangu,nida,gari,kituo,lat_k,lon_k,path))
            conn.commit()
            st.success("Umesajiliwa Bei "+str(bei_yangu)+"/KM Kituo "+kituo+" Subiri Admin")

elif menu == "Dereva - Wallet":
    simu_d=st.text_input("Simu yako")
    if simu_d:
        c.execute("SELECT id,jina,kituo,bei,aina FROM drivers WHERE simu=? AND verified=1",(simu_d,))
        dr=c.fetchone()
        if not dr:
            st.error("Huja-verifywa bado")
            st.stop()
        did,jina,kituo,bei_sasa,aina=dr
        st.write("Karibu "+jina+" | "+aina+" | Kituo "+kituo)
        st.write("Bei yako sasa: "+str(int(bei_sasa))+" TZS/KM")
        bei_mpya=st.number_input("Badilisha Bei mpya kwa KM", 1000, 100000, int(bei_sasa), step=500)
        if st.button("Hifadhi Bei Mpya"):
            c.execute("UPDATE drivers SET bei=? WHERE id=?",(bei_mpya,did))
            conn.commit()
            st.success("Bei imebadilishwa kuwa "+str(bei_mpya)+" TZS/KM")
        c.execute("SELECT balance,total_earned FROM wallets WHERE driver_id=?",(did,))
        w=c.fetchone()
        bal,tot=w if w else (0,0)
        st.metric("Balance", str(int(bal)))
        st.metric("Jumla", str(int(tot)))
        c.execute("SELECT AVG(stars),COUNT(*) FROM maoni WHERE driver_id=?",(did,))
        avg,cnt=c.fetchone()
        if avg:
            st.success("STAR "+str(round(avg,1))+" kutoka kwa wateja "+str(cnt))
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
                            conn.commit()
                            st.success(str(int(d_pesa))+" imeingia")

else:
    pwd=st.text_input("Password Admin", type="password")
    if pwd=="hama123":
        c.execute("SELECT balance FROM admin_wallet WHERE id=1")
        ab=c.fetchone()[0]
        st.metric("Commission yako 5%", str(int(ab)))
        st.divider()
        st.write("Madereva Pending")
        c.execute("SELECT id,jina,simu,aina,bei,kituo,picha_gari FROM drivers WHERE verified=0")
        pend=c.fetchall()
        for i,j,s,a,b,kt,pg in pend:
            with st.container(border=True):
                st.write(j+" | "+s+" | "+a+" | Bei "+str(int(b))+" | "+kt)
                if pg and os.path.exists(pg):
                    st.image(pg, width=180)
                b1,b2=st.columns(2)
                with b1:
                    if st.button("Kubali", key="kubali_"+str(i)):
                        c.execute("UPDATE drivers SET verified=1 WHERE id=?",(i,))
                        conn.commit()
                        st.rerun()
                with b2:
                    if st.button("Futa Pending", key="kataa_"+str(i)):
                        c.execute("DELETE FROM drivers WHERE id=?",(i,))
                        conn.commit()
                        st.rerun()
        st.divider()
        st.write("Madereva Waliokubaliwa")
        c.execute("SELECT id,jina,simu,aina,bei,kituo FROM drivers WHERE verified=1")
        ver=c.fetchall()
        for i,j,s,a,b,kt in ver:
            col1,col2=st.columns([3,1])
            with col1:
                st.write(j+" | "+s+" | "+a+" | Bei "+str(int(b))+"/KM | "+kt)
            with col2:
                if st.button("Futa", key="futa_verified_"+str(i)):
                    c.execute("DELETE FROM drivers WHERE id=?",(i,))
                    c.execute("DELETE FROM wallets WHERE driver_id=?",(i,))
                    c.execute("DELETE FROM maoni WHERE driver_id=?",(i,))
                    conn.commit()
                    st.success(j+" amefutwa")
                    time.sleep(1)
                    st.rerun()
