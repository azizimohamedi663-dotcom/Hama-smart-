import streamlit as st
import sqlite3
import pandas as pd
import random
import time
import math
import os
from datetime import datetime

st.set_page_config(page_title="HAMA SMART ", page_icon="🚚", layout="centered")

NMB_ACC = "22810064566"
NAME="Azizi Frenk Mohamedi"
BASE_FEE = 15000
COMMISSION = 0.05

BEI_CONFIG = {
    "Pikipiki": {"bei": 8000, "max_kg": 50, "desc": "Mizigo <50KG - Document, Chakula kidogo"},
    "Bajaji": {"bei": 12000, "max_kg": 300, "desc": "Mizigo <300KG - TV, Gunia, Mifuko"},
    "Pickup Small": {"bei": 18000, "max_kg": 1000, "desc": "Samani <1 Ton - Fridge, Kiti"},
    "Fuso Small": {"bei": 25000, "max_kg": 3500, "desc": "Mzigo <3.5 Ton - Ujenzi"},
    "Fuso Big": {"bei": 35000, "max_kg": 10000, "desc": "Mzito 10 Ton - Lory"},
}

VITUO = ["Kariakoo","Posta","Ubungo","Mbagala","Tegeta","Mbezi","Kimara","Kigamboni","Msasani","Sinza","Manzese","Tabata","Chanika","Gongo la Mboto","Bunju","Kivukoni","Ilala","Temeke","Kinondoni","Kigoma-Ujiji","Arusha Mjini","Dodoma Mjini","Mwanza Mjini"]

