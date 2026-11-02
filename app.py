import streamlit as st
import pandas as pd
import urllib.parse
from os import path
from datetime import datetime
from fpdf import FPDF

# ----------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA
# ----------------------------------------------------
st.set_page_config(
    page_title="AgroYaracuy & Región | Mercado Agrícola Digital",
    page_icon="🌾",
    layout="wide"
)

# Datos oficiales de la empresa
EMPRESA_NOMBRE = "COMPAÑÍA HCHF4 C.A."
EMPRESA_RIF = "J-404509216"
EMPRESA_BANCO = "Banco de Venezuela (0102)"
EMPRESA_TELEFONO = "04120582064"

# ----------------------------------------------------
# 2. INICIALIZACIÓN DE ESTADOS GLOBALES
# ----------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "rol_actual" not in st.session_state:
    st.session_state.rol_actual = None
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = ""
if "tasa_bcv" not in st.session_state:
    st.session_state.tasa_bcv = 36.50
if "pedidos" not in st.session_state:
    st.session_state.pedidos = []
if "ofertas" not in st.session_state:
    st.session_state.ofertas = []
if "agrotiendas_registradas" not in st.session_state:
    st.session_state.agrotiendas_registradas = [
        {"nombre": "Agroinsumos San Felipe C.A.", "estado": "Yaracuy", "municipio": "San Felipe", "telefono": "584121234567"},
        {"nombre": "Agrotienda El Semillero Barquisimeto", "estado": "Lara", "municipio": "Iribarren", "telefono": "584149876543"},
        {"nombre": "Distribuidora Agropecuaria Carabobo", "estado": "Carabobo", "municipio": "Valencia", "telefono": "584167654321"}
    ]
if "transacciones_cerradas" not in st.session_state:
    st.session_state.transacciones_cerradas = []

# ----------------------------------------------------
# 3. ENCABEZADO CORPORATIVO AMIGABLE
# ----------------------------------------------------
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    st.markdown("<h2 style='text-align: center; color: #2E7D32;'>🌾 AgroDigital Venezuela</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #1565C0;'>Mercado Agrícola Digital (Yaracuy • Lara • Carabobo)</h4>", unsafe_allow_html=True)

st.markdown("---")

