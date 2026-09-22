import streamlit as st
import sqlite3, pandas as pd, random, time, math, os
from datetime import datetime

st.set_page_config(page_title="HAMA SMART", page_icon="🚚", layout="centered")

NMB_ACC = "22810064566"
BASE_FEE = 15000
COMMISSION = 0.05

BEI_CONFIG = {
    "Pikipiki": {"bei": 8000, "max_kg": 50, "desc": "Mizigo <50KG"},
    "Bajaji": {"bei": 12000, "max_kg": 300, "desc": "Mizigo <300KG"},
    "Pickup Small": {"bei": 18000, "max_kg": 1000, "desc": "Samani <1 Ton"},
    "Fuso Small": {"bei": 25000, "max_kg": 3500, "desc": "<3.5 Ton"},
    "Fuso Big": {"bei": 35000, "max_kg": 10000, "desc": "10 Ton"},
}
VITUO = ["Kariakoo","Posta","Ubungo","Mbagala","Tegeta","Mbezi","Kimara","Kigamboni","Msasani","Sinza","Manzese","Tabata","Chanika","Bunju","Kivukoni","Ilala","Temeke","Kinondoni"]

conn = sqlite3.connect('hama_v65_fixed.db', check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS drivers (id INTEGER PRIMARY KEY, jina TEXT, simu TEXT, aina TEXT, bei REAL, nida TEXT, gari TEXT, kituo TEXT, lat_k REAL, lon_k REAL, picha_gari TEXT, verified INTEGER DEFAULT 0)")
c.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, mteja TEXT, simu_m TEXT, kutoka TEXT, kwenda TEXT, km REAL, jumla REAL, admin_pesa REAL, dereva_pesa REAL, status TEXT, driver_id INTEGER, lat_c REAL, lon_c REAL, ref TEXT UNIQUE, otp TEXT, date TEXT, aina_mzigo TEXT, uzito REAL, thamani REAL, fragile INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY, order_id INTEGER, driver_id INTEGER, nyota INTEGER, maoni TEXT, date TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS wallets (driver_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, total_earned REAL DEFAULT 0, withdrawn REAL DEFAULT 0)")
c.execute("CREATE TABLE IF NOT EXISTS admin_wallet (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, total_comission REAL DEFAULT 0)")
c.execute("INSERT OR IGNORE INTO admin_wallet (id,balance,total_comission) VALUES (1,0,0)")
conn.commit()
os.makedirs("picha_madereva", exist_ok=True)

def distance_km(lat1,lon1,lat2,lon2):
    R=6371
    dlat=math.radians(lat2-lat1)
    dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R*2*math.asin(math.sqrt(a))

st.markdown("<style>.orange{background:#FF6B00;padding:18px;border-radius:15px;color:white;text-align:center}.stButton>button{background:#FF6B00;color:white;border-radius:12px;height:50px;font-weight:bold;width:100%}</style><div class='orange'><h1>HAMA SMART V6.5 FIXED</h1><p>PICHA + KITUO + WALLET AUTO</p></div>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("MENU", ["Mteja - Book", "Jisajili Dereva", "Dereva - Wallet", "LIVE MAP", "Admin"])

if menu == "Mteja - Book":
    mteja=st.text_input("Jina"); simu_m=st.text_input("Simu 255...")
    col1,col2=st.columns(2)
    with col1: kutoka=st.text_input("Kutoka","Msasani"); lat_c=st.number_input("Lat", -6.7924, format="%.4f")
    with col2: kwenda=st.text_input("Kwenda","Kariakoo"); lon_c=st.number_input("Lon", 39.2083, format="%.4f")
    km=st.number_input("KM",1.0,500.0,6.5)
    aina_mzigo=st.selectbox("Mzigo?", ["Samani","Electronics","Vyakula","Ujenzi","Document","Mingine"])
    c1,c2=st.columns(2)
    with c1: uzito=st.number_input("KG",5,10000,30)
    with c2: thamani=st.number_input("Thamani",0,50000000,100000)
    fragile=st.checkbox("Fragile +10k"); wapakizi=st.checkbox("Wapakizi +20k")
    extra = (uzito-500)*50 if uzito>500 else 0
    if fragile: extra+=10000
    if wapakizi: extra+=20000
    bima=int(thamani*0.02) if thamani>100000 else 0
    st.map(pd.DataFrame([{"lat":lat_c,"lon":lon_c}]), zoom=13)
    kituo_filter=st.selectbox("Kituo", ["Vyote"]+VITUO)
    c.execute("SELECT id,jina,simu,aina,bei,kituo,lat_k,lon_k,picha_gari FROM drivers WHERE verified=1")
    drivers=c.fetchall()
    def get_d(d):
        try: return distance_km(lat_c,lon_c,d[6],d[7]) if d[6] else 999
        except: return 999
    drivers=sorted(drivers,key=get_d)
    if kituo_filter!="Vyote": drivers=[d for d in drivers if kituo_filter.lower() in d[5].lower()]
    for did,jina,simu,aina,bei,kituo,lat_k,lon_k,picha in drivers:
        conf=BEI_CONFIG.get(aina,{"bei":bei,"max_kg":10000})
        if uzito>conf["max_kg"]: continue
        jumla=km*conf["bei"]+BASE_FEE+extra+bima
        with st.container(border=True):
            colA,colB=st.columns([1,2])
            with colA:
                if picha and os.path.exists(picha): st.image(picha,width=120)
            with colB:
                st.write(jina+" | "+aina+" | Kituo "+kituo)
                st.write(str(round(get_d((0,0,0,0,0,0,lat_k,lon_k,0)),1))+"KM | "+str(int(jumla))+" TZS")
                btn_key="c"+str(did)
                if st.button("Chagua "+jina, key=btn_key):
                    st.session_state['order']=(did,jina,simu,jumla,km,kutoka,kwenda,mteja,simu_m,lat_c,lon_c,aina_mzigo,uzito,thamani)
    if 'order' in st.session_state:
        did,jina,simu_d,jumla,km,kutoka,kwenda,mteja,simu_m,lat_c,lon_c,aina_mzigo,uzito,thamani=st.session_state['order']
        st.error("LIPA "+str(int(jumla))+" -> NMB "+NMB_ACC)
        kiasi=st.number_input("Kiasi",0,step=1000); ref=st.text_input("Ref NMB")
        if st.button("THIBITISHA"):
            if kiasi<jumla: st.error("NUSU HAIRUHUSIWI")
            else:
                otp=str(random.randint(1000,9999))
                admin_pesa=jumla*COMMISSION; dereva_pesa=jumla*(1-COMMISSION)
                c.execute("INSERT INTO orders (mteja,simu_m,kutoka,kwenda,km,jumla,admin_pesa,dereva_pesa,status,driver_id,lat_c,lon_c,ref,otp,date,aina_mzigo,uzito,thamani,fragile) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(mteja,simu_m,kutoka,kwenda,km,jumla,admin_pesa,dereva_pesa,"pending_admin",did,lat_c,lon_c,ref,otp,str(datetime.now()),aina_mzigo,uzito,thamani,0))
                conn.commit(); st.success("Oda "+str(c.lastrowid)+" Code "+otp)

elif menu == "Jisajili Dereva":
    jina=st.text_input("Jina NIDA"); simu=st.text_input("Simu 255..."); aina=st.selectbox("Aina", list(BEI_CONFIG.keys()))
    nida=st.text_input("NIDA 20"); gari=st.text_input("Namba ya Chombo")
    kituo=st.selectbox("Kituo unapopaki", VITUO)
    kituo_custom=st.text_input("Kituo kingine kama hakipo")
    final_kituo=kituo_custom if kituo_custom else kituo
    lat_k=st.number_input("Lat ya Kituo", -6.7924, format="%.4f"); lon_k=st.number_input("Lon ya Kituo", 39.2083, format="%.4f")
    picha_cam=st.camera_input("Piga picha ya chombo")
    picha_up=st.file_uploader("Au upload", type=['jpg','png','jpeg'])
    if st.button("Tuma Maombi"):
        if len(nida)<18: st.error("NIDA sio sahihi")
        elif not picha_cam and not picha_up: st.error("Piga picha ya chombo")
        else:
            path="picha_madereva/"+simu+"_gari.jpg"
            if picha_cam:
                with open(path,"wb") as f: f.write(picha_cam.getbuffer())
            elif picha_up:
                with open(path,"wb") as f: f.write(picha_up.getbuffer())
            c.execute("INSERT INTO drivers (jina,simu,aina,bei,nida,gari,kituo,lat_k,lon_k,picha_gari,verified) VALUES (?,?,?,?,?,?,?,?,?,?,0)",(jina,simu,aina,BEI_CONFIG[aina]['bei'],nida,gari,final_kituo,lat_k,lon_k,path))
            conn.commit(); st.success("Umesajiliwa Kituo "+final_kituo); st.balloons()

elif menu == "Dereva - Wallet":
    simu_d=st.text_input("Simu yako")
    if simu_d:
        c.execute("SELECT id,jina,kituo FROM drivers WHERE simu=? AND verified=1",(simu_d,)); dr=c.fetchone()
        if not dr: st.error("Huja-verifywa"); st.stop()
        did,jina,kituo=dr
        c.execute("SELECT balance,total_earned,withdrawn FROM wallets WHERE driver_id=?",(did,)); w=c.fetchone(); bal,tot,withd=w if w else (0,0,0)
        st.subheader(jina+" - Kituo "+kituo)
        c1,c2,c3=st.columns(3); c1.metric("Balance",str(int(bal))); c2.metric("Jumla",str(int(tot))); c3.metric("Umelipiwa",str(int(withd)))
        c.execute("SELECT id,mteja,jumla,dereva_pesa,status,lat_c,lon_c,otp FROM orders WHERE driver_id=? ORDER BY id DESC",(did,))
        for oid,mteja,jumla,d_pesa,status,lat_c,lon_c,otp in c.fetchall():
            with st.container(border=True):
                st.write("Oda "+str(oid)+" "+mteja+" "+str(int(jumla))+" -> Kwako "+str(int(d_pesa))+" - "+status)
                if "verified" in status:
                    code_in=st.text_input("OTP "+str(oid), key="otp"+str(oid))
                    pic=st.camera_input("Picha mzigo "+str(oid), key="pic"+str(oid))
                    if st.button("Maliza "+str(oid), key="fin"+str(oid)):
                        if code_in==otp and pic:
                            c.execute("SELECT dereva_pesa,admin_pesa FROM orders WHERE id=?",(oid,)); dp,ap=c.fetchone()
                            c.execute("UPDATE orders SET status='completed' WHERE id=?",(oid,))
                            c.execute("INSERT INTO wallets (driver_id,balance,total_earned) VALUES (?,?,?) ON CONFLICT(driver_id) DO UPDATE SET balance=balance+?, total_earned=total_earned+?", (did,dp,dp,dp,dp))
                            c.execute("UPDATE admin_wallet SET balance=balance+?, total_comission=total_comission+? WHERE id=1", (ap,ap))
                            conn.commit(); st.success(str(int(dp))+" imeingia Wallet")

elif menu == "LIVE MAP":
    oid=st.text_input("Oda ID")
    if oid:
        c.execute("SELECT lat_c,lon_c,status,otp FROM orders WHERE id=?",(oid,)); r=c.fetchone()
        if r:
            lat_c,lon_c,status,otp=r; st.write(status+" Code "+otp)
            prog=st.slider("Progress",0,100,50)
            lat_d=lat_c+(1-prog/100)*0.12; lon_d=lon_c+(1-prog/100)*0.12
            st.map(pd.DataFrame([{"lat":lat_c,"lon":lon_c},{"lat":lat_d,"lon":lon_d}]), zoom=12)
            if prog>=100: st.success("Fika Code "+otp)

else:
    st.subheader("Admin Panel FIXED")
    c.execute("SELECT balance,total_comission FROM admin_wallet WHERE id=1"); ab,at=c.fetchone(); st.metric("Comission", str(int(ab)))
    st.divider()
    st.write("Madereva Pending")
    c.execute("SELECT id,jina,simu,aina,nida,gari,kituo,lat_k,lon_k,picha_gari FROM drivers WHERE verified=0")
    for i,j,s,a,n,g,kt,ltk,lnk,pg in c.fetchall():
        with st.container(border=True):
            st.write(j+" | "+s+" | "+a+" | Kituo "+kt)
            if pg and os.path.exists(pg): st.image(pg,width=200)
            col1,col2=st.columns(2)
            with col1:
                if st.button("Kubali "+j, key="av"+str(i)):
                    c.execute("UPDATE drivers SET verified=1 WHERE id=?",(i,)); conn.commit(); st.success("OK")
            with col2:
                if st.button("Kataa "+j, key="re"+str(i)):
                    c.execute("DELETE FROM drivers WHERE id=?",(i,)); conn.commit(); st.error("Deleted")
    st.divider()
    c.execute("SELECT id,mteja,jumla,ref FROM orders WHERE status='pending_admin'")
    for oid,mteja,jumla,ref in c.fetchall():
        st.write("Oda "+str(oid)+" "+mteja+" "+str(int(jumla))+" Ref "+ref)
        if st.button("Thibitisha "+str(oid), key="ap"+str(oid)):
            c.execute("UPDATE orders SET status='paid_verified' WHERE id=?",(oid,)); conn.commit()
