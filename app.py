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
if "catalogo_productos" not in st.session_state:
    st.session_state.catalogo_productos = [
        {"producto": "Urea 46% Granulada (Saco 50kg)", "categoria": "Fertilizantes", "precio_ref": 35.0},
        {"producto": "NPK 12-24-12 (Saco 50kg)", "categoria": "Fertilizantes", "precio_ref": 42.0},
        {"producto": "Semilla de Maíz Blanco Certificada", "categoria": "Semillas", "precio_ref": 120.0},
        {"producto": "Vacuna Fiebre Aftosa (Dosis)", "categoria": "Sanidad Animal", "precio_ref": 2.5}
    ]
if "transacciones_cerradas" not in st.session_state:
    st.session_state.transacciones_cerradas = []
if "pagos_agrotiendas" not in st.session_state:
    st.session_state.pagos_agrotiendas = []

# ----------------------------------------------------
# 3. ENCABEZADO CORPORATIVO CON DOBLE LOGOTIPO
# ----------------------------------------------------
col_logo1, col_titulo, col_logo2 = st.columns([1, 2, 1])

logo_izq = "logoshchf4.png"
logo_der = "logo agrodigitalvenezueladeinitivo.png"

with col_logo1:
    if path.exists(logo_izq):
        st.image(logo_izq, width=180)
    else:
        st.warning(f"⚠️ Falta archivo: {logo_izq}")

with col_titulo:
    st.markdown("<h2 style='text-align: center; color: #2E7D32;'>🌾 AgroDigital Venezuela</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #1565C0;'>Mercado Agrícola Digital (Yaracuy • Lara • Carabobo)</h4>", unsafe_allow_html=True)

with col_logo2:
    if path.exists(logo_der):
        st.image(logo_der, width=180)
    else:
        st.warning(f"⚠️ Falta archivo: {logo_der}")

st.markdown("---")

