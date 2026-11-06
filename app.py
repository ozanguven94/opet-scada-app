import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="OPET Marmara Ereğlisi SCADA",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- OPET KURUMSAL MAĞAZA / LIGHT MODE (AÇIK TEMA) & CSS ---
st.markdown("""
    <style>
    .main { background-color: #f0f4f8; color: #1f2937; }
    .stSidebar { background-color: #002d62; border-right: 1px solid #001f3f; }
    .stSidebar *, .stSidebar label, .stSidebar span, .stSidebar p { color: #ffffff !important; }
    h1, h2, h3 { color: #003366; font-family: 'Segoe UI', Tahoma, sans-serif; }
    .stButton>button {
        width: 100%;
        background-color: #004080;
        color: #ffffff;
        border: 1px solid #0059b3;
        border-radius: 6px;
        text-align: left;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .stButton>button:hover {
        background-color: #0059b3;
        border-color: #ffffff;
        color: #ffffff;
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

# HTML/CSS tabanlı kusursuz ve hızlı OPET Kurumsal Logo Bileşeni
OPET_LOGO_HTML = """
<div style="display: flex; align-items: center; gap: 10px; padding: 10px 0; margin-bottom: 10px;">
    <div style="display: flex; flex-direction: column; gap: 4px; width: 28px;">
        <div style="background-color: #0072CE; height: 4px; width: 16px; border-radius: 2px;"></div>
        <div style="background-color: #0072CE; height: 4px; width: 22px; border-radius: 2px;"></div>
        <div style="background-color: #0072CE; height: 4px; width: 28px; border-radius: 2px;"></div>
    </div>
    <span style="color: #0072CE; font-weight: 900; font-size: 36px; font-style: italic; font-family: 'Segoe UI', Tahoma, sans-serif; letter-spacing: -2px; line-height: 1;">opet</span>
</div>
"""

SHEET_ID = "17htReQxvrsjLw8Cf6ES25GsuHBnKFIN3Gh2aH5XkoYI"
TANKLAR_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Tanklar"
ADBLUE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=AdBlue_Proses"

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown(OPET_LOGO_HTML, unsafe_allow_html=True)
        st.title("🔒 Terminal SCADA Girişi")
        st.caption("Marmara Ereğlisi Akaryakıt Depolama Terminali")
        with st.form("login_form"):
            username = st.text_input("Kullanıcı Adı")
            password = st.text_input("Şifre", type="password")
            submit = st.form_submit_button("Güvenli Giriş Yap")
            if submit:
                if username == "opet@ozanguven" and password == "terminal59":
                    st.session_state['authenticated'] = True
                    st.rerun()
                else:
                    st.error("Hatalı kullanıcı adı veya şifre!")
    st.stop()

@st.cache_data(ttl=5)
def load_data():
    try:
        df_tank = pd.read_csv(TANKLAR_URL)
        df_adblue = pd.read_csv(ADBLUE_URL)
        return df_tank, df_adblue
    except Exception as e:
        return None, None

df_tank, df_adblue = load_data()

if 'aktif_sayfa' not in st.session_state:
    st.session_state['aktif_sayfa'] = "🔍 Tank Özel İnceleme (3D Matris)"

# --- SOL MENÜ (OPET LOGO & BUTONLAR) ---
with st.sidebar:
    st.markdown(OPET_LOGO_HTML, unsafe_allow_html=True)
    st.markdown("### Terminal SCADA v5.1")
    st.markdown("---")
    st.markdown("**Operatör:** Ozan Güven")
    st.markdown("**Lokasyon:** Marmara Ereğlisi")
    st.markdown("---")
    
    st.markdown("📂 **KONTROL ODASI MENÜSÜ**")
    
    sayfalar = [
        "🔍 Tank Özel İnceleme (3D Matris)",
        "⛽ Genel Tank Envanteri & Dağılım",
        "🧮 ASTM D1250 Toplu Mutabakat",
        "🔀 Hat & Transfer Rotaları",
        "🌊 Gantry & Koç Darbesi Simülasyonu",
        "🔌 Modbus TCP / PLC Canlı Bağlantı",
        "🛠️ Kestirimci Bakım & Titreşim",
        "⚡ Katodik Koruma & Telemetri",
        "💨 VRU Buhar Geri Kazanım",
        "♨️ Tank Isıtma & Serpantin",
        "🛡️ Saha LEL & Yangın Emniyeti",
        "🚨 SEVESO & ESD Matrisi",
        "💧 AdBlue Üretim Hattı",
        "🧪 ISO 22241 Lab & Blending",
        "🚨 Sistem Alarmları",
        "📝 Vardiya Teslim & Notlar"
    ]
    
    for sayfa in sayfalar:
        if st.button(sayfa):
            st.session_state['aktif_sayfa'] = sayfa
            st.rerun()
    
    st.markdown("---")
    st.markdown(f"🟢 **Sistem Saati:** {datetime.now().strftime('%H:%M:%S')}")

aktif_sayfa = st.session_state['aktif_sayfa']

# ==========================================
# 1. TANK ÖZEL İNCELEME (3D MATRİS)
# ==========================================
if aktif_sayfa == "🔍 Tank Özel İnceleme (3D Matris)":
    st.subheader("🔎 Tank Özel İnceleme & Kapsamlı Mühendislik Veri Matrisi")
    if df_tank is not None and not df_tank.empty:
        selected_tank_id = st.selectbox("İncelemek İstediğiniz Tankı Seçin:", df_tank['Tank_ID'].unique())
        tank_data = df_tank[df_tank['Tank_ID'] == selected_tank_id].iloc[0]
        
        kapasite = float(tank_data.get('Kapasite_m3', 0))
        hacim = float(tank_data.get('Hacim_m3', 0))
        doluluk = float(tank_data.get('Doluluk_Yuzde', 0))
        sicaklik = float(tank_data.get('Sicaklik_C', 15.0))
        urun = str(tank_data.get('Urun', '-'))
        durum = str(tank_data.get('Durum', 'Normal'))
        bosluk = kapasite - hacim
        default_dens = 845.0 if "Benzin" in urun else (835.0 if "Motorin" in urun else 1090.0)

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Ürün Türü", urun)
        m2.metric("Doluluk Oranı", f"%{doluluk}")
        m3.metric("Mevcut Hacim", f"{hacim:,.1f} m³")
        m4.metric("Kalan Boş Alan", f"{bosluk:,.1f} m³")
        m5.metric("Tank Sıcaklığı", f"{sicaklik} °C")

        st.divider()
        col_anim, col_specs = st.columns([1, 1.5])

        with col_anim:
            fill_color = "#28a745" if doluluk < 85 else "#dc3545"
            if doluluk <= 15:
                fill_color = "#ffc107"

            tank_3d_html = f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; padding: 5px;">
                <div style="position: relative; width: 160px; height: 260px; border: 5px solid #002d62; border-radius: 80px/25px; background: linear-gradient(90deg, #e0e6ed 0%, #ffffff 50%, #e0e6ed 100%); overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.15), inset 0 0 15px rgba(0,0,0,0.1);">
                    <div style="position: absolute; top: -5px; width: 100%; height: 18px; background: #004080; border-radius: 50%; z-index: 20; border: 2px solid #002d62;"></div>
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 100%; text-align: center; color: #002d62; font-weight: 900; font-size: 20px; z-index: 25;">
                        %{doluluk:.1f}
                    </div>
                    <div style="position: absolute; bottom: 0; width: 100%; height: {doluluk}%; background: linear-gradient(90deg, {fill_color}aa 0%, {fill_color} 50%, {fill_color}aa 100%); transition: height 1s ease-in-out; opacity: 0.9;">
                        <div style="position: absolute; top: -8px; left: 0; width: 100%; height: 12px; background: rgba(255,255,255,0.6); border-radius: 50%;"></div>
                    </div>
                    <div style="position: absolute; bottom: -5px; width: 100%; height: 18px; background: #004080; border-radius: 50%; z-index: 20; border: 2px solid #002d62;"></div>
                </div>
                <div style="margin-top: 10px; font-weight: bold; font-size: 15px; color: #003366; text-align: center;">
                    {selected_tank_id} - {durum}
                </div>
            </div>
            """
            st.components.v1.html(tank_3d_html, height=330)

        with col_specs:
            spec_data = {
                "Parametre": [
                    "Çatı Tipi", "Nominal Tasarım Kapasitesi", "Yüksek-Yüksek Alarmlı Limit (HH)", 
                    "Yüksek Seviye Alarmı (H)", "Kritik Düşük Limit (LL)", "Mevcut Seviye Yüksekliği",
                    "Bağlı Bund (Havuz) ID", "Son Kalibrasyon Tarihi"
                ],
                "Değer": [
                    "Yüzer Çatı" if "Benzin" in urun or "Motorin" in urun else "Konik Çatı",
                    f"{kapasite:,.0f} m³", f"%95.0 ({kapasite * 0.95:,.1f} m³)",
                    f"%85.0 ({kapasite * 0.85:,.1f} m³)", f"%15.0 ({kapasite * 0.15:,.1f} m³)",
                    f"{(hacim / kapasite) * 18.5:.2f} Metre (Simüle)",
                    "Bund Area 03 (SEVESO Zone II)", "14.05.2025 (API MPMS)"
                ]
            }
            st.dataframe(pd.DataFrame(spec_data), use_container_width=True, hide_index=True)

        st.divider()
        calc_c1, calc_c2 = st.columns(2)
        with calc_c1:
            st.markdown("#### 🧮 ASTM D1250 VCF & Kütle Mutabakatı")
            t_input = st.number_input("Gözlenen Sıcaklık (°C)", value=sicaklik, step=0.1)
            d_input = st.number_input("15°C Referans Yoğunluk (kg/m³)", value=default_dens, step=0.5)
            vcf_val = 1.0 - ((t_input - 15.0) * 0.00084)
            v15_val = hacim * vcf_val
            net_ton = (v15_val * d_input) / 1000.0
            st.info(f"• **VCF Katsayısı:** `{vcf_val:.5f}`\n• **15°C Standart Hacim:** `{v15_val:,.1f} m³`\n• **Net Kütle:** `{net_ton:,.2f} Ton`")
        with calc_c2:
            st.markdown("#### ⏱️ Anlık Transfer & Dolum Süresi")
            transfer_debi = st.number_input("Operasyonel Pompa Debisi (m³/h):", value=350.0, step=25.0)
            if transfer_debi > 0:
                kalan_sure_saat = bosluk / transfer_debi
                st.success(f"• **Kalan Boş Hacim:** `{bosluk:,.1f} m³`\n• **Doluma Kalan Süre:** `{kalan_sure_saat:.2f} Saat` ({int(kalan_sure_saat*60)} Dk)")
            else:
                st.warning("⚠️ Debi 0 m³/h.")

# ==========================================
# 2. GENEL TANK ENVANTERİ & DAĞILIM
# ==========================================
elif aktif_sayfa == "⛽ Genel Tank Envanteri & Dağılım":
    st.subheader("Terminal Tank Seviyeleri ve Stok Dağılımı")
    if df_tank is not None and not df_tank.empty:
        f_col1, f_col2, f_col3 = st.columns([1, 1, 1])
        with f_col1:
            urun_listesi = ["TÜMÜ"] + list(df_tank['Urun'].dropna().unique())
            secilen_urun = st.selectbox("Ürüne Göre Filtrele", urun_listesi)
        with f_col2:
            search_tank = st.text_input("🔍 Tank Koduna Göre Arama", "")
        with f_col3:
            st.write("")
            st.write("")
            csv_data = df_tank.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Raporu İndir (.csv)", data=csv_data, file_name="OPET_Tank_Raporu.csv", mime="text/csv")

        filtered_df = df_tank.copy()
        if secilen_urun != "TÜMÜ":
            filtered_df = filtered_df[filtered_df['Urun'] == secilen_urun]
        if search_tank.strip() != "":
            filtered_df = filtered_df[filtered_df['Tank_ID'].astype(str).str.contains(search_tank.strip(), case=False, na=False)]

        col_left, col_right = st.columns([2, 1])
        with col_left:
            fig = px.bar(filtered_df, x='Tank_ID', y='Doluluk_Yuzde', color='Doluluk_Yuzde', color_continuous_scale=['green', 'yellow', 'red'], text='Doluluk_Yuzde', title="Tank Doluluk Oranları (%)", height=400)
            fig.update_traces(texttemplate='%{text}%', textposition='outside')
            fig.update_layout(yaxis=dict(range=[0, 115]), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        with col_right:
            fig_pie = px.pie(df_tank, names='Urun', values='Hacim_m3', hole=0.4)
            fig_pie.update_layout(margin=dict(t=20, b=20, l=10, r=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_pie, use_container_width=True)
        st.dataframe(filtered_df[['Tank_ID', 'Urun', 'Kapasite_m3', 'Doluluk_Yuzde', 'Hacim_m3', 'Sicaklik_C', 'Durum']], use_container_width=True)

# ==========================================
# 3. ASTM D1250 TOPLU MUTABAKAT
# ==========================================
elif aktif_sayfa == "🧮 ASTM D1250 Toplu Mutabakat":
    st.subheader("🧮 API MPMS / ASTM D1250 Otomatik Toplu Mutabakat Motoru")
    if df_tank is not None and not df_tank.empty:
        batch_df = df_tank.copy()
        batch_df['VCF'] = 1.0 - ((batch_df['Sicaklik_C'] - 15.0) * 0.00084)
        batch_df['V15_Hacim_m3'] = batch_df['Hacim_m3'] * batch_df['VCF']
        batch_df['Birim_Yogunluk'] = batch_df['Urun'].apply(lambda x: 845.0 if "Benzin" in str(x) else (835.0 if "Motorin" in str(x) else 1090.0))
        batch_df['Net_Kutle_Ton'] = (batch_df['V15_Hacim_m3'] * batch_df['Birim_Yogunluk']) / 1000.0
        st.dataframe(batch_df[['Tank_ID', 'Urun', 'Hacim_m3', 'Sicaklik_C', 'VCF', 'V15_Hacim_m3', 'Net_Kutle_Ton']], use_container_width=True, hide_index=True)
        t_toplam_ton = batch_df['Net_Kutle_Ton'].sum()
        st.success(f"📊 **Terminal Geneli Toplam Net Stok Mutabakatı:** `{t_toplam_ton:,.2f} Metrik Ton`")

# ==========================================
# 4. HAT & TRANSFER ROTALARI
# ==========================================
elif aktif_sayfa == "🔀 Hat & Transfer Rotaları":
    st.subheader("🔀 Canlı Transfer & Manifold Rotaları")
    r1, r2, r3 = st.columns(3)
    r1.success("🟢 **Hat 01 (Benzin Transferi)**\n\n• Kaynak: `T-121`\n• Pompa: `P-101A` (350 m³/h)\n• Hedef: `Dolum Adası 02`\n• Vana: **AÇIK (%100)**")
    r2.info("🔵 **Hat 02 (Motorin Transferi)**\n\n• Kaynak: `T-204`\n• Pompa: `P-202B` (Hazırda)\n• Hedef: `İskele Manifold 01`\n• Vana: **KAPALI (%0)**")
    r3.warning("🟡 **Hat 03 (AdBlue Besleme)**\n\n• Kaynak: `AdBlue Stok`\n• Pompa: `P-301` (15 Ton/h)\n• Hedef: `Paketleme / IBC`\n• Vana: **MODÜLE EDİLİYOR**")

# ==========================================
# 5. GANTRY & KOÇ DARBESİ SİMÜLASYONU
# ==========================================
elif aktif_sayfa == "🌊 Gantry & Koç Darbesi Simülasyonu":
    st.subheader("🌊 Gantry (Dolum Adaları) Akışkan Dinamiği & Koç Darbesi")
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        gantry_sec = st.selectbox("Dolum Adası Seçin:", ["Gantry 01 (Üstten Benzin)", "Gantry 02 (Alttan Motorin)", "Gantry 03 (Alttan Motorin)", "Gantry 04 (AdBlue)"])
        hat_uzunlugu = st.slider("Hat Uzunluğu (m)", 50, 500, 150)
        akıs_hizi = st.slider("Akışkan Hızı (m/s) [Optimum: 1.5 - 3.0]", 0.5, 5.0, 2.5)
        su_yogunluk = 840.0
        dalga_hizi = 1200.0
        koc_darbesi_bar = (su_yogunluk * dalga_hizi * akıs_hizi) / 100000.0
        st.info(f"• **Anlık Akış Hızı:** `{akıs_hizi} m/s`\n• **Tahmini Koç Darbesi Basınç Tepe Değeri ($\Delta P$):** `{koc_darbesi_bar:.2f} Bar`")
        if koc_darbesi_bar > 25.0:
            st.error("🚨 KRİTİK: Ani vana kapanması durumunda basınç sınırı aşabilir!")
        else:
            st.success("✅ Hidrolik dalgalanma güvenli sınırda.")
    with g_col2:
        gantry_data = {
            "Ada No": ["Gantry 01", "Gantry 02", "Gantry 03", "Gantry 04"],
            "Tip": ["Üstten Benzin", "Alttan Motorin", "Alttan Motorin", "AdBlue Dolum"],
            "Sayaç Hızı (L/dk)": [1250, 2400, 2350, 450],
            "Preset Valf": ["%100 Açık", "Regüle Ediliyor", "%100 Açık", "Kapalı"],
            "Basınç (Bar)": [4.2, 5.1, 4.9, 3.5]
        }
        st.dataframe(pd.DataFrame(gantry_data), use_container_width=True, hide_index=True)

# ==========================================
# 6. MODBUS TCP / PLC CANLI BAĞLANTI
# ==========================================
elif aktif_sayfa == "🔌 Modbus TCP / PLC Canlı Bağlantı":
    st.subheader("🔌 Modbus TCP / OPC UA Canlı PLC Entegrasyon Monitörü")
    st.write("Saha PLC istasyonlarından (Schneider / Siemens) TCP/IP soketleri üzerinden anlık register okuma durumu:")
    
    plc_col1, plc_col2 = st.columns(2)
    with plc_col1:
        st.markdown("#### 🌐 PLC Bağlantı Parametreleri")
        plc_ip = st.text_input("PLC Gateway IP Adresi:", "192.168.10.50")
        modbus_port = st.number_input("Modbus TCP Port:", value=502)
        polling_rate = st.slider("Polling Süresi (ms)", 500, 5000, 1000)
        
        if st.button("PLC Bağlantısını Test Et"):
            st.success(f"✅ Bağlantı Başarılı! `{plc_ip}:{modbus_port}` adresinden veri akışı aktif (Yanıt süresi: 12ms)")
            
    with plc_col2:
        st.markdown("#### 📊 Aktif Register Blok Durumları")
        plc_status_df = pd.DataFrame({
            "Rack / Modül": ["PLC-Rack 01 (Tank Farm)", "PLC-Rack 02 (Gantry)", "PLC-Rack 03 (AdBlue)", "PLC-Gateway (HSE)"],
            "IP Adresi": ["192.168.10.51", "192.168.10.52", "192.168.10.53", "192.168.10.54"],
            "Durum": ["Çevrimiçi", "Çevrimiçi", "Çevrimiçi", "Çevrimiçi"],
            "Hata Oranı": ["0.0%", "0.0%", "0.0%", "0.0%"]
        })
        st.dataframe(plc_status_df, use_container_width=True, hide_index=True)

# ==========================================
# 7. KESTİRİMÇİ BAKIM & TİTREŞİM
# ==========================================
elif aktif_sayfa == "🛠️ Kestirimci Bakım & Titreşim":
    st.subheader("🛠️ Transfer Pompaları Kestirimci Bakım & Titreşim Monitörü")
    st.write("ISO 10816 standartlarına göre pompa mil titreşimleri, yatak sıcaklıkları ve kavitasyon risk analizi:")
    
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        secilen_pompa = st.selectbox("İncelemek İstediğiniz Pompa:", ["P-101A (Benzin Transfer)", "P-101B (Benzin Yedek)", "P-202A (Motorin)", "P-301 (AdBlue Sevkiyat)"])
        calisma_saati = st.number_input("Toplam Çalışma Saati (h):", value=4250, step=100)
        titresim_mm_s = st.slider("Mil Titreşimi (mm/sn RMS)", 0.5, 10.0, 2.1)
        yatak_sicaklik = st.slider("Yatak Sıcaklığı (°C)", 30.0, 90.0, 52.5)
        
        if titresim_mm_s > 4.5 or yatak_sicaklik > 75.0:
            st.error("🚨 UYARI: Pompa yataklarında aşırı titreşim veya ısınma tespit edildi! Bakım planlanmalı.")
        else:
            st.success("✅ Pompa mekanik durumu normal sınırlarda (ISO 10816 Sınıf A/B).")
            
    with b_col2:
        st.markdown("#### 📋 Terminal Geneli Pompa Sağlık Matrisi")
        pompa_saglik_df = pd.DataFrame({
            "Pompa ID": ["P-101A", "P-101B", "P-202A", "P-301"],
            "Çalışma (h)": [4250, 1100, 6800, 3100],
            "Titreşim (mm/s)": [2.1, 1.2, 4.8, 1.5],
            "Yatak Sıcaklığı (°C)": [52.5, 45.0, 78.2, 48.0],
            "Sağlık Durumu": ["İyi", "İyi", "Bakım Gerekli", "İyi"]
        })
        st.dataframe(pompa_saglik_df, use_container_width=True, hide_index=True)

# ==========================================
# 8. KATODİK KORUMA & TELEMETRİ
# ==========================================
elif aktif_sayfa == "⚡ Katodik Koruma & Telemetri":
    st.subheader("⚡ Katodik Koruma & Boru Hattı Potansiyel Telemetrisi")
    st.write("Yer altı transfer hatları ve tank tabanları koruma potansiyelleri (Cu/CuSO4 referans elektrot):")
    
    k_col1, k_col2 = st.columns(2)
    with k_col1:
        st.markdown("#### 🔋 Redresör İstasyon Durumları")
        redresor_id = st.selectbox("İstasyon Seçin:", ["TR-01 (Ana İskele Hattı)", "TR-02 (Tank Çiftliği Kuzey)", "TR-03 (Gantry Besleme Hattı)"])
        cikis_volt = st.number_input("Çıkış Voltajı (V):", value=18.5, step=0.5)
        cikis_akim = st.number_input("Çıkış Akımı (A):", value=12.4, step=0.2)
        potansiyel = st.slider("Ölçülen Boru/Zemin Potansiyeli (mV)", -1200, -600, -880)
        
        if potansiyel > -850:
            st.error("🚨 KRİTİK: Koruma potansiyeli -850 mV eşiğinin altında! Korozyon riski mevcut.")
        else:
            st.success("✅ Katodik koruma seviyesi ISO 15589 standardına uygundur (-850 mV altı korumada).")
            
    with k_col2:
        st.markdown("#### 📊 İstasyon Telemetri Özeti")
        katodik_df = pd.DataFrame({
            "İstasyon": ["TR-01", "TR-02", "TR-03", "TR-04"],
            "Bölge": ["İskele", "Kuzey Tanklar", "Gantry", "AdBlue Tesis"],
            "Potansiyel (mV)": [-880, -910, -865, -940],
            "Durum": ["Normal", "Normal", "Normal", "Normal"]
        })
        st.dataframe(katodik_df, use_container_width=True, hide_index=True)

# ==========================================
# 9. VRU BUHAR GERİ KAZANIM
# ==========================================
elif aktif_sayfa == "💨 VRU Buhar Geri Kazanım":
    st.subheader("💨 Vapor Recovery Unit (VRU) Performans Denetimi")
    st.write("Benzin dolum adalarından yükselen hidrokarbon buharlarının geri kazanım ve absorpsiyon verimliliği:")
    
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        st.markdown("#### 🎛️ VRU Kolon Parametreleri")
        vru_basinç = st.slider("Absorpsiyon Kolonu Basıncı (mbar)", 50, 500, 180)
        emisyON_ppm = st.number_input("Baca Çıkışı Hidrokarbon Emisyonu (ppm):", value=18.5, step=0.5)
        vakum_vfd = st.slider("Vakum Emiş Fanı Frekansı (Hz)", 20.0, 50.0, 42.0)
        
        if emisyON_ppm > 35.0:
            st.error("🚨 UYARI: Baca emisyon sınır değeri (35 ppm) aşıldı! Absorpsiyon yıkama debisini artırın.")
        else:
            st.success("✅ VRU emisyon değerleri çevre mevzuatına tamamen uygun.")
            
    with v_col2:
        st.markdown("#### 📈 VRU Çalışma Metrikleri")
        vru_df = pd.DataFrame({
            "Parametre": ["Geri Kazanım Verimi", "Yıkama Sıvısı Akışı", "Kompresör Sıcaklığı", "Aktif Karbon Yatak Dp"],
            "Değer": ["%98.4", "4.5 m³/h", "64.2 °C", "35 mbar"],
            "Limit / Durum": ["(> %95) - OK", "(4-6 m³/h) - OK", "(< 80°C) - OK", "(< 50 mbar) - OK"]
        })
        st.dataframe(vru_df, use_container_width=True, hide_index=True)

# ==========================================
# 10. TANK ISITMA & SERPANTİN
# ==========================================
elif aktif_sayfa == "♨️ Tank Isıtma & Serpantin":
    st.subheader("♨️ Tank Serpantin ve Isıtma Sistemi (Steam Heating) Otomasyonu")
    st.write("Ağır ürün tanklarının viskozite kontrolü için buhar serpantinleri ve eşanjör sıcaklık denetimi:")
    
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        st.markdown("#### 🔥 Isıtma Kontrol Paneli")
        isitmali_tank = st.selectbox("Tank Seçin:", ["T-201 (Ağır Fuel-Oil)", "T-202 (Ağır Motorin)", "T-301 (AdBlack Stok)"])
        buhar_basinc = st.slider("Buhar Serpantin Giriş Basıncı (Bar)", 1.0, 10.0, 4.2)
        urun_hedef_sicaklik = st.number_input("Hedef Tank Sıcaklığı (°C):", value=45.0, step=1.0)
        mevcut_tank_sicaklik = st.number_input("Ölçülen Tank Sıcaklığı (°C):", value=43.5, step=0.5)
        
        if mevcut_tank_sicaklik < (urun_hedef_sicaklik - 3.0):
            st.warning("⚠️ Sıcaklık hedef değerin altında! Buhar kapanı (steam trap) valfi açılıyor.")
        else:
            st.success("✅ Tank ısıtma PID döngüsü kararlı çalışıyor.")
            
    with s_col2:
        st.markdown("#### 📋 Serpantin Hat Durumları")
        serp_df = pd.DataFrame({
            "Tank ID": ["T-201", "T-202", "T-301", "T-302"],
            "Ürün": ["Fuel-Oil", "Motorin", "AdBlue", "AdBlue"],
            "Sıcaklık (°C)": [43.5, 22.0, 24.5, 23.0],
            "Buhar Vanası": ["%45 Açık", "Kapalı", "Kapalı", "Kapalı"]
        })
        st.dataframe(serp_df, use_container_width=True, hide_index=True)

# ==========================================
# 11. SAHA LEL & YANGIN EMNİYETİ
# ==========================================
elif aktif_sayfa == "🛡️ Saha LEL & Yangın Emniyeti":
    st.subheader("🛡️ Saha LEL & Yangın Emniyet Paneli")
    e1, e2, e3 = st.columns(3)
    e1.metric("Anlık Saha LEL Oranı", "%0.0 Vol", delta="Normal", delta_color="normal")
    e2.metric("Yangın Suyu Stok (YT 01-03)", "10.000 m³ (%100)", delta="Emniyetli")
    e3.metric("ESD Durumu", "HAZIR (NORMAL)", delta_color="normal")
    st.divider()
    st.success("✅ **Saha-01 Tank Sahası LEL Dedektörü:** Normal (%0)")
    st.success("✅ **Saha-02 Dolum Adaları LEL Dedektörü:** Normal (%0)")

# ==========================================
# 12. SEVESO & ESD MATRİSİ
# ==========================================
elif aktif_sayfa == "🚨 SEVESO & ESD Matrisi":
    st.subheader("🚨 SEVESO II/III Emniyet Matrisi & Acil Durdurma (ESD)")
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        st.markdown("#### Yangın Suyu & Köpük Ring Basınçları")
        st.success("✅ **Ana Yangın Suyu Ring Basıncı:** 10.2 Bar (Hedef: 10.0 Bar)")
        st.success("✅ **Köpük Pompası Hazırlık Durumu:** DEVREDE (Standby)")
        st.success("✅ **Deluge (Su Perdesi) Vanaları:** Otomatik Modda")
    with s_col2:
        st.markdown("#### Acil Durdurma (ESD) Interlock Durumu")
        st.warning("⚠️ **ESD-1 (Tank Sahası):** AKTİF / NORMAL")
        st.warning("⚠️ **ESD-2 (Dolum Adaları):** AKTİF / NORMAL")
        st.warning("⚠️ **ESD-3 (İskele Deniz Kolları):** AKTİF / NORMAL")

# ==========================================
# 13. ADBLUE ÜRETİM HATTI
# ==========================================
elif aktif_sayfa == "💧 AdBlue Üretim Hattı":
    st.subheader("AdBlue (DEF) Üretim, Stok ve Sevkiyat Takibi")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Azami Tasarım Kapasitesi", "100 Ton / Gün")
    col2.metric("Bugünkü Fiili Üretim", "78.5 Ton", delta="+2.5 Ton")
    col3.metric("Kapasite Kullanımı (KKO)", "%78.5")
    col4.metric("AdBlue Ana Stok Tankı", "110 Ton (%55)", delta="-5 Ton")

# ==========================================
# 14. ISO 22241 LAB & BLENDING
# ==========================================
elif aktif_sayfa == "🧪 ISO 22241 Lab & Blending":
    st.subheader("🧪 ISO 22241 AdBlue Laboratuvar & Düzeltme Modülü")
    q_col1, q_col2 = st.columns(2)
    with q_col1:
        st.markdown("#### 🔬 Partiye Özel Numune Analizi")
        parti_no = st.text_input("Analiz Edilen Parti No:", "PARTI-2026-1106")
        ure_orani = st.number_input("Üre Konsantrasyonu (%) [İdeal: 32.5]", value=32.52, step=0.01)
        yogunluk_20 = st.number_input("20°C Yoğunluk (kg/m³) [İdeal: 1087 - 1093]", value=1089.5, step=0.5)
        biure_yuzde = st.number_input("Biüre Oranı (%) [Maksimum %0.2]", value=0.12, step=0.01)
        
        if st.button("Laboratuvar Uygunluk Onayı Ver"):
            if 31.8 <= ure_orani <= 33.2 and 1087 <= yogunluk_20 <= 1093 and biure_yuzde <= 0.2:
                st.success(f"✅ {parti_no} nolu parti ISO 22241 standardına uygundur. Sevkiyat onaylandı!")
            else:
                st.error(f"❌ {parti_no} nolu parti standart dışı değerler içeriyor!")

        st.markdown("---")
        st.markdown("#### ⚖️ Parti Düzeltme (Blending) Hesaplayıcısı")
        mevcut_parti_hacim = st.number_input("Parti Hacmi (Ton)", value=20.0, step=1.0)
        olculen_ure = st.number_input("Mevcut Ölçülen Üre (%)", value=33.5, step=0.1)
        if olculen_ure > 32.5:
            su_ihtiyaci = mevcut_parti_hacim * (olculen_ure - 32.5) / 32.5
            st.warning(f"⚠️ Yüksek konsantrasyon! Tam %32.5'e düşürmek için eklenecek saf su: **{su_ihtiyaci*1000:.1f} Litre**")
        elif olculen_ure < 32.5 and olculen_ure > 0:
            st.warning(f"⚠️ Düşük konsantrasyon! Katı üre takviyesi gerekiyor.")
        else:
            st.success(f"✅ Konsantrasyon ideal seviyede.")

    with q_col2:
        st.markdown("#### 📈 ISO 22241 Kalite Kontrol Trendi (Üre %)")
        trend_df = pd.DataFrame({
            "Parti": ["P-1101", "P-1102", "P-1103", "P-1104", "P-1105", "P-1106"],
            "Ure_Yuzde": [32.5, 32.6, 32.4, 32.52, 32.48, 32.52]
        })
        fig_trend = px.line(trend_df, x="Parti", y="Ure_Yuzde", markers=True, title="Son Partilerin Üre Konsantrasyon Seyri")
        fig_trend.add_hline(y=32.5, line_dash="dash", line_color="green", annotation_text="İdeal (%32.5)")
        fig_trend.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=320)
        st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("#### 📋 Geçmiş Lab Logları")
        lab_history = pd.DataFrame({
            "Parti No": ["PARTI-1105", "PARTI-1104", "PARTI-1103"],
            "Üre (%)": [32.48, 32.52, 32.40],
            "Yoğunluk": [1088.5, 1089.5, 1087.8],
            "Durum": ["Onaylandı", "Onaylandı", "Onaylandı"]
        })
        st.dataframe(lab_history, use_container_width=True)

# ==========================================
# 15. SİSTEM ALARMLARI
# ==========================================
elif aktif_sayfa == "🚨 Sistem Alarmları":
    st.subheader("🚨 Otomatik Algılanan Tank & Sistem Alarmları")
    if df_tank is not None and not df_tank.empty:
        high_tanks = df_tank[df_tank['Doluluk_Yuzde'] >= 85]['Tank_ID'].tolist()
        low_tanks = df_tank[df_tank['Doluluk_Yuzde'] <= 15]['Tank_ID'].tolist()
        a1, a2 = st.columns(2)
        with a1:
            st.error(f"🔴 **Yüksek Seviye Riski (≥%85):** {len(high_tanks)} Tank")
            if high_tanks:
                st.write(", ".join(high_tanks))
        with a2:
            st.warning(f"🟡 **Kritik Düşük Stok (≤%15):** {len(low_tanks)} Tank")
            if low_tanks:
                st.write(", ".join(low_tanks))

# ==========================================
# 16. VARDIYA TESLİM & NOTLAR
# ==========================================
elif aktif_sayfa == "📝 Vardiya Teslim & Notlar":
    st.subheader("📝 Vardiya Teslim & Saha Notları")
    if 'notes' not in st.session_state:
        st.session_state['notes'] = []
    with st.form("note_form"):
        note_text = st.text_area("Yeni Operasyonel Not / Vardiya Teslim Mesajı:")
        submit_note = st.form_submit_button("Notu Kaydet")
        if submit_note and note_text.strip():
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state['notes'].append(f"📌 **[{now_str}]** {note_text}")
            st.success("Not başarıyla eklendi!")
    st.markdown("#### 📋 Aktif Vardiya Logları")
    if st.session_state['notes']:
        for n in reversed(st.session_state['notes']):
            st.info(n)
    else:
        st.write("Henüz eklenmiş not bulunmuyor.")