conn = sqlite3.connect('hama_v65_full.db', check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS drivers (id INTEGER PRIMARY KEY, jina TEXT, simu TEXT, aina TEXT, bei REAL, nida TEXT, gari TEXT, kituo TEXT, lat_k REAL, lon_k REAL, picha_gari TEXT, verified INTEGER DEFAULT 0)")
c.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, mteja TEXT, simu_m TEXT, kutoka TEXT, kwenda TEXT, km REAL, jumla REAL, admin_pesa REAL, dereva_pesa REAL, status TEXT, driver_id INTEGER, lat_c REAL, lon_c REAL, ref TEXT UNIQUE, otp TEXT, date TEXT, aina_mzigo TEXT, uzito REAL, thamani REAL, fragile INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY, order_id INTEGER, driver_id INTEGER, nyota INTEGER, maoni TEXT, date TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS wallets (driver_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, total_earned REAL DEFAULT 0, withdrawn REAL DEFAULT 0)")
c.execute("CREATE TABLE IF NOT EXISTS admin_wallet (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, total_comission REAL DEFAULT 0)")
c.execute("CREATE TABLE IF NOT EXISTS blacklist (simu TEXT PRIMARY KEY, reason TEXT)")
c.execute("INSERT OR IGNORE INTO admin_wallet (id,balance,total_comission) VALUES (1,0,0)")
conn.commit()
os.makedirs("picha_madereva", exist_ok=True)

def distance_km(lat1,lon1,lat2,lon2):
    R=6371
    dlat=math.radians(lat2-lat1)
    dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R*2*math.asin(math.sqrt(a))

st.markdown("<style>.orange{background:#FF6B00;padding:18px;border-radius:15px;color:white;text-align:center}.stButton>button{background:#FF6B00;color:white;border-radius:12px;height:50px;font-weight:bold;width:100%}</style><div class='orange'><h1>🚚 HAMA SMART V6.5 FULL</h1><p>PIKIPIKI | BAJAJI | MIZIGO | PICHA | KITUO | WALLET AUTO | LIVE | MAONI</p></div>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("MENU KUU", ["🚚 Mteja - Book Mizigo", "🧑‍✈️ Jisajili Dereva + Picha + Kituo", "🚛 Dereva - Kazi & Wallet", "📦 LIVE MAP + Maoni", "💰 Admin - Wallets & Picha"])

if menu == "🚚 Mteja - Book Mizigo":
    st.subheader("Jaza Taarifa za Mzigo")
    mteja=st.text_input("Jina lako Kamili")
    simu_m=st.text_input("Namba yako ya Simu 255...")
    c.execute("SELECT simu FROM blacklist WHERE simu=?",(simu_m,))
    if c.fetchone():
        st.error("⛔ Namba yako imefungiwa, wasiliana na Admin")
        st.stop()
    col1,col2=st.columns(2)
    with col1:
        kutoka=st.text_input("Mzigo unatoka wapi?","Msasani")
        lat_c=st.number_input("Latitude yako (Lat)", -6.7924, format="%.4f", value=-6.7924)
    with col2:
        kwenda=st.text_input("Mzigo unakwenda wapi?","Kariakoo")
        lon_c=st.number_input("Longitude yako (Lon)", 39.2083, format="%.4f", value=39.2083)
    km=st.number_input("Umbali KM (kadiria)", 1.0, 500.0, 6.5)
    st.divider()
    st.subheader("📦 Taarifa za Mizigo")
    aina_mzigo=st.selectbox("Aina ya Mzigo?", ["Samani","Electronics","Vyombo/Mavazi","Vyakula/Mazao","Ujenzi","Document","Mingine"])
    c1,c2=st.columns(2)
    with c1:
        uzito=st.number_input("Uzito KG", 5, 10000, 30)
    with c2:
        thamani=st.number_input("Thamani ya Mzigo kwa Bima", 0, 50000000, 100000)
    fragile=st.checkbox("⚠️ Mzigo Fragile (Kioo) +10,000 TZS")
    wapakizi=st.checkbox("👷‍♂️ Nahitaji Wapakizi 2 +20,000 TZS")
    extra_uzito=(uzito-500)*50 if uzito>500 else 0
    extra_fragile=10000 if fragile else 0
    extra_wapakizi=20000 if wapakizi else 0
    bima=int(thamani*0.02) if thamani>100000 else 0
    st.map(pd.DataFrame([{"lat":lat_c,"lon":lon_c}]), zoom=13)
    st.info(f"Extra Charges: Uzito {extra_uzito:,.0f} + Fragile {extra_fragile:,.0f} + Wapakizi {extra_wapakizi:,.0f} + Bima {bima:,.0f} = {extra_uzito+extra_fragile+extra_wapakizi+bima:,.0f} TZS")
    st.subheader("Chagua Gari - Wako Karibu Kwanza")
    kituo_filter = st.selectbox("Tafuta madereva wa kituo gani?", ["Vituo Vyote"]+VITUO)
    c.execute("SELECT id,jina,simu,aina,bei,kituo,lat_k,lon_k,picha_gari FROM drivers WHERE verified=1")
    all_drivers=c.fetchall()
    def get_dist(d):
        try:
            if d[6] and d[7]:
                return distance_km(lat_c,lon_c,d[6],d[7])
            else:
                return 9999
        except:
            return 9999
    all_drivers_sorted = sorted(all_drivers, key=get_dist)
    if kituo_filter!= "Vituo Vyote":
        all_drivers_sorted = [d for d in all_drivers_sorted if kituo_filter.lower() in d[5].lower()]
    found=False
    for did,jina,simu,aina,bei,kituo,lat_k,lon_k,picha_gari in all_drivers_sorted:
        conf=BEI_CONFIG.get(aina,{"bei":bei,"max_kg":10000,"desc":""})
        if uzito>conf["max_kg"]:
            continue
        found=True
        c.execute("SELECT AVG(nyota),COUNT(*) FROM reviews WHERE driver_id=?",(did,))
        avg_r,count_r=c.fetchone()
        avg_r=avg_r if avg_r else 5.0
        count_r=count_r if count_r else 0
        stars="⭐"*int(round(avg_r))
        dist_km = distance_km(lat_c,lon_c,lat_k,lon_k) if lat_k and lon_k else 0
        jumla=km*conf["bei"]+BASE_FEE+extra_uzito+extra_fragile+extra_wapakizi+bima
        icon="🏍️" if aina=="Pikipiki" else "🛺" if aina=="Bajaji" else "🚚"
        with st.container(border=True):
            colA,colB=st.columns([1,2])
            with colA:
                if picha_gari and os.path.exists(picha_gari):
                    st.image(picha_gari, width=130, caption=f"{aina}")
                else:
                    st.markdown(f"<h1>{icon}</h1>", unsafe_allow_html=True)
            with colB:
                st.markdown(f"{icon} **{jina}** | {aina}")
                st.markdown(f"📍 Kituo: **{kituo}** - {dist_km:.1f}KM kutoka kwako")
                st.markdown(f"{stars} {avg_r:.1f} ({count_r} maoni) | Max {conf['max_kg']}KG")
                st.markdown(f"💰 **{jumla:,.0f} TZS** - {conf['desc']}")
                if st.button(f"Chagua {jina} - {kituo}", key=f"chagua_{did}"):
                    st.session_state['order']=(did,jina,simu,jumla,km,kutoka,kwenda,mteja,simu_m,lat_c,lon_c,aina_mzigo,uzito,thamani,fragile)
    if not found:
        st.warning("Hakuna gari lenye uwezo wa mzigo huu au kwenye kituo hicho")
    if 'order' in st.session_state:
        did,jina,simu_d,jumla,km,kutoka,kwenda,mteja,simu_m,lat_c,lon_c,aina_mzigo,uzito,thamani,fragile=st.session_state['order']
        st.divider()
        st.error(f"💳 LIPA {jumla:,.0f} TZS → NMB {NMB_ACC} Jina HAMA SMART")
        st.write(f"Baada ya kulipa, Admin 5% = {jumla*COMMISSION:,.0f} na Dereva 95% = {jumla*(1-COMMISSION):,.0f} itagawanyika automatic")
        kiasi=st.number_input("Andika Kiasi Ulicholipa", 0, step=1000)
        ref=st.text_input("Andika Ref Number ya NMB")
        if st.button("THIBITISHA MALIPO"):
            if kiasi<jumla:
                st.error("⛔ NUSU HAIRUHUSIWI - Lipa kamili")
            else:
                c.execute("SELECT ref FROM orders WHERE ref=?",(ref,))
                if c.fetchone():
                    st.error("⛔ Ref hii imeshatumika")
                else:
                    otp=str(random.randint(1000,9999))
                    admin_pesa=jumla*COMMISSION
                    dereva_pesa=jumla*(1-COMMISSION)
                    c.execute("INSERT INTO orders (mteja,simu_m,kutoka,kwenda,km,jumla,admin_pesa,dereva_pesa,status,driver_id,lat_c,lon_c,ref,otp,date,aina_mzigo,uzito,thamani,fragile) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(mteja,simu_m,kutoka,kwenda,km,jumla,admin_pesa,dereva_pesa,"paid_escrow_pending_admin",did,lat_c,lon_c,ref,otp,str(datetime.now()),aina_mzigo,uzito,thamani,1 if fragile else 0))
                    conn.commit()
                    st.success(f"✅ Oda #{c.lastrowid} Imehifadhiwa! Code yako ya kupokelea mzigo ni: {otp} - Fuatilia kwenye LIVE MAP")
                    st.balloons()

elif menu == "🧑‍✈️ Jisajili Dereva + Picha + Kituo":
    st.subheader("Fomu ya Kujiunga - Dereva")
    jina=st.text_input("Jina Kamili Kama NIDA")
    simu=st.text_input("Simu 255...")
    aina=st.selectbox("Aina ya Chombo Unachoendesha", list(BEI_CONFIG.keys()))
    st.info(f"{BEI_CONFIG[aina]['desc']} - Bei {BEI_CONFIG[aina]['bei']:,}/km - Max {BEI_CONFIG[aina]['max_kg']}KG")
    nida=st.text_input("NIDA Namba 20 tarakimu")
    gari=st.text_input("Namba ya Chombo - Mf: T123 ABC / MC 123")
    st.divider()
    st.subheader("📍 Kituo / Kiwanja Unapopaki Chombo Chako")
    st.caption("Mteja akibook karibu na kituo chako utaonekana wa kwanza")
    kituo_select=st.selectbox("Chagua Kituo chako", VITUO)
    kituo_custom=st.text_input("Au Andika Kituo chako kama hakipo hapo juu, Mf: Kiwalani Stendi ya Fuso")
    final_kituo = kituo_custom if kituo_custom.strip()!="" else kituo_select
    colk1,colk2=st.columns(2)
    with colk1:
        lat_k=st.number_input("Lat ya Kituo chako", -12.0, 0.0, -6.7924, format="%.4f")
    with colk2:
        lon_k=st.number_input("Lon ya Kituo chako", 29.0, 41.0, 39.2083, format="%.4f")
    st.caption("Nenda Google Maps, gusa kituo chako, copy Lat Lon")
    st.link_button("Fungua Google Maps Kutafuta Kituo", "https://maps.google.com")
    st.divider()
    st.subheader("📸 Picha ya Chombo - LAZIMA")
    st.warning("Piga picha ambapo namba ya gari inaonekana")
    picha_cam=st.camera_input("📸 Piga Picha ya Gari/Bajaji/Pikipiki")
    picha_upload=st.file_uploader("Au Upload Kutoka Gallery", type=['jpg','jpeg','png'], key="gari_upload")
    picha_license=st.file_uploader("📄 Picha ya Leseni / Card (Optional)", type=['jpg','jpeg','png'], key="les_upload")
    if st.button("Tuma Maombi ya Kujiunga"):
        if len(nida)<18:
            st.error("NIDA lazima 20 tarakimu")
        elif not final_kituo:
            st.error("Weka kituo unapopaki")
        elif not picha_cam and not picha_upload:
            st.error("❌ Lazima upige picha ya chombo!")
        else:
            path_gari=f"picha_madereva/{simu}_gari.jpg"
            if picha_cam:
                with open(path_gari,"wb") as f:
                    f.write(picha_cam.getbuffer())
            elif picha_upload:
                with open(path_gari,"wb") as f:
                    f.write(picha_upload.getbuffer())
            c.execute("INSERT INTO drivers (jina,simu,aina,bei,nida,gari,kituo,lat_k,lon_k,picha_gari,verified) VALUES (?,?,?,?,?,?,?,?,?,?,0)",(jina,simu,aina,BEI_CONFIG[aina]['bei'],nida,gari,final_kituo,lat_k,lon_k,path_gari))
            conn.commit()
            st.success(f"✅ Hongera {jina}! Umesajiliwa kituo {final_kituo}. Subiri Admin akukubali")
            st.balloons()

elif menu == "🚛 Dereva - Kazi & Wallet":
    st.subheader("Ingia na Simu yako")
    simu_d=st.text_input("Simu yako 255...")
    if simu_d:
        c.execute("SELECT id,jina,aina,kituo FROM drivers WHERE simu=? AND verified=1",(simu_d,))
        dr=c.fetchone()
        if not dr:
            st.error("❌ Simu haija-verifywa au haipo. Subiri Admin")
            st.stop()
        did,jina,aina,kituo=dr
        c.execute("SELECT balance,total_earned,withdrawn FROM wallets WHERE driver_id=?",(did,))
        w=c.fetchone()
        bal,tot,withd = w if w else (0,0,0)
        st.subheader(f"💰 Wallet - {jina} | {aina} | 📍 {kituo}")
        col1,col2,col3=st.columns(3)
        col1.metric("Balance Unayodai", f"{bal:,.0f} TZS")
        col2.metric("Jumla Uliyochuma", f"{tot:,.0f} TZS")
        col3.metric("Umeshalipiwa", f"{withd:,.0f} TZS")
        st.info("Balance ndio unayodai sasa - Admin atakulipa M-Pesa mwisho wa wiki")
        with st.expander("📍 Badilisha Kituo Chako"):
            new_kituo=st.selectbox("Chagua kituo kipya", VITUO, key="new_k")
            new_lat=st.number_input("Lat mpya", -12.0, 0.0, -6.7924, format="%.4f", key="nlat")
            new_lon=st.number_input("Lon mpya", 29.0, 41.0, 39.2083, format="%.4f", key="nlon")
            if st.button("Hifadhi Kituo Kipya"):
                c.execute("UPDATE drivers SET kituo=?, lat_k=?, lon_k=? WHERE id=?",(new_kituo,new_lat,new_lon,did))
                conn.commit()
                st.success(f"Kituo sasa {new_kituo}")
        st.divider()
        st.subheader("📦 Kazi Zako")
        c.execute("SELECT id,mteja,simu_m,kutoka,kwenda,km,jumla,dereva_pesa,admin_pesa,status,lat_c,lon_c,otp,aina_mzigo,uzito FROM orders WHERE driver_id=? ORDER BY id DESC",(did,))
        rows=c.fetchall()
        if not rows:
            st.info("Huna oda bado")
        for oid,mteja,simu_m,kutoka,kwenda,km,jumla,d_pesa,a_pesa,status,lat_c,lon_c,otp,aina_mzigo,uzito in rows:
            with st.container(border=True):
                st.markdown(f"**Oda #{oid}** - {mteja} ({simu_m})")
                st.write(f"{kutoka} → {kwenda} | {km}KM | 📦 {aina_mzigo} {uzito}KG | Jumla {jumla:,.0f} → Kwako {d_pesa:,.0f}")
                st.write(f"Status: {status}")
                if "pending_admin" in status:
                    st.warning("⏳ Subiri Admin athibitishe malipo ya mteja")
                elif "paid_verified" in status:
                    st.success("✅ Pesa imethibitishwa - Nenda Kachukue Mzigo")
                    st.map(pd.DataFrame([{"lat":lat_c,"lon":lon_c}]), zoom=13)
                    st.link_button("📍 Fungua Google Maps", f"https://maps.google.com/?q={lat_c},{lon_c}")
                    st.info(f"Code ya Mteja: {otp} - Muombe akupatie ukifika")
                    code_in=st.text_input(f"Ingiza OTP ya Mteja Oda {oid}", key=f"otp_{oid}")
                    pic=st.camera_input(f"📸 Piga Picha Mzigo Ukiwa Umemfikishia Mteja - Oda {oid}", key=f"cam_{oid}")
                    if st.button(f"Maliza Oda {oid} & Ingiza Pesa Wallet", key=f"maliza_{oid}"):
                        if code_in==otp and pic:
                            c.execute("SELECT dereva_pesa,admin_pesa FROM orders WHERE id=?",(oid,))
                            dp,ap=c.fetchone()
                            c.execute("UPDATE orders SET status='completed_auto_wallet' WHERE id=?",(oid,))
                            c.execute("INSERT INTO wallets (driver_id,balance,total_earned) VALUES (?,?,?) ON CONFLICT(driver_id) DO UPDATE SET balance=balance+?, total_earned=total_earned+?", (did,dp,dp,dp,dp))
                            c.execute("UPDATE admin_wallet SET balance=balance+?, total_comission=total_comission+? WHERE id=1", (ap,ap))
                            conn.commit()
                            st.success(f"🎉 Hongera! {dp:,.0f} TZS imeingia Wallet yako! Admin amepata {ap:,.0f}")
                            st.balloons()
                        else:
                            st.error("❌ OTP sio sahihi au haujapiga picha")
                elif "completed_auto_wallet" in status:
                    st.success(f"✅ Ulikamilisha - {d_pesa:,.0f} iliingia Wallet")

elif menu == "📦 LIVE MAP + Maoni":
    st.subheader("📍 Fuatilia Gari Live + Mpe Nyota")
    oid=st.text_input("Andika Oda ID yako, Mf: 1")
    if oid:
        try:
            c.execute("SELECT lat_c,lon_c,status,otp,aina_mzigo,driver_id,mteja FROM orders WHERE id=?",(int(oid),))
            r=c.fetchone()
            if not r:
                st.error("Oda haipo")
            else:
                lat_c,lon_c,status,otp,aina_mzigo,did,mteja=r
                st.write(f"**{mteja}** | 📦 {aina_mzigo} | Status: {status} | Code: **{otp}**")
                if 'live_prog' not in st.session_state:
                    st.session_state.live_prog=0
                auto=st.checkbox("🔴 LIVE Auto Update", value=True)
                if auto:
                    if st.session_state.live_prog<100:
                        st.session_state.live_prog+=4
                    prog=st.session_state.live_prog
                    st.caption(f"🔴 LIVE - Gari lipo {prog}% njiani")
                    time.sleep(3)
                    st.rerun()
                else:
                    prog=st.slider("Sogeza Gari Manual", 0, 100, st.session_state.live_prog)
                    st.session_state.live_prog=prog
                lat_d=lat_c+(1-prog/100)*0.12
                lon_d=lon_c+(1-prog/100)*0.12
                km_left=distance_km(lat_c,lon_c,lat_d,lon_d)
                c1,c2,c3=st.columns(3)
                c1.metric("KM Iliyobaki", f"{km_left:.1f}")
                c2.metric("Dakika", f"{int(km_left*3)} min")
                c3.metric("%", f"{prog}%")
                df_map=pd.DataFrame([{"lat":lat_c,"lon":lon_c,"name":"Wewe"},{"lat":lat_d,"lon":lon_d,"name":"Gari"}])
                st.map(pd.DataFrame([{"lat":lat_c,"lon":lon_c},{"lat":lat_d,"lon":lon_d}]), zoom=12)
                if prog>=100:
                    st.balloons()
                    st.success(f"✅ Gari limefika! Mpe dereva Code: {otp}")
                    st.divider()
                    st.subheader("⭐ Mpe Dereva Nyota")
                    c.execute("SELECT id FROM reviews WHERE order_id=?",(int(oid),))
                    if c.fetchone():
                        st.info("✅ Umeshamtupia maoni dereva huyu")
                    else:
                        nyota=st.slider("Chagua Nyota 1-5", 1, 5, 5)
                        maoni_txt=st.text_area("Andika Maoni yako kwa Dereva")
                        if st.button("Tuma Maoni"):
                            c.execute("INSERT INTO reviews (order_id,driver_id,nyota,maoni,date) VALUES (?,?,?,?,?)",(int(oid),did,nyota,maoni_txt,str(datetime.now())))
                            conn.commit()
                            st.success("🙏 Asante kwa maoni!")
        except:
            st.error("Oda ID lazima iwe namba")

else:
    st.subheader("💰 Admin Panel - V6.5 FULL")
    c.execute("SELECT balance,total_comission FROM admin_wallet WHERE id=1")
    ab,at=c.fetchone()
    col1,col2=st.columns(2)
    col1.metric("💵 Comission Yako (Balance)", f"{ab:,.0f} TZS")
    col2.metric("📈 Total Comission Yote", f"{at:,.0f} TZS")
    st.divider()
    st.subheader("⏳ Madereva Wanaosubiri - Angalia Picha + Kituo")
    c.execute("SELECT id,jina,simu,aina,nida,gari,kituo,lat_k,lon_k,picha_gari FROM drivers WHERE verified=0 ORDER BY id DESC")
    pending=c.fetchall()
    if not pending:
        st.info("Hakuna dereva pending")
    for i,j,s,a,n,g,kt,ltk,lnk,pg in pending:
        with st.container(border=True):
            col1,col2=st.columns([1,1])
            with col1:
                st.markdown(f"**{j}** | {s} | {a}")
                st.write(f"NIDA: {n}")
                st.write(f"Gari: {g}")
                st.write(f"📍 Kituo: **{kt}**")
                st.write(f"Lat {ltk} Lon {lnk}")
                st.link_button("📍 Ona Kituo Google Maps", f"https://maps.google.com/?q={ltk},{lnk}")
            with col2:
                if pg and os.path.exists(pg):
                    st.image(pg, caption=f"Picha ya {a} - {g}", width=250)
                else:
                    st.warning("Hakuna picha ya chombo")
                c1,c2=st.columns(2)
                with c1:
                    if st.button(f"✅ Kubali {