# ----------------------------------------------------
# 4. PANTALLA DE ACCESO RÁPIDO Y VISUAL (LOGIN AMIGABLE)
# ----------------------------------------------------
if not st.session_state.autenticado:
    st.markdown("<h3 style='text-align: center;'>🔐 Seleccione su Perfil para Ingresar al Sistema</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Haga clic en el botón correspondiente a su rol. ¡Diseñado para ser fácil y rápido!</p>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.info("🚜 **¿Eres Productor o Agricultor?**\n\nPublica lo que necesitas sin costo y recibe ofertas de múltiples tiendas.")
        if st.button("👉 Ingresar como Productor", use_container_width=True):
            st.session_state.autenticado = True
            st.session_state.rol_actual = "🚜 Productor"
            st.session_state.usuario_actual = "Productor Agrícola Regional"
            st.rerun()
            
    with col_b:
        st.success("🏪 **¿Eres Dueño de Agrotienda?**\n\nVende más y atiende solicitudes directas de compra en tu zona.")
        if st.button("👉 Ingresar como Agrotienda", use_container_width=True):
            st.session_state.autenticado = True
            st.session_state.rol_actual = "🏪 Agrotienda"
            st.session_state.usuario_actual = "Agrotienda Afiliada"
            st.rerun()
            
    with col_c:
        st.warning("⚙️ **Panel de Administración**\n\nControl de tasa BCV, auditoría y liquidaciones operativas.")
        if st.button("👉 Ingresar como Administrador", use_container_width=True):
            st.session_state.autenticado = True
            st.session_state.rol_actual = "⚙️ Administrador"
            st.session_state.usuario_actual = "Administrador Central"
            st.rerun()
            
    st.stop()

# ----------------------------------------------------
# 5. BARRA DE SESIÓN ACTIVA SUPERIOR (FÁCIL SALIDA)
# ----------------------------------------------------
st.sidebar.markdown(f"### 👤 Usuario: {st.session_state.usuario_actual}")
st.sidebar.markdown(f"**Rol:** {st.session_state.rol_actual}")
st.sidebar.markdown(f"💱 **Tasa BCV:** {st.session_state.tasa_bcv:.2f} VES")

if st.sidebar.button("🚪 Salir de la Plataforma", use_container_width=True):
    st.session_state.autenticado = False
    st.session_state.rol_actual = None
    st.session_state.usuario_actual = ""
    st.rerun()

st.sidebar.divider()

# ----------------------------------------------------
# 6. MENÚS PRINCIPALES SEGÚN ROL (DISEÑO VISUAL DE PESTAÑAS)
# ----------------------------------------------------
if st.session_state.rol_actual == "🚜 Productor":
    st.markdown("### 🚜 Panel de Control - Productor Agrícola")
    pestanas = st.tabs([
        "🛒 Pedir Insumo (Subasta)", 
        "📊 Mis Solicitudes y Ofertas", 
        "💳 Pagar Producto", 
        "📈 Precios del Mercado"
    ])
    
    with pestanas[0]:
        st.subheader("🛒 Solicite su Insumo en 3 Simples Pasos")
        with st.form("form_prod_facil"):
            c1, c2 = st.columns(2)
            with c1:
                est = st.selectbox("1️⃣ Su Estado:", ["Yaracuy", "Lara", "Carabobo"])
                mun = st.text_input("2️⃣ Municipio o Localidad:", placeholder="Ej. San Felipe, Iribarren, Valencia")
            with c2:
                nom = st.text_input("3️⃣ Nombre de su Finca o Productor:", placeholder="Ej. Finca San Juan")
                tel = st.text_input("4️⃣ Su Teléfono / WhatsApp de Contacto:", placeholder="04121234567")
            
            st.divider()
            ins = st.text_input("📦 ¿Qué insumo o repuesto necesita?", placeholder="Ej. Urea 46% (20 sacos), Repuesto Tractor...")
            cant = st.text_input("🔢 Cantidad requerida:", placeholder="Ej. 20 sacos / 1 unidad")
            
            enviar_subasta = st.form_submit_button("🚀 ¡Publicar Requerimiento Ahora!", use_container_width=True)
            if enviar_subasta:
                if nom and mun and ins and tel:
                    pid = len(st.session_state.pedidos) + 1
                    st.session_state.pedidos.append({
                        "id": pid, "productor": nom, "estado": est,
                        "municipio": mun, "insumo": ins, "cantidad": cant, "telefono": tel
                    })
                    st.success(f"¡Listo! Su solicitud #{pid} fue publicada. Las agrotiendas cercanas comenzarán a enviarle sus mejores precios.")
                    st.balloons()
                else:
                    st.error("⚠️ Por favor complete todos los datos para poder enviarlo.")

    with pestanas[1]:
        st.subheader("📊 Ofertas Recibidas de las Agrotiendas")
        if not st.session_state.pedidos:
            st.info("Aún no ha creado ninguna solicitud de insumo.")
        else:
            for p in st.session_state.pedidos:
                st.markdown(f"**Solicitud #{p['id']}: {p['insumo']} ({p['cantidad']})** — _{p['estado']} / {p['municipio']}_")
                ofertas_p = [o for o in st.session_state.ofertas if o["pedido_id"] == p["id"]]
                if not ofertas_p:
                    st.warning("⏳ Esperando que las agrotiendas respondan con sus precios...")
                else:
                    for o in ofertas_p:
                        col_o1, col_o2, col_o3 = st.columns([2, 2, 2])
                        with col_o1: st.write(f"🏪 **{o['tienda']}**")
                        with col_o2: st.write(f"💲 **${o['precio']:.2f} USD** (~{o['precio']*st.session_state.tasa_bcv:,.2f} VES)")
                        with col_o3:
                            if st.button(f"✅ ¡Aceptar Oferta!", key=f"btn_adj_{o['pedido_id']}_{o['tienda']}"):
                                st.session_state.transacciones_cerradas.append({
                                    "id_transaccion": len(st.session_state.transacciones_cerradas) + 1,
                                    "productor": p['productor'], "telefono_productor": p['telefono'],
                                    "tienda": o['tienda'], "telefono_tienda": o['telefono_tienda'],
                                    "insumo": p['insumo'], "cantidad": p['cantidad'], "precio": o['precio'],
                                    "zona": f"{p['estado']} - {p['municipio']}"
                                })
                                st.success("🎉 ¡Oferta aceptada con éxito! Vaya a la pestaña 'Pagar Producto' para finalizar.")
                st.divider()

    with pestanas[2]:
        st.subheader("💳 Pago Fácil del Producto Adquirido")
        if not st.session_state.transacciones_cerradas:
            st.info("No tiene transacciones pendientes de pago.")
        else:
            for t in st.session_state.transacciones_cerradas:
                monto_ves = t['precio'] * st.session_state.tasa_bcv
                st.markdown(f"### 📦 Insumo: {t['insumo']} ({t['cantidad']})")
                st.write(f"🏪 Tienda Proveedora: **{t['tienda']}** | 💲 Total a Pagar: **${t['precio']:.2f} USD**")
                st.error(f"💱 Equivalente en Bolívares (Tasa BCV {st.session_state.tasa_bcv:.2f}): **{monto_ves:,.2f} VES**")
                
                with st.form(f"pago_prod_{t['id_transaccion']}"):
                    st.info(f"🏦 **Realice Pago Móvil a:** {EMPRESA_BANCO} | Teléfono: {EMPRESA_TELEFONO} | RIF: {EMPRESA_RIF}")
                    ref = st.text_input("Ingrese los últimos 4 o 6 números de Referencia del Pago:")
                    if st.form_submit_button("✅ Reportar Pago Realizado", use_container_width=True):
                        if ref:
                            st.success("¡Pago reportado y notificado correctamente a la agrotienda!")
                            msg = f"Hola {t['tienda']}, he pagado el insumo {t['insumo']} por ${t['precio']:.2f}. Ref: {ref}"
                            url_wa = f"https://wa.me/58{t['telefono_tienda'][-10:]}?text={urllib.parse.quote(msg)}"
                            st.markdown(f"[💬 Enviar comprobante por WhatsApp a la Tienda]({url_wa})", unsafe_allow_html=True)
                        else:
                            st.error("Por favor ingrese el número de referencia bancaria.")

    with pestanas[3]:
        st.subheader("📈 Tendencias y Precios Promedio en la Región")
        ins = st.selectbox("Seleccione el insumo a consultar:", ["Urea 46%", "NPK 12-24-12", "Semilla Maíz Certificada", "Vacuna Aftosa"])
        st.line_chart(pd.DataFrame({"Semana": ["Semana 1", "Semana 2", "Semana 3", "Semana Actual"], "Precio USD": [38.0, 36.5, 35.0, 34.2]}).set_index("Semana"))

elif st.session_state.rol_actual == "🏪 Agrotienda":
    st.markdown("### 🏪 Panel de Operaciones - Agrotienda Comercial")
    pestanas_t = st.tabs([
        "🔔 Responder Solicitudes (Cotizar)", 
        "📦 Mi Catálogo de Productos", 
        "📝 Afiliación Mercantil", 
        "📈 Precios del Mercado"
    ])
    
    with pestanas_t[0]:
        st.subheader("🔔 Solicitudes Activas de Productores")
        if not st.session_state.pedidos:
            st.info("No hay solicitudes de productores en este momento. ¡Vuelva pronto!")
        else:
            for p in st.session_state.pedidos:
                st.markdown(f"### 📍 Zona: [{p['estado']}] - Municipio {p['municipio']}")
                st.write(f"📦 **Necesita:** {p['insumo']} (Cantidad: {p['cantidad']})")
                
                with st.form(f"cot_{p['id']}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        t_nom = st.text_input("Nombre de su Agrotienda:", placeholder="Ej. Agroinsumos San Felipe")
                        t_est = st.selectbox("Su Estado:", ["Yaracuy", "Lara", "Carabobo"], key=f"est_{p['id']}")
                    with c2:
                        precio = st.number_input("Precio Total de Oferta (USD $):", min_value=0.0, format="%.2f")
                        whatsapp = st.text_input("Su WhatsApp Comercial:", placeholder="04121234567")
                    
                    tiempo = st.text_input("Tiempo de Entrega / Disponibilidad:", placeholder="Ej. Entrega inmediata en tienda")
                    
                    if st.form_submit_button("💡 Enviar Oferta al Productor", use_container_width=True):
                        if t_nom and precio > 0 and whatsapp:
                            st.session_state.ofertas.append({
                                "pedido_id": p['id'], "tienda": t_nom, "estado_tienda": t_est,
                                "precio": precio, "tiempo": tiempo, "telefono_tienda": whatsapp
                            })
                            st.success("¡Oferta enviada con éxito al productor!")
                        else:
                            st.error("Por favor complete todos los datos de su oferta.")
                st.divider()

    with pestanas_t[1]:
        st.subheader("📦 Registro Rápido de Productos Frecuentes")
        with st.text_input("Nombre del Producto o Insumo:", placeholder="Ej. Fertilizante NPK") as p_nom:
            pass
        with st.number_input("Precio Referencial (USD $):", min_value=0.0, format="%.2f") as p_pre:
            pass
        if st.button("➕ Guardar en mi Catálogo"):
            st.success("¡Producto agregado con éxito!")

    with pestanas_t[2]:
        st.subheader("📝 Contrato y Registro Comercial")
        st.info("Al afiliarse, usted acepta participar en el ecosistema transparente de corretaje agrícola regional.")
        with st.form("form_reg_tienda_facil"):
            rt_nom = st.text_input("Nombre Comercial de la Tienda:")
            rt_rif = st.text_input("RIF:")
            rt_mun = st.text_input("Municipio:")
            if st.form_submit_button("Registrar Mi Agrotienda", use_container_width=True):
                st.success("¡Registro completado exitosamente!")

    with pestanas_t[3]:
        st.subheader("📈 Tendencias de Precios Regionales")
        st.line_chart(pd.DataFrame({"Semana": ["Semana 1", "Semana 2", "Semana 3", "Actual"], "Precio USD": [45, 44, 43, 42]}).set_index("Semana"))

else: # Administrador
    st.markdown("### ⚙️ Panel de Control del Administrador")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💱 Actualizar Tasa BCV Oficial")
        nueva_tasa = st.number_input("Tasa Actual USD/VES:", value=float(st.session_state.tasa_bcv), format="%.2f")
        if st.button("🔄 Guardar Nueva Tasa BCV", use_container_width=True):
            st.session_state.tasa_bcv = nueva_tasa
            st.success(f"¡Tasa actualizada a {nueva_tasa:.2f} VES/USD!")
    with col2:
        st.subheader("📊 Resumen General")
        st.metric("Subastas Activas", len(st.session_state.pedidos))
        st.metric("Agrotiendas Afiliadas", len(st.session_state.agrotiendas_registradas))
        st.metric("Transacciones Cerradas", len(st.session_state.transacciones_cerradas))
