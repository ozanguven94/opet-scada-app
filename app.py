import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="OPET Marmara Ereğlisi SCADA",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

SHEET_ID = "17htReQxvrsjLw8Cf6ES25GsuHBnKFIN3Gh2aH5XkoYI"

TANKLAR_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Tanklar"
ADBLUE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=AdBlue_Proses"

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.title("🔒 OPET Marmara Ereğlisi Terminal SCADA")
    st.caption("Mobil Otomasyon & İzleme Paneli")
    
    with st.form("login_form"):
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        submit = st.form_submit_button("Giriş Yap")
        
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

# Başlık ve Anlık Durum
head_c1, head_c2 = st.columns([3, 1])
with head_c1:
    st.markdown("## 🛢️ OPET Marmara Ereğlisi Terminal SCADA")
with head_c2:
    st.success(f"🟢 CANLI AKIŞ: {datetime.now().strftime('%H:%M:%S')}")

# Üst KPI Paneli
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Toplam Depolama Kapasitesi", "840.000 m³")
kpi2.metric("Motorin Kapasitesi", "413.000 m³")
kpi3.metric("Benzin Kapasitesi", "290.000 m³")
kpi4.metric("Aktif Takip Edilen Tank", "68 Tank")

st.divider()

tabs = st.tabs([
    "🔍 Tank Detay & Animasyonlu Görsel",
    "📝 Vardiya Defteri & Notlar",
    "🔀 Hat & Transfer Rotaları",
    "🛡️ LEL & Emniyet (HSE)",
    "⛽ Genel Tank Envanteri", 
    "🧮 ASTM D1250 & ETA", 
    "💧 AdBlue Üretim", 
    "🚨 Sistem Alarmları"
])

