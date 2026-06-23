import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# Configuración inicial de la página
st.set_page_config(page_title="Dashboard de Bodegas", page_icon="📊", layout="wide")

# =========================================================
# CONTROL DE ESTADOS GLOBAL (Filtros persistentes y clics)
# =========================================================
if "segmentos_seleccionados" not in st.session_state:
    st.session_state["segmentos_seleccionados"] = []

# =========================================================
# PALETA DE COLORES Y DISEÑO CSS PROFESIONAL
# =========================================================
ORDEN_SEGMENTOS = ["VIP", "Leal", "Regular", "En riesgo", "Perdido"]
COLORES_SEGMENTO = {
    "VIP": "#588157",        # Verde Olivo
    "Leal": "#003554",       # Azul marino
    "Regular": "#5B8FA8",    # Azul acero
    "En riesgo": "#C41230",  # Rojo corporativo
    "Perdido": "#8B0000"     # Vino oscuro
}

st.markdown("""
<style>
/* Contenedor principal */
.main .block-container { 
    padding-top: 2rem !important; 
    background-color: #FAFAFA !important; 
}

/* Tarjeta Hero Principal */
.hero-card {
    background: linear-gradient(135deg, #051923 0%, #003554 100%);
    padding: 24px; 
    border-radius: 12px; 
    color: #FFFFFF; 
    height: 100%;
    display: flex; 
    flex-direction: column; 
    justify-content: center;
}
.hero-value { 
    font-size: 40px; 
    font-weight: 700; 
    margin-top: 4px; 
}

/* Rediseño de las Tarjetas Interactivas sin superposición */
.card-container {
    background-color: #FFFFFF;
    border: 1px solid #E4E4E7;
    border-radius: 10px;
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    margin-bottom: 12px;
}
.card-container-selected {
    background-color: #F4F4F5;
    border: 2px solid #18181B;
    border-radius: 10px;
    padding: 11px 15px; /* Ajuste por el grosor de borde */
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    margin-bottom: 12px;
}

/* Encabezado oscuro dentro de la sobre hoja (Estilo Pop-up) */
.popup-header {
    background: linear-gradient(135deg, #0A1628 0%, #003554 100%);
    padding: 24px;
    border-radius: 12px 12px 0px 0px;
    color: #FFFFFF;
    margin-bottom: 20px;
    margin-top: -30px; 
    margin-left: -15px;
    margin-right: -15px;
}
.popup-title { font-size: 24px; font-weight: 700; text-transform: uppercase; }
.popup-subtitle { font-size: 13px; color: #94A3B8; margin-top: 4px; }

.popup-meta-box {
    background-color: #FFFFFF; border: 1px solid #E4E4E7; border-radius: 8px; padding: 12px 16px; text-align: center;
}
.popup-meta-label { font-size: 11px; text-transform: uppercase; color: #71717A; font-weight: 500; }
.popup-meta-value { font-size: 18px; font-weight: 600; color: #18181B; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# CARGA DE DATOS (PARQUET)
# =========================================================
@st.cache_data
def cargar_clientes():
    df = pd.read_parquet("clientes.parquet")
    df["SEGMENTO"] = pd.Categorical(df["SEGMENTO"], categories=ORDEN_SEGMENTOS, ordered=True)
    return df

@st.cache_data
def cargar_ventas():
    df = pd.read_parquet("ventas.parquet")
    # Convertimos a formato fecha simple eliminando horas
    df["FECHA"] = pd.to_datetime(df["FECHA"]).dt.date
    return df

@st.cache_data
def cargar_rutas():
    return pd.read_parquet("rutas.parquet")

def fmt_monto(valor):
    try:
        if isinstance(valor, (int, float)):
            return "${:,.2f}".format(float(valor))
        s = str(valor).strip()
        if "," in s and "." in s:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s:
            s = s.replace(",", ".")
        return "${:,.2f}".format(float(s))
    except (ValueError, TypeError):
        return str(valor)

if not os.path.exists("clientes.parquet") or not os.path.exists("ventas.parquet") or not os.path.exists("rutas.parquet"):
    st.error("Error crítico: Faltan archivos físicos de datos .parquet.")
    st.stop()

clientes = cargar_clientes()

# =========================================================
# ENCABEZADO DE LA APLICACIÓN (LOGOTIPO CIRCLE K)
# =========================================================
if os.path.exists("logo.png"):
    with open("logo.png", "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0A1628 0%, #003554 100%); padding: 16px 28px; border-radius: 12px; display: flex; align-items: center; gap: 20px; margin-bottom: 24px;">
        <img src="data:image/png;base64,{logo_b64}" style="height: 45px; object-fit: contain;">
        <div style="width: 1px; height: 38px; background-color: rgba(255,255,255,0.25);"></div>
        <div>
            <div style="font-size: 20px; font-weight: 700; color: #FFFFFF;">Análisis Estratégico de Clientes</div>
            <div style="font-size: 12px; color: #94A3B8; margin-top: 3px;">Consolidado de madurez comercial y SKUs transaccionados.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.title("Análisis Estratégico de Clientes")

# =========================================================
# SECCIÓN DE FILTROS SUPERIORES (Sincronizados)
# =========================================================
col_f1, col_f2 = st.columns(2)
with col_f1:
    rutas_df = cargar_rutas()
    RUTAS_EXCLUIDAS = [10101, 7658, 7437, 10201, 7436, 7545, 7544, 9031, 7300, 10301]
    rutas_df = rutas_df[~rutas_df["RUTA"].isin(RUTAS_EXCLUIDAS)]
    rutas_df["ETIQUETA"] = rutas_df["RUTA"].astype(str) + " - " + rutas_df["BODEGA"]
    etiquetas_sel = st.multiselect("📍 Central / Bodegas de Distribución", sorted(rutas_df["ETIQUETA"].tolist()), placeholder="🔍 Buscar nombre o ID")
    bodegas_sel = rutas_df[rutas_df["ETIQUETA"].isin(etiquetas_sel)]["BODEGA"].tolist()

# Datos base para los conteos fijos de las tarjetas
datos_base_botones = clientes.copy()
if bodegas_sel:
    datos_base_botones = datos_base_botones[datos_base_botones["BODEGA"].isin(bodegas_sel)]

conteo_botones = datos_base_botones["SEGMENTO"].value_counts().reindex(ORDEN_SEGMENTOS).fillna(0).astype(int)

with col_f2:
    # Captura y manipulación directa a través del multiselect
    segmentos_sel = st.multiselect(
        "🎯 Segmentación RFM", 
        ORDEN_SEGMENTOS, 
        key="segmentos_seleccionados",
        placeholder="🔍 Buscar tipo de cliente"
    )

# Filtrado definitivo para la vista de datos
datos = datos_base_botones.copy()
if segmentos_sel:
    datos = datos[datos["SEGMENTO"].isin(segmentos_sel)]

total_filtrado = len(datos)

# =========================================================
# SECCIÓN DE BOTONES DE METRICAS (Rediseño Seguro anti-amontonamiento)
# =========================================================
col_hero, col_grid = st.columns([1.2, 3])
with col_hero:
    st.markdown(f"""
    <div class="hero-card">
        <div style="font-size:11px; text-transform:uppercase; color:#A1A1AA; font-weight:500;">Cartera Activa Filtrada</div>
        <div class="hero-value">{total_filtrado:,}</div>
        <div style="font-size: 12px; color: #71717A; margin-top: 12px;">Establecimientos concurrentes.</div>
    </div>
    """, unsafe_allow_html=True)

# Función para alternar múltiples elementos al mismo tiempo en la lista
def alternar_filtro_multiple(nombre_seg):
    if nombre_seg in st.session_state["segmentos_seleccionados"]:
        st.session_state["segmentos_seleccionados"].remove(nombre_seg)
    else:
        st.session_state["segmentos_seleccionados"].append(nombre_seg)

with col_grid:
    sub_c1, sub_c2, sub_c3 = st.columns(3)
    
    # --- COLUMNA 1: VIP Y LEAL ---
    with sub_c1:
        # Tarjeta VIP
        clase_vip = "card-container-selected" if "VIP" in segmentos_sel else "card-container"
        check_vip = "✅" if "VIP" in segmentos_sel else "⬜"
        st.markdown(f"""
        <div class="{clase_vip}">
            <div style="border-left: 4px solid {COLORES_SEGMENTO['VIP']}; padding-left:10px;">
                <div style="font-size:12px; font-weight:600; color:#52525B;">VIP</div>
                <div style="font-size:24px; font-weight:700; color:{COLORES_SEGMENTO['VIP']};">{conteo_botones['VIP']:,}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        

        # Tarjeta Leal
        clase_leal = "card-container-selected" if "Leal" in segmentos_sel else "card-container"
        check_leal = "✅" if "Leal" in segmentos_sel else "⬜"
        st.markdown(f"""
        <div class="{clase_leal}">
            <div style="border-left: 4px solid {COLORES_SEGMENTO['Leal']}; padding-left:10px;">
                <div style="font-size:12px; font-weight:600; color:#52525B;">Leal</div>
                <div style="font-size:24px; font-weight:700; color:#111827;">{conteo_botones['Leal']:,}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        

    # --- COLUMNA 2: REGULAR Y EN RIESGO ---
    with sub_c2:
        # Tarjeta Regular
        clase_reg = "card-container-selected" if "Regular" in segmentos_sel else "card-container"
        check_reg = "✅" if "Regular" in segmentos_sel else "⬜"
        st.markdown(f"""
        <div class="{clase_reg}">
            <div style="border-left: 4px solid {COLORES_SEGMENTO['Regular']}; padding-left:10px;">
                <div style="font-size:12px; font-weight:600; color:#52525B;">Regular</div>
                <div style="font-size:24px; font-weight:700; color:#005F73;">{conteo_botones['Regular']:,}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        

        # Tarjeta En Riesgo
        clase_riesgo = "card-container-selected" if "En riesgo" in segmentos_sel else "card-container"
        check_riesgo = "✅" if "En riesgo" in segmentos_sel else "⬜"
        st.markdown(f"""
        <div class="{clase_riesgo}">
            <div style="border-left: 4px solid {COLORES_SEGMENTO['En riesgo']}; padding-left:10px;">
                <div style="font-size:12px; font-weight:600; color:#52525B;">En Riesgo</div>
                <div style="font-size:24px; font-weight:700; color:{COLORES_SEGMENTO['En riesgo']};">{conteo_botones['En riesgo']:,}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        

    # --- COLUMNA 3: PERDIDO ---
    with sub_c3:
        # Tarjeta Perdido
        clase_perdido = "card-container-selected" if "Perdido" in segmentos_sel else "card-container"
        check_perdido = "✅" if "Perdido" in segmentos_sel else "⬜"
        st.markdown(f"""
        <div class="{clase_perdido}">
            <div style="border-left: 4px solid {COLORES_SEGMENTO['Perdido']}; padding-left:10px;">
                <div style="font-size:12px; font-weight:600; color:#52525B;">Perdido</div>
                <div style="font-size:24px; font-weight:700; color:{COLORES_SEGMENTO['Perdido']};">{conteo_botones['Perdido']:,}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        

st.write("")
st.divider()

# =========================================================
# SOBRE HOJA FLOTANTE CORREGIDA (st.dialog)
# =========================================================
@st.dialog("Análisis Detallado", width="large")
def descolgar_sobre_hoja_sku(id_cliente, nombre_establecimiento, fila_cliente):
    st.markdown(f"""
    <div class="popup-header">
        <div class="popup-title">{nombre_establecimiento}</div>
        <div class="popup-subtitle">ID CLIENTE: {id_cliente} &nbsp;|&nbsp; Bodega: {fila_cliente['BODEGA']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="popup-meta-box"><div class="popup-meta-label">Segmentación</div><div class="popup-meta-value" style="color:{COLORES_SEGMENTO.get(fila_cliente["SEGMENTO"], "#18181B")}">{fila_cliente["SEGMENTO"]}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="popup-meta-box"><div class="popup-meta-label">Inactividad</div><div class="popup-meta-value">{int(fila_cliente["DIAS DE COMPRA (HACE CUANTO COMPRO LA ULTIMA VEZ)"])} días</div></div>', unsafe_allow_html=True)
    with m3:
        _raw = str(fila_cliente["SUMA DE MONTO"]).strip()
        if "," in _raw and "." in _raw:
            _raw = _raw.replace(".", "").replace(",", ".")
        elif "," in _raw:
            _raw = _raw.replace(",", ".")
        _monto_fmt = "${:,.2f}".format(float(_raw)) if _raw else "$0.00"
        st.markdown(f'<div class="popup-meta-box"><div class="popup-meta-label">Monto Histórico</div><div class="popup-meta-value">{_monto_fmt}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="popup-meta-box"><div class="popup-meta-label">Pedidos Totales</div><div class="popup-meta-value">{int(fila_cliente["CUENTA DE FOLIO PEDIDO"])}</div></div>', unsafe_allow_html=True)
        
    st.write("<br>", unsafe_allow_html=True)
    
    with st.spinner("Extrayendo desglose analítico de compras..."):
        ventas_df = cargar_ventas()
        prods = ventas_df[ventas_df["IDCLIENTE"] == id_cliente]
        
    if not prods.empty:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("<p style='font-size:13px; font-weight:600; color:#3F3F46;'>Top 10 SKUs Más Adquiridos</p>", unsafe_allow_html=True)
            top_p = prods.groupby("DESCRIPCION")["CANTIDAD"].sum().reset_index().sort_values("CANTIDAD", ascending=False).head(10)
            fig_p = px.bar(top_p, x="CANTIDAD", y="DESCRIPCION", orientation="h", text_auto='.2s')
            fig_p.update_traces(marker_color='#003554', textposition="outside", cliponaxis=False)
            fig_p.update_layout(xaxis_title="", yaxis_title="", template="plotly_white", height=280, yaxis={'categoryorder':'total ascending'}, margin=dict(t=5, b=5, l=5, r=35))
            st.plotly_chart(fig_p, use_container_width=True)
            
        with col_g2:
            st.markdown("<p style='font-size:13px; font-weight:600; color:#3F3F46;'>Participación por Marca Comercial</p>", unsafe_allow_html=True)
            top_m = prods.groupby("MARCA")["CANTIDAD"].sum().reset_index().sort_values("CANTIDAD", ascending=False).head(10)
            fig_m = px.bar(top_m, x="MARCA", y="CANTIDAD", text_auto='.2s')
            fig_m.update_traces(marker_color='#5B8FA8', textposition="outside", cliponaxis=False)
            fig_m.update_layout(xaxis_title="", yaxis_title="", template="plotly_white", height=280, margin=dict(t=5, b=5, l=5, r=5))
            st.plotly_chart(fig_m, use_container_width=True)
            
        st.write("<br>", unsafe_allow_html=True)
        st.dataframe(
            prods[["FECHA", "FOLIO PEDIDO", "DESCRIPCION", "MARCA", "CANTIDAD", "MONTO", "TOTAL"]],
            use_container_width=True, height=280,
            column_config={
                "MONTO": st.column_config.NumberColumn("PRECIO U.", format="$%,.2f"),
                "TOTAL": st.column_config.NumberColumn("TOTAL LÍNEA", format="$%,.2f")
            }
        )
    else:
        st.info("No se registran datos detallados de transacciones para este establecimiento.")

# =========================================================
# DISTRIBUCIÓN EN PESTAÑAS PRINCIPALES
# =========================================================
tab_resumen, tab_clientes = st.tabs(["📊 Vista Ejecutiva", "👥 Cartera Detallada"])

# PESTAÑA 1: VISTA GRÁFICA
with tab_resumen:
    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown("<p style='font-size:14px; font-weight:500; color:#27272A; margin-bottom:10px;'>Distribución porcentual de cartera</p>", unsafe_allow_html=True)
        conteo_filtrado_pie = datos["SEGMENTO"].value_counts().reindex(ORDEN_SEGMENTOS).fillna(0).reset_index(name="CANTIDAD")
        fig_pie = px.pie(conteo_filtrado_pie, names="SEGMENTO", values="CANTIDAD", color="SEGMENTO", color_discrete_map=COLORES_SEGMENTO, hole=0.6)
        fig_pie.update_layout(template="plotly_white", margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_der:
        st.markdown("<p style='font-size:14px; font-weight:500; color:#27272A; margin-bottom:10px;'>Volumen financiero por segmento</p>", unsafe_allow_html=True)
        monto_seg = datos.groupby("SEGMENTO", observed=False)["SUMA DE MONTO"].sum().reindex(ORDEN_SEGMENTOS).reset_index()
        fig_bar = px.bar(monto_seg, x="SEGMENTO", y="SUMA DE MONTO", color="SEGMENTO", color_discrete_map=COLORES_SEGMENTO)
        fig_bar.update_layout(showlegend=False, xaxis_title="", yaxis_title="", template="plotly_white", margin=dict(t=10))
        st.plotly_chart(fig_bar, use_container_width=True)

# PESTAÑA 2: EXPLORADOR DE CLIENTES
with tab_clientes:
    st.subheader("Explorador General de Cuentas")
    
    cols_grid = [
        "ID CLIENTE", "BODEGA", "ESTABLECIMIENTO", "CONTACTO PRIMARIO", "TEL", "CORREO",
        "SEGMENTO", "CUENTA DE FOLIO PEDIDO", "SUMA DE MONTO", "DIAS DE COMPRA (HACE CUANTO COMPRO LA ULTIMA VEZ)"
    ]
    
    tabla_main = datos[cols_grid].rename(columns={
        "CUENTA DE FOLIO PEDIDO": "FOLIOS", "SUMA DE MONTO": "MONTO TOTAL", "DIAS DE COMPRA (HACE CUANTO COMPRO LA ULTIMA VEZ)": "DIAS INACTIVO"
    })
    tabla_main["MONTO TOTAL"] = pd.to_numeric(tabla_main["MONTO TOTAL"], errors='coerce').fillna(0)
    tabla_main = tabla_main.sort_values("MONTO TOTAL", ascending=False).reset_index(drop=True)
    
    tabla_main["FOLIOS"] = pd.to_numeric(tabla_main["FOLIOS"], errors='coerce').fillna(0).astype(int)
    tabla_main["DIAS INACTIVO"] = pd.to_numeric(tabla_main["DIAS INACTIVO"], errors='coerce').fillna(0).astype(int)

    evento_seleccion = st.dataframe(
        tabla_main, use_container_width=True, height=450,
        selection_mode="single-row", on_select="rerun",
        column_config={
            "ID CLIENTE": st.column_config.TextColumn("ID CLIENTE"),
            "FOLIOS": st.column_config.NumberColumn("FOLIOS", format="%d"),
            "MONTO TOTAL": st.column_config.NumberColumn("MONTO TOTAL", format="$%,.2f"),
            "DIAS INACTIVO": st.column_config.NumberColumn("DIAS INACTIVO", format="%d"),
        },
        key="grid_clientes_comercial"
    )
    
    if evento_seleccion and "rows" in evento_seleccion["selection"] and evento_seleccion["selection"]["rows"]:
        renglon_activo = evento_seleccion["selection"]["rows"][0]
        fila_grid = tabla_main.iloc[renglon_activo]
        id_final = int(fila_grid["ID CLIENTE"])
        nombre_final = fila_grid["ESTABLECIMIENTO"]
        fila_origen = datos[datos["ID CLIENTE"] == id_final].iloc[0]
        descolgar_sobre_hoja_sku(id_final, nombre_final, fila_origen)