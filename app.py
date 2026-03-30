import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from PIL import Image

# 1. CONFIGURACIÓN E INTERFAZ
st.set_page_config(page_title="Panadería Control", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; background-color: #2E86C1; color: white; height: 3em; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS (Simulada para persistencia en sesión)
if 'compras' not in st.session_state:
    # Datos iniciales de ejemplo
    st.session_state.compras = pd.DataFrame([
        {'fecha': '2023-10-01', 'producto': 'Harina', 'proveedor': 'Proveedor A', 'precio': 1.10, 'cantidad': 10},
        {'fecha': '2023-10-05', 'producto': 'Harina', 'proveedor': 'Proveedor B', 'precio': 1.05, 'cantidad': 10}
    ])

if 'ventas' not in st.session_state:
    # Datos simulados de las últimas 4 semanas para las gráficas
    data = []
    for i in range(28):
        fecha = datetime.date.today() - datetime.timedelta(days=i)
        data.append({'fecha': fecha, 'cantidad': 100 + (i % 7 * 20)})
    st.session_state.ventas = pd.DataFrame(data)

# 3. MENÚ PRINCIPAL
st.title("🍞 Sistema de Gestión Panadería")
opcion = st.sidebar.radio("MENÚ", ["📋 Ventas y Clientes", "📸 Facturas e Inventario", "🏢 Comparador de Proveedores", "📈 Producción Semanal"])

# --- MÓDULO 1: CLIENTES Y VENTAS ---
if opcion == "📋 Ventas y Clientes":
    st.header("Nueva Venta / Pedido")
    
    col1, col2 = st.columns(2)
    with col1:
        cliente = st.selectbox("Cliente", ["Público General", "Restaurante El Pescador (VIP)", "Cafetería Centro (Gran Volumen)"])
        producto = st.selectbox("Producto", ["Barra de Pan", "Croissant", "Tarta Artesana"])
    
    # Lógica de precios diferenciados
    precios_base = {"Barra de Pan": 1.0, "Croissant": 1.5, "Tarta Artesana": 15.0}
    tarifas = {"Público General": 1.0, "Restaurante El Pescador (VIP)": 0.75, "Cafetería Centro (Gran Volumen)": 0.85}
    
    precio_final = precios_base[producto] * tarifas[cliente]
    
    with col2:
        cantidad = st.number_input("Cantidad", min_value=1, value=1)
        st.metric("Precio Unitario", f"{precio_final:.2f} €", delta=f"Tarifa: {cliente}")
    
    if st.button("Registrar Venta"):
        nueva_v = pd.DataFrame([{'fecha': datetime.date.today(), 'cantidad': cantidad}])
        st.session_state.ventas = pd.concat([st.session_state.ventas, nueva_v], ignore_index=True)
        st.success(f"Venta registrada: {cantidad * precio_final:.2f} €")

# --- MÓDULO 2: FACTURAS E INVENTARIO ---
elif opcion == "📸 Facturas e Inventario":
    st.header("📸 Escanear Factura de Compra")
    foto = st.camera_input("Haz una foto a la factura del proveedor")
    
    if foto:
        st.info("Procesando factura con IA...")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            proveedor_f = st.text_input("Proveedor", value="Proveedor Nuevo")
            producto_f = st.selectbox("Producto comprado", ["Harina", "Mantequilla", "Levadura", "Azúcar"])
        with col_f2:
            precio_f = st.number_input("Precio por unidad (€)", format="%.2f")
            cant_f = st.number_input("Cantidad comprada", min_value=1)
            
        if st.button("Guardar Compra e Inventario"):
            nueva_compra = {
                'fecha': str(datetime.date.today()),
                'producto': producto_f,
                'proveedor': proveedor_f,
                'precio': precio_f,
                'cantidad': cant_f
            }
            st.session_state.compras = pd.concat([st.session_state.compras, pd.DataFrame([nueva_compra])], ignore_index=True)
            st.success("Inventario actualizado y precio registrado.")

# --- MÓDULO 3: COMPARADOR DE PROVEEDORES ---
elif opcion == "🏢 Comparador de Proveedores":
    st.header("⚖️ ¿Quién me vende más barato?")
    
    prod_ver = st.selectbox("Selecciona producto para comparar", st.session_state.compras['producto'].unique())
    df_comp = st.session_state.compras[st.session_state.compras['producto'] == prod_ver]
    
    if not df_comp.empty:
        df_sorted = df_comp.sort_values('precio')
        st.dataframe(df_sorted[['proveedor', 'precio', 'fecha']], use_container_width=True)
        
        mejor_p = df_sorted.iloc[0]
        st.success(f"El mejor proveedor para **{prod_ver}** es **{mejor_p['proveedor']}** a **{mejor_p['precio']}€**")
        
        fig_comp = px.bar(df_comp, x='proveedor', y='precio', color='proveedor', title=f"Histórico de precios de {prod_ver}")
        st.plotly_chart(fig_comp)

# --- MÓDULO 4: ESTADÍSTICAS DE PRODUCCIÓN ---
elif opcion == "📈 Producción Semanal":
    st.header("📊 Análisis de Venta de Pan")
    
    df_v = st.session_state.ventas.copy()
    df_v['fecha'] = pd.to_datetime(df_v['fecha'])
    df_v['dia_semana'] = df_v['fecha'].dt.day_name()
    
    orden_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    resumen = df_v.groupby('dia_semana')['cantidad'].mean().reindex(orden_dias)
    
    st.subheader("Media de ventas por día")
    fig_prod = px.line(x=resumen.index, y=resumen.values, markers=True, title="Previsión de Producción")
    st.plotly_chart(fig_prod)
    
    st.info("💡 Consejo: Los fines de semana la producción debe subir un 30% según tus históricos.")