# --- TAB 0: TANK DETAY & CANLI ANİMASYON ---
with tabs[0]:
    st.subheader("🔎 Tank Özel İnceleme & Canlı Sıvı Animasyonu")
    if df_tank is not None and not df_tank.empty:
        selected_tank_id = st.selectbox("İncelemek İstediğiniz Tankı Seçin:", df_tank['Tank_ID'].unique())
        tank_data = df_tank[df_tank['Tank_ID'] == selected_tank_id].iloc[0]
        
        kapasite = float(tank_data.get('Kapasite_m3', 0))
        hacim = float(tank_data.get('Hacim_m3', 0))
        doluluk = float(tank_data.get('Doluluk_Yuzde', 0))
        sicaklik = float(tank_data.get('Sicaklik_C', 0))
        urun = str(tank_data.get('Urun', '-'))
        durum = str(tank_data.get('Durum', '-'))
        bosluk = kapasite - hacim

        st.markdown(f"### 📌 {selected_tank_id} Tankı Anlık Verileri ({urun})")
        
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Ürün Türü", urun)
        m2.metric("Doluluk Oranı", f"%{doluluk}")
        m3.metric("Mevcut Hacim", f"{hacim:,.1f} m³")
        m4.metric("Kalan Boş Alan", f"{bosluk:,.1f} m³")
        m5.metric("Tank Sıcaklığı", f"{sicaklik} °C")

        st.divider()
        d_col1, d_col2 = st.columns([1, 2])

        with d_col1:
            st.markdown("#### 🛢️ Canlı Likit Seviye Animasyonu")
            
            # Dinamik Sıvı Rengi
            fill_color = "#28a745" if doluluk < 85 else "#dc3545"
            if doluluk <= 15:
                fill_color = "#ffc107"

            # CSS Animasyonlu Tank HTML/CSS Bloğu
            tank_html = f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%;">
                <div style="position: relative; width: 160px; height: 260px; border: 4px solid #333; border-radius: 20px; overflow: hidden; background-color: #1e1e1e; box-shadow: inset 0 0 10px #000;">
                    <div style="position: absolute; top: 10px; width: 100%; text-align: center; color: white; font-weight: bold; font-size: 18px; z-index: 10;">
                        %{doluluk:.1f}
                    </div>
                    <div style="position: absolute; bottom: 0; width: 100%; height: {doluluk}%; background-color: {fill_color}; transition: height 1s ease-in-out; opacity: 0.85;">
                        <div style="position: absolute; top: -10px; left: 0; width: 100%; height: 10px; background: rgba(255,255,255,0.4); border-radius: 50%;"></div>
                    </div>
                </div>
                <div style="margin-top: 10px; font-weight: bold; font-size: 16px; color: #555;">{selected_tank_id} - {urun}</div>
            </div>
            """
            st.components.v1.html(tank_html, height=310)

        with d_col2:
            st.markdown("#### ⚡ Hızlı Operasyonel Analiz")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=doluluk,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"{selected_tank_id} Kadran Göstergesi (%)"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 15], 'color': "lightyellow"},
                        {'range': [15, 85], 'color': "lightgreen"},
                        {'range': [85, 100], 'color': "pink"}
                    ],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}
                }
            ))
            fig_gauge.update_layout(height=260, margin=dict(t=30, b=10, l=30, r=30))
            st.plotly_chart(fig_gauge, use_container_width=True)

            transfer_debi = st.number_input(f"{selected_tank_id} Transfer Debisi (m³/h):", value=350.0, step=25.0)
            if transfer_debi > 0:
                kalan_sure_saat = bosluk / transfer_debi
                st.success(f"⏱️ Tankın dolmasına kalan tahmini süre: **{kalan_sure_saat:.2f} Saat** ({int(kalan_sure_saat*60)} Dk)")
            else:
                st.warning("Transfer yapılmıyor (Debi 0 m³/h).")
    else:
        st.error("Tank verileri yüklenemedi.")

# --- TAB 1: VARDIYA DEFTERİ ---
with tabs[1]:
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

# --- TAB 2: HAT & TRANSFER ---
with tabs[2]:
    st.subheader("🔀 Canlı Transfer & Manifold Rotaları")
    r1, r2, r3 = st.columns(3)
    with r1:
        st.success("🟢 **Hat 01 (Benzin Transferi)**\n\n• Kaynak: `T-121`\n• Pompa: `P-101A` (350 m³/h)\n• Hedef: `Dolum Adası 02`\n• Vana: **AÇIK (%100)**")
    with r2:
        st.info("🔵 **Hat 02 (Motorin Transferi)**\n\n• Kaynak: `T-204`\n• Pompa: `P-202B` (Hazırda Wait)\n• Hedef: `İskele Manifold 01`\n• Vana: **KAPALI (%0)**")
    with r3:
        st.warning("🟡 **Hat 03 (AdBlue Besleme)**\n\n• Kaynak: `AdBlue Stok Tankı`\n• Pompa: `P-301` (15 Ton/h)\n• Hedef: `Paketleme / IBC`\n• Vana: **MODÜLE EDİLİYOR**")

# --- TAB 3: LEL ---
with tabs[3]:
    st.subheader("🛡️ Saha LEL & Yangın Emniyet Paneli")
    e1, e2, e3 = st.columns(3)
    e1.metric("Anlık Saha LEL Oranı", "%0.0 Vol", delta="Normal", delta_color="normal")
    e2.metric("Yangın Suyu Stok (YT 01-03)", "10.000 m³ (%100)", delta="Emniyetli")
    e3.metric("ESD (Acil Durdurma) Durumu", "HAZIR (NORMAL)", delta_color="normal")
    st.divider()
    st.success("✅ **Saha-01 Tank Sahası LEL Dedektörü:** Normal (%0)")
    st.success("✅ **Saha-02 Dolum Adaları LEL Dedektörü:** Normal (%0)")

# --- TAB 4: GENEL ENVANTER ---
with tabs[4]:
    st.subheader("Terminal Tank Seviyeleri ve Stok Dağılımı")
    if df_tank is not None and not df_tank.empty:
        f_col1, f_col2, f_col3 = st.columns([1, 1, 1])
        with f_col1:
            urun_listesi = ["TÜMÜ"] + list(df_tank['Urun'].dropna().unique())
            secilen_urun = st.selectbox("Ürüne Göre Filtrele", urun_listesi, key="env_urun")
        with f_col2:
            search_tank = st.text_input("🔍 Tank Koduna Göre Arama", "", key="env_search")
        with f_col3:
            st.write("")
            st.write("")
            csv_data = df_tank.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Vardiya Raporunu İndir (.csv)", data=csv_data, file_name="OPET_Tank_Raporu.csv", mime="text/csv")

        filtered_df = df_tank.copy()
        if secilen_urun != "TÜMÜ":
            filtered_df = filtered_df[filtered_df['Urun'] == secilen_urun]
        if search_tank.strip() != "":
            filtered_df = filtered_df[filtered_df['Tank_ID'].astype(str).str.contains(search_tank.strip(), case=False, na=False)]

        col_left, col_right = st.columns([2, 1])
        with col_left:
            fig = px.bar(filtered_df, x='Tank_ID', y='Doluluk_Yuzde', color='Doluluk_Yuzde', color_continuous_scale=['green', 'yellow', 'red'], text='Doluluk_Yuzde', title="Tank Doluluk Oranları (%)", height=400)
            fig.update_traces(texttemplate='%{text}%', textposition='outside')
            fig.update_layout(yaxis=dict(range=[0, 115]))
            st.plotly_chart(fig, use_container_width=True)
            
        with col_right:
            fig_pie = px.pie(df_tank, names='Urun', values='Hacim_m3', hole=0.4)
            fig_pie.update_layout(margin=dict(t=20, b=20, l=10, r=10))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.dataframe(filtered_df[['Tank_ID', 'Urun', 'Kapasite_m3', 'Doluluk_Yuzde', 'Hacim_m3', 'Sicaklik_C', 'Durum']], use_container_width=True)

# --- TAB 5: ASTM D1250 ---
with tabs[5]:
    st.subheader("📐 API MPMS / ASTM D1250 Sıcaklık Düzeltme & Dolum Süresi Simülasyonu")
    col_calc1, col_calc2 = st.columns(2)
    with col_calc1:
        v_obs = st.number_input("Gözlenen Hacim (V_obs - m³)", value=5000.0, step=100.0)
        temp_c = st.number_input("Tank Sıcaklığı (°C)", value=22.5, step=0.5)
        dens_15 = st.number_input("15°C Yoğunluk (kg/m³)", value=835.0, step=0.5)
        vcf = 1.0 - ((temp_c - 15.0) * 0.00084)
        v_15 = v_obs * vcf
        mass_ton = (v_15 * dens_15) / 1000.0
        st.info(f"• **VCF:** `{vcf:.5f}`\n• **V15 Hacim:** `{v_15:.2f} m³`\n• **Toplam Ağırlık:** `{mass_ton:.2f} Ton`")

    with col_calc2:
        target_tank = st.selectbox("Operasyonel Tank Seçin", df_tank['Tank_ID'].unique() if df_tank is not None else ["T-121"], key="eta_tank")
        flow_rate = st.number_input("Anlık Transfer Debi (m³/h)", value=350.0, step=10.0, key="eta_flow")
        if df_tank is not None and not df_tank.empty:
            tank_info = df_tank[df_tank['Tank_ID'] == target_tank].iloc[0]
            kapasite = float(tank_info.get('Kapasite_m3', 10000.0))
            mevcut_hacim = float(tank_info.get('Hacim_m3', 5000.0))
            kalan_boşluk = kapasite - mevcut_hacim
            if flow_rate > 0:
                kalan_saat = kalan_boşluk / flow_rate
                st.success(f"• **Kalan Boş Hacim:** `{kalan_boşluk:.1f} m³`\n• **Doluma Kalan Süre:** `{kalan_saat:.2f} Saat` ({int(kalan_saat*60)} Dk)")

# --- TAB 6: ADBLUE ---
with tabs[6]:
    st.subheader("AdBlue (DEF) Üretim, Stok ve Sevkiyat Takibi")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Azami Tasarım Kapasitesi", "100 Ton / Gün")
    col2.metric("Bugünkü Fiili Üretim", "78.5 Ton", delta="+2.5 Ton")
    col3.metric("Kapasite Kullanımı (KKO)", "%78.5")
    col4.metric("AdBlue Ana Stok Tankı", "110 Ton (%55)", delta="-5 Ton")

# --- TAB 7: ALARMLAR ---
with tabs[7]:
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