# ----------------------------------------------------
# 4. CONTROL DE ACCESO Y AISLAMIENTO DE PERFILES
# ----------------------------------------------------
if not st.session_state.autenticado:
    st.markdown("<h3 style='text-align: center;'>🔐 Seleccione su Perfil de Acceso</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Cada perfil cuenta con una pantalla exclusiva y segura para sus operaciones.</p>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.info("🚜 **Productor Agrícola**\n\nPublica subastas de insumos de forma anónima y recibe ofertas.")
        if st.button("👉 Ingresar como Productor", use_container_width=True):
            st.session_state.autenticado = True
            st.session_state.rol_actual = "🚜 Productor"
            st.session_state.usuario_actual = "Productor Finca Regional"
            st.rerun()
            
    with col_b:
        st.success("🏪 **Agrotienda Comercial**\n\nCotiza solicitudes de productores y gestiona tu inventario.")
        if st.button("👉 Ingresar como Agrotienda", use_container_width=True):
            st.session_state.autenticado = True
            st.session_state.rol_actual = "🏪 Agrotienda"
            st.session_state.usuario_actual = "Agrotienda Afiliada"
            st.rerun()
            
    with col_c:
        st.warning("⚙️ **Administrador Central**\n\nAcceso maestro: control de tasa BCV, auditorías y liquidaciones.")
        with st.form("form_admin_seguro"):
            clave_adm = st.text_input("Contraseña de Administrador:", type="password")
            if st.form_submit_button("👉 Ingresar como Administrador", use_container_width=True):
                if clave_adm == "123456":
                    st.session_state.autenticado = True
                    st.session_state.rol_actual = "⚙️ Administrador"
                    st.session_state.usuario_actual = "Administrador Central"
                    st.rerun()
                else:
                    st.error("Contraseña de administrador incorrecta.")
    st.stop()

# ----------------------------------------------------
# 5. BARRA SUPERIOR DE SESIÓN Y CIERRE SEGURO
# ----------------------------------------------------
col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
with col_s1:
    st.success(f"👤 **Sesión:** {st.session_state.usuario_actual} | **Rol:** {st.session_state.rol_actual}")
with col_s2:
    st.info(f"💱 **Tasa BCV:** {st.session_state.tasa_bcv:.2f} VES/USD")
with col_s3:
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.rol_actual = None
        st.session_state.usuario_actual = ""
        st.rerun()

st.markdown("---")

# ----------------------------------------------------
# 6. ENRUTAMIENTO ESTRICTO POR ROL (AISLAMIENTO DE PANTALLAS)
# ----------------------------------------------------

# --- VISTA 1: EXCLUSIVA PARA PRODUCTORES ---
if st.session_state.rol_actual == "🚜 Productor":
    st.markdown("### 🚜 Módulo Exclusivo - Productor Agrícola")
    pestanas_prod = st.tabs([
        "🛒 Lanzar Subasta", 
        "📊 Mis Pujas y Ofertas", 
        "💳 Pagar Insumo", 
        "📈 Tendencias",
        "🚜 Requerimientos"
    ])
    
    with pestanas_prod[0]:
        st.subheader("🛒 Solicite su Insumo en 3 Sencillos Pasos")
        with st.form("form_prod_facil"):
            c1, c2 = st.columns(2)
            with c1:
                estado_prod = st.selectbox("1️⃣ Su Estado:", ["Yaracuy", "Lara", "Carabobo"], key="s_est")
                municipio_prod = st.text_input("2️⃣ Municipio o Localidad:", placeholder="Ej. San Felipe, Iribarren...", key="s_mun")
            with c2:
                nombre_prod = st.text_input("3️⃣ Nombre de Finca / Productor:", placeholder="Ej. Finca El Carmen", key="s_nom")
                tel_prod = st.text_input("4️⃣ WhatsApp de Contacto:", placeholder="04121234567", key="s_tel")
            
            st.divider()
            insumo_req = st.text_input("📦 Insumo o Repuesto Necesario:", placeholder="Ej. Urea 46%, Filtro...")
            cant_req = st.text_input("🔢 Cantidad:", placeholder="Ej. 20 sacos")
            
            if st.form_submit_button("🚀 Publicar Subasta Inversa", use_container_width=True):
                if nombre_prod and municipio_prod and insumo_req and tel_prod:
                    pid = len(st.session_state.pedidos) + 1
                    st.session_state.pedidos.append({
                        "id": pid, "productor": nombre_prod, "estado": estado_prod,
                        "municipio": municipio_prod, "insumo": insumo_req, "cantidad": cant_req, "telefono": tel_prod
                    })
                    st.success(f"¡Subasta Inversa #{pid} publicada con éxito!")
                else:
                    st.error("Complete todos los campos obligatorios.")

    with pestanas_prod[1]:
        st.subheader("📊 Seguimiento de Ofertas Recibidas")
        if not st.session_state.pedidos:
            st.info("No tiene solicitudes activas.")
        else:
            for p in st.session_state.pedidos:
                with st.expander(f"📦 Solicitud #{p['id']}: {p['insumo']} ({p['cantidad']})"):
                    ofertas_p = [o for o in st.session_state.ofertas if o["pedido_id"] == p["id"]]
                    if not ofertas_p:
                        st.caption("⏳ Esperando respuestas de las agrotiendas...")
                    else:
                        for o in ofertas_p:
                            c1, c2, c3 = st.columns([2, 2, 2])
                            with c1: st.write(f"🏪 **{o['tienda']}**")
                            with c2: st.write(f"💲 **${o['precio']:.2f} USD**")
                            with c3:
                                if st.button(f"✅ Aceptar Oferta", key=f"adj_{o['pedido_id']}_{o['tienda']}"):
                                    st.session_state.transacciones_cerradas.append({
                                        "id_transaccion": len(st.session_state.transacciones_cerradas) + 1,
                                        "productor": p['productor'], "telefono_productor": p['telefono'],
                                        "tienda": o['tienda'], "telefono_tienda": o['telefono_tienda'],
                                        "insumo": p['insumo'], "cantidad": p['cantidad'], "precio": o['precio'],
                                        "zona": f"{p['estado']} - {p['municipio']}"
                                    })
                                    st.success("¡Oferta adjudicada! Vaya a la pestaña de pagos.")

    with pestanas_prod[2]:
        st.subheader("💳 Pasarela de Pago de Insumo Adquirido")
        if not st.session_state.transacciones_cerradas:
            st.info("Sin transacciones pendientes de pago.")
        else:
            for t in st.session_state.transacciones_cerradas:
                monto_ves = t['precio'] * st.session_state.tasa_bcv
                st.write(f"📦 **{t['insumo']}** | Tienda: {t['tienda']} | **${t['precio']:.2f} USD** (~{monto_ves:,.2f} VES)")
                ref = st.text_input("Número de Referencia de Pago Móvil:", key=f"ref_p_{t['id_transaccion']}")
                if st.button("Confirmar Pago", key=f"btn_p_{t['id_transaccion']}"):
                    if ref:
                        st.success("¡Pago reportado a la agrotienda con éxito!")
                    else:
                        st.error("Ingrese el número de referencia.")

    with pestanas_prod[3]:
        st.subheader("📈 Tendencias de Precios Regionales")
        st.line_chart(pd.DataFrame({"Semana": ["Sem 1", "Sem 2", "Sem 3", "Actual"], "USD": [38, 36.5, 35, 34.2]}).set_index("Semana"))

    with pestanas_prod[4]:
        st.subheader("🚜 Directorio de Insumos")
        st.write("• Fertilizantes y Nutrición\n• Sanidad Animal\n• Maquinaria y Repuestos")

# --- VISTA 2: EXCLUSIVA PARA AGROTIENDAS ---
elif st.session_state.rol_actual == "🏪 Agrotienda":
    st.markdown("### 🏪 Módulo Exclusivo - Agrotienda Comercial")
    pestanas_tienda = st.tabs([
        "🏪 Cotizar Solicitudes", 
        "📦 Mi Inventario", 
        "📝 Afiliación Mercantil", 
        "📈 Tendencias",
        "💳 Pago Móvil BDV"
    ])
    
    with pestanas_tienda[0]:
        st.subheader("🏪 Panel de Cotización Abierta")
        if not st.session_state.pedidos:
            st.warning("No hay solicitudes activas de productores.")
        else:
            for p in st.session_state.pedidos:
                st.markdown(f"**Zona:** [{p['estado']}] - **Necesita:** {p['insumo']} ({p['cantidad']})")
                with st.form(f"cot_{p['id']}"):
                    t_nom = st.text_input("Nombre de su Agrotienda:")
                    precio = st.number_input("Precio Total Ofertado (USD $):", min_value=0.0, format="%.2f")
                    whatsapp = st.text_input("WhatsApp Comercial:")
                    if st.form_submit_button("Enviar Oferta"):
                        if t_nom and precio > 0:
                            st.session_state.ofertas.append({
                                "pedido_id": p['id'], "tienda": t_nom, "estado_tienda": p['estado'],
                                "precio": precio, "tiempo": "Inmediato", "telefono_tienda": whatsapp
                            })
                            st.success("¡Puja enviada correctamente!")

    with pestanas_tienda[1]:
        st.subheader("📦 Catálogo de Productos Frecuentes")
        st.dataframe(pd.DataFrame(st.session_state.catalogo_productos), use_container_width=True)

    with pestanas_tienda[2]:
        st.subheader("📝 Contrato de Adhesión Mercantil")
        st.info("Las operaciones se rigen por las normativas de corretaje digital de la región.")

    with pestanas_tienda[3]:
        st.subheader("📈 Tendencias de Precios")
        st.line_chart(pd.DataFrame({"Semana": ["Sem 1", "Sem 2", "Sem 3", "Actual"], "USD": [45, 44, 43, 42]}).set_index("Semana"))

    with pestanas_tienda[4]:
        st.subheader("📲 Pasarela de Pago Móvil")
        st.info(f"Banco: {EMPRESA_BANCO} | Teléfono: {EMPRESA_TELEFONO} | RIF: {EMPRESA_RIF}")

# --- VISTA 3: EXCLUSIVA PARA EL ADMINISTRADOR (ACCESO TOTAL) ---
elif st.session_state.rol_actual == "⚙️ Administrador":
    st.markdown("### ⚙️ Panel Maestro - Administrador Central (Acceso Total)")
    pestanas_adm = st.tabs([
        "📊 Tasa BCV y Métricas", 
        "📑 Auditoría", 
        "💸 Liquidación a Tiendas", 
        "📊 Reportes Contables",
        "💬 Agradecimientos",
        "📄 Notas de Entrega (PDF)"
    ])
    
    with pestanas_adm[0]:
        nueva_tasa = st.number_input("Modificar Tasa USD/VES Referencial:", value=float(st.session_state.tasa_bcv), format="%.2f")
        if st.button("🔄 Actualizar Tasa BCV"):
            st.session_state.tasa_bcv = nueva_tasa
            st.success(f"¡Tasa actualizada a {nueva_tasa:.2f} VES!")
        st.metric("Subastas Activas", len(st.session_state.pedidos))
        st.metric("Agrotiendas Afiliadas", len(st.session_state.agrotiendas_registradas))

    with pestanas_adm[1]:
        st.subheader("📑 Auditoría General")
        st.write(st.session_state.transacciones_cerradas if st.session_state.transacciones_cerradas else "Sin transacciones cerradas.")

    with pestanas_adm[2]:
        st.subheader("💸 Liquidación de Pagos a Agrotiendas")
        st.write("Módulo de transferencia neta y comisiones de corretaje operativo.")

    with pestanas_adm[3]:
        st.subheader("📊 Reportes Contables")
        if st.session_state.transacciones_cerradas:
            df_exp = pd.DataFrame(st.session_state.transacciones_cerradas)
            st.dataframe(df_exp, use_container_width=True)
            st.download_button("📥 Descargar CSV", df_exp.to_csv(index=False).encode('utf-8'), "reporte.csv", "text/csv")
        else:
            st.info("Sin datos contables disponibles.")

    with pestanas_adm[4]:
        st.subheader("💬 Gestión de Mensajería y Agradecimientos")
        tel_prod_adm = st.text_input("Teléfono del Productor:")
        nom_prod_adm = st.text_input("Nombre:")
        if st.button("Generar Enlace WhatsApp"):
            if tel_prod_adm and nom_prod_adm:
                msg = f"¡Estimado {nom_prod_adm}! Gracias por usar {EMPRESA_NOMBRE}."
                url = f"https://wa.me/58{tel_prod_adm[-10:]}?text={urllib.parse.quote(msg)}"
                st.markdown(f"[💬 Enviar mensaje]({url})", unsafe_allow_html=True)

    with pestanas_adm[5]:
        st.subheader("📄 Generador de Notas de Entrega PDF")
        if not st.session_state.transacciones_cerradas:
            st.info("No hay transacciones para generar PDF.")
        else:
            for t in st.session_state.transacciones_cerradas:
                if st.button(f"📥 Descargar PDF Transacción #{t['id_transaccion']}", key=f"pdf_{t['id_transaccion']}"):
                    class PDF(FPDF):
                        def header(self):
                            self.set_font("Arial", "B", 14)
                            self.cell(0, 10, EMPRESA_NOMBRE, 0, 1, "C")
                    pdf = PDF()
                    pdf.add_page()
                    pdf.set_font("Arial", "", 10)
                    pdf.cell(0, 8, f"Transaccion #{t['id_transaccion']} - {t['insumo']} (${t['precio']} USD)", 0, 1)
                    fn = f"Nota_{t['id_transaccion']}.pdf"
                    pdf.output(fn)
                    with open(fn, "rb") as f:
                        st.download_button("⬇️ Descargar Archivo PDF", f, fn, "application/pdf")
