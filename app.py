import streamlit as st
import pandas as pd
import urllib.parse
from os import path
from datetime import datetime
from fpdf import FPDF

# Configuración de la página
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
# INICIALIZACIÓN DE ESTADOS GLOBALES
# ----------------------------------------------------
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

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "rol_actual" not in st.session_state:
    st.session_state.rol_actual = None
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = ""

# ----------------------------------------------------
# SECCIÓN CORPORATIVA: ENCABEZADO Y LOGOS
# ----------------------------------------------------
col_l1, col_l2 = st.columns(2)
with col_l1:
    if path.exists("logo.png"):
        st.image("logo.png", width=200)
    elif path.exists("logoshchf4.png"):
        st.image("logo agrodigitalvenezueladeinitivo.png", width=200)
    else:
        st.markdown(f"### 🌾 {EMPRESA_NOMBRE}")

with col_l2:
    if path.exists("logo agrodigitalvenezueladeinitivo.png"):
        st.image("logo agrodigitalvenezueladeinitivo.png", width=200)
    elif path.exists("logo.png"):
        st.image("logo.png", width=200)
    else:
        st.markdown("### 💻 AgroDigital Venezuela")

st.markdown("<h3 style='text-align: center; color: #1565C0;'>Plataforma Segura con Autenticación y Control de Roles</h3>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: #2E7D32;'>Eje de Operaciones: Yaracuy - Lara - Carabobo</h5>", unsafe_allow_html=True)

# ----------------------------------------------------
# VISTA PRINCIPAL: OBJETIVOS DEL NEGOCIO
# ----------------------------------------------------
st.markdown("---")
st.markdown("<h3 style='text-align: center; color: #1565C0;'>🌾 Ecosistema Digital AgroYaracuy</h3>", unsafe_allow_html=True)

with st.container():
    st.info(
        "💡 **Nuestro Objetivo:** Eliminar la intermediación costosa y conectar de forma transparente "
        "a los productores agrícolas de Yaracuy, Lara y Carabobo con las agrotiendas de la región mediante subastas en tiempo real."
    )
    
    col_prod, col_tienda = st.columns(2)
    with col_prod:
        st.markdown(
            "#### 🚜 Para el Productor\n"
            "• **Ahorro de Tiempo y Dinero:** Consigue el mejor precio de insumos sin salir de tu finca.\n"
            "• **Subasta Anónima:** Tu identidad y teléfono están protegidos hasta que decidas comprar.\n"
            "• **Acceso Gratuito:** Publica tus requerimientos sin costo alguno."
        )
    with col_tienda:
        st.markdown(
            "#### 🏪 Para la Agrotienda\n"
            "• **Clientes Directos:** Recibe solicitudes de compra reales todos los días.\n"
            "• **Mayor Rotación:** Vende tu inventario de fertilizantes, semillas y repuestos rápidamente.\n"
            "• **Respaldo Legal:** Transacciones protegidas por contrato mercantil y pasarela oficial."
        )

st.markdown("---")

# ----------------------------------------------------
# CONTROL DE ACCESO: LOGIN OBLIGATORIO
# ----------------------------------------------------
if not st.session_state.autenticado:
    st.sidebar.markdown("### 🔐 Iniciar Sesión en el Sistema")
    st.sidebar.info("Ingrese sus credenciales para acceder al módulo correspondiente.")
    
    with st.sidebar.form("form_login"):
        input_usuario = st.text_input("Usuario o Cédula/RIF:")
        input_clave = st.text_input("Contraseña:", type="password")
        btn_login = st.form_submit_button("Entrar al Sistema")
        
        if btn_login:
            credenciales = {
                "admin": {"rol": "⚙️ Administrador", "nombre": "Administrador Central"},
                "agrotienda": {"rol": "🏪 Agrotienda", "nombre": "Agrotienda Afiliada"},
                "productor": {"rol": "🚜 Productor", "nombre": "Productor Agrícola"}
            }
            
            if input_usuario in credenciales and input_clave == "123456":
                st.session_state.autenticado = True
                st.session_state.rol_actual = credenciales[input_usuario]["rol"]
                st.session_state.usuario_actual = credenciales[input_usuario]["nombre"]
                st.toast(f"¡Bienvenido(a) {credenciales[input_usuario]['nombre']}!", icon="👋")
                st.rerun()
            else:
                st.sidebar.error("Usuario o contraseña incorrectos.")
    
    st.warning("⚠️ **Acceso Restringido:** Debe iniciar sesión en el panel lateral para utilizar las herramientas del sistema.")
    st.stop()

# ----------------------------------------------------
# SESIÓN ACTIVA Y MENÚ POR ROLES
# ----------------------------------------------------
st.sidebar.markdown("### 👤 Sesión Activa")
st.sidebar.success(f"**Usuario:** {st.session_state.usuario_actual}\n\n**Rol:** {st.session_state.rol_actual}\n\n**Tasa BCV:** {st.session_state.tasa_bcv:.2f} VES")

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.autenticado = False
    st.session_state.rol_actual = None
    st.session_state.usuario_actual = ""
    st.rerun()

st.sidebar.divider()
st.sidebar.markdown("### 🧭 Menú Autorizado")

if st.session_state.rol_actual == "🚜 Productor":
    menu = st.sidebar.selectbox("Seleccione Módulo:", [
        "🛒 Lanzar Subasta Inversa (Anónima)",
        "📊 Mis Pujas y Adjudicación",
        "💳 Pagar Producto Adquirido",
        "📈 Tendencias de Precios del Mercado",
        "🚜 Requerimientos del Campo"
    ])

elif st.session_state.rol_actual == "🏪 Agrotienda":
    menu = st.sidebar.selectbox("Seleccione Módulo:", [
        "🏪 Panel de Cotización Abierta",
        "📦 Mi Catálogo de Inventario Frecuente",
        "📝 Afiliación y Contrato Mercantil",
        "📈 Tendencias de Precios del Mercado",
        "💳 Pasarela de Pago Móvil BDV"
    ])

else: # Administrador
    menu = st.sidebar.selectbox("Seleccione Módulo:", [
        "📊 Panel General y Tasa BCV (24h)",
        "📑 Auditoría Detallada de Transacciones",
        "💸 Liquidación y Pagos a Agrotiendas",
        "📊 Reportes Contables Exportables",
        "💬 Gestión de Agradecimiento",
        "📄 Generador de Notas de Entrega (PDF)"
    ])

# ----------------------------------------------------
# EJECUCIÓN DE MÓDULOS SEGÚN ROL
# ----------------------------------------------------

# --- MÓDULOS DE PRODUCTOR ---
if menu == "🛒 Lanzar Subasta Inversa (Anónima)":
    st.header("🛒 Módulo de Subasta Inversa (Asistente Interactivo)")
    st.markdown("Publique su necesidad de insumos en 3 sencillos pasos. Sus datos de contacto permanecen estrictamente ocultos.")
    
    tab_p1, tab_p2, tab_p3 = st.tabs(["📍 1. Ubicación de la Finca", "📦 2. Detalle del Insumo", "🚀 3. Confirmación"])
    
    with tab_p1:
        st.subheader("Paso 1: Seleccione la Zona Geográfica")
        estado_prod = st.selectbox("Estado:", ["Yaracuy", "Lara", "Carabobo"], key="s_est")
        municipio_prod = st.text_input("Municipio / Sector:", placeholder="Ej. San Felipe, Bruzual, Iribarren...", key="s_mun")
        nombre_prod = st.text_input("Nombre de Finca / Productor:", placeholder="Ej. Finca El Carmen", key="s_nom")
        tel_prod = st.text_input("WhatsApp Privado de Contacto:", placeholder="04121234567", key="s_tel")

    with tab_p2:
        st.subheader("Paso 2: Especifique el Requerimiento")
        insumo_req = st.text_input("Insumo / Repuesto Solicitado:", placeholder="Ej. Urea 46%, Filtro de Aceite Tractor...", key="s_ins")
        cant_req = st.text_input("Cantidad Necesaria:", placeholder="Ej. 20 sacos, 2 unidades...", key="s_can")

    with tab_p3:
        st.subheader("Paso 3: Verificación y Emisión")
        st.write(f"• **Productor / Finca:** {nombre_prod if nombre_prod else 'Pendiente'}")
        st.write(f"• **Ubicación:** {estado_prod} - {municipio_prod if municipio_prod else 'Pendiente'}")
        st.write(f"• **Requerimiento:** {insumo_req if insumo_req else 'Pendiente'} ({cant_req if cant_req else 'N/A'})")
        
        if st.button("🚀 Lanzar Subasta Inversa en la Red"):
            if nombre_prod and municipio_prod and insumo_req and tel_prod:
                pid = len(st.session_state.pedidos) + 1
                st.session_state.pedidos.append({
                    "id": pid, "productor": nombre_prod, "estado": estado_prod,
                    "municipio": municipio_prod, "insumo": insumo_req, "cantidad": cant_req, "telefono": tel_prod
                })
                st.toast("¡Subasta emitida exitosamente!", icon="✅")
                st.success(f"¡Subasta Inversa #{pid} publicada con éxito! Las agrotiendas regionales comenzarán a pujar.")
            else:
                st.error("Por favor complete todos los datos requeridos.")

elif menu == "📊 Mis Pujas y Adjudicación":
    st.header("📊 Seguimiento de Pujas y Adjudicación")
    if not st.session_state.pedidos:
        st.info("No tiene solicitudes de subasta activas en este momento.")
    else:
        for p in st.session_state.pedidos:
            with st.expander(f"📦 Subasta #{p['id']}: {p['insumo']} ({p['cantidad']}) — [{p['estado']} / {p['municipio']}]", expanded=True):
                ofertas_p = [o for o in st.session_state.ofertas if o["pedido_id"] == p["id"]]
                
                if not ofertas_p:
                    st.caption("_Las agrotiendas están analizando su requerimiento..._")
                else:
                    for o in sorted(ofertas_p, key=lambda x: x["precio"]):
                        c1, c2, c3 = st.columns([2, 2, 2])
                        with c1: st.write(f"🏪 **{o['tienda']}** ({o['estado_tienda']})")
                        with c2: st.write(f"💲 **${o['precio']:.2f} USD** (~{o['precio']*st.session_state.tasa_bcv:,.2f} VES) | {o['tiempo']}")
                        with c3:
                            if st.button(f"✅ Adjudicar Oferta #{o['pedido_id']}", key=f"adj_{o['pedido_id']}_{o['tienda']}"):
                                st.session_state.transacciones_cerradas.append({
                                    "id_transaccion": len(st.session_state.transacciones_cerradas) + 1,
                                    "productor": p['productor'], "telefono_productor": p['telefono'],
                                    "tienda": o['tienda'], "telefono_tienda": o['telefono_tienda'],
                                    "insumo": p['insumo'], "cantidad": p['cantidad'], "precio": o['precio'],
                                    "zona": f"{p['estado']} - {p['municipio']}"
                                })
                                st.toast("¡Oferta Adjudicada!", icon="🎉")
                                st.success("¡Adjudicación exitosa! Proceda al pago en la sección 'Pagar Producto Adquirido'.")
                                msg = f"Hola {o['tienda']}, he adjudicado su oferta de ${o['precio']:.2f} en {EMPRESA_NOMBRE}."
                                url_wa = f"https://wa.me/58{o['telefono_tienda'][-10:]}?text={urllib.parse.quote(msg)}"
                                st.markdown(f"[💬 Contactar Agrotienda vía WhatsApp]({url_wa})", unsafe_allow_html=True)

elif menu == "💳 Pagar Producto Adquirido":
    st.header("💳 Pasarela de Pago del Producto Adquirido")
    st.markdown("Realice el pago de los insumos adjudicados en subasta.")
    
    if not st.session_state.transacciones_cerradas:
        st.info("No tiene transacciones adjudicadas pendientes de pago actualmente.")
    else:
        for t in st.session_state.transacciones_cerradas:
            monto_ves_prod = t['precio'] * st.session_state.tasa_bcv
            with st.container():
                st.markdown(f"### 📦 Transacción #{t['id_transaccion']} - {t['insumo']} ({t['cantidad']})")
                st.write(f"🏪 **Agrotienda Proveedora:** {t['tienda']} | 💲 **Monto USD:** ${t['precio']:.2f}")
                st.info(f"💱 **Monto equivalente en Bolívares (Tasa BCV {st.session_state.tasa_bcv:.2f}):** **{monto_ves_prod:,.2f} VES**")
                
                with st.form(f"form_pago_prod_{t['id_transaccion']}"):
                    st.markdown(f"🏦 **Pago Móvil BDV:** {EMPRESA_BANCO} | Teléfono: {EMPRESA_TELEFONO} | RIF: {EMPRESA_RIF}")
                    ref_pago_prod = st.text_input("Número de Referencia Bancaria:", key=f"ref_{t['id_transaccion']}")
                    banco_origen_prod = st.text_input("Banco Emisor:", key=f"banco_{t['id_transaccion']}")
                    
                    if st.form_submit_button("Confirmar Pago del Insumo"):
                        if ref_pago_prod:
                            st.toast("¡Pago reportado con éxito!", icon="💸")
                            st.success("¡Pago validado y notificado!")
                            msg_pago_prod = f"Hola {t['tienda']}, he pagado el insumo {t['insumo']} por ${t['precio']:.2f} ({monto_ves_prod:,.2f} VES). Ref: {ref_pago_prod}."
                            url_wa_pago = f"https://wa.me/58{t['telefono_tienda'][-10:]}?text={urllib.parse.quote(msg_pago_prod)}"
                            st.markdown(f"[📲 Notificar Pago a la Agrotienda vía WhatsApp]({url_wa_pago})", unsafe_allow_html=True)
                        else:
                            st.error("Por favor ingrese el número de referencia bancaria.")
                st.divider()

elif menu == "📈 Tendencias de Precios del Mercado":
    st.header("📈 Visualizador Bursátil y Tendencias de Precios")
    st.markdown("Consulte la evolución del precio promedio de insumos clave en Yaracuy, Lara y Carabobo.")
    
    insumo_grafico = st.selectbox("Seleccione Insumo:", ["Urea 46%", "NPK 12-24-12", "Semilla Maíz Certificada", "Vacuna Aftosa Bovino"])
    
    datos_tendencia = {
        "Semana": ["Semana 1", "Semana 2", "Semana 3", "Semana 4 (Actual)"],
        "Precio Promedio (USD)": [38.0, 36.5, 35.0, 34.2] if insumo_grafico == "Urea 46%" else [45.0, 44.0, 43.5, 42.0]
    }
    st.line_chart(pd.DataFrame(datos_tendencia).set_index("Semana"))

elif menu == "🚜 Requerimientos del Campo":
    st.header("📋 Directorio de Insumos y Urgencias Agrícolas")
    st.write("• Fertilizantes y Nutrición de Suelos (Urea, NPK)\n• Sanidad y Vacunación Animal\n• Agroquímicos y Control de Plagas\n• Maquinaria y Repuestos Críticos\n• Semillas Certificadas")


# --- MÓDULOS DE AGROTIENDA ---
elif menu == "📦 Mi Catálogo de Inventario Frecuente":
    st.header("📦 Gestión de Inventario de Productos Frecuentes")
    st.markdown("Cargue sus productos recurrentes para responder cotizaciones de subastas con rapidez.")
    
    with st.form("form_add_prod_cat"):
        c_prod_nom = st.text_input("Nombre del Insumo / Repuesto:")
        c_prod_cat = st.selectbox("Categoría:", ["Fertilizantes", "Semillas", "Agroquímicos", "Sanidad Animal", "Maquinaria"])
        c_prod_precio = st.number_input("Precio Referencial (USD $):", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("➕ Agregar al Catálogo"):
            if c_prod_nom and c_prod_precio > 0:
                st.session_state.catalogo_productos.append({
                    "producto": c_prod_nom, "categoria": c_prod_cat, "precio_ref": c_prod_precio
                })
                st.toast("Producto agregado al catálogo", icon="📦")
                st.success("¡Insumo registrado exitosamente!")
            else:
                st.error("Ingrese nombre y precio válido.")
                
    st.subheader("📋 Insumos Frecuentes Registrados")
    st.dataframe(pd.DataFrame(st.session_state.catalogo_productos), use_container_width=True)

elif menu == "🏪 Panel de Cotización Abierta":
    st.header("🏪 Panel de Cotización y Competencia (Agrotiendas)")
    st.markdown("Filtre solicitudes por estado y envíe sus mejores ofertas de precio.")
    
    filtro_estados = st.multiselect("Filtrar Solicitudes por Estado:", ["Yaracuy", "Lara", "Carabobo"], default=["Yaracuy", "Lara", "Carabobo"])
    pedidos_filtrados = [p for p in st.session_state.pedidos if p['estado'] in filtro_estados]
    
    if not pedidos_filtrados:
        st.warning("No hay solicitudes activas en las zonas seleccionadas actualmente.")
    else:
        for p in pedidos_filtrados:
            with st.container():
                st.markdown(f"### 🔔 Requerimiento #{p['id']} - Zona: [{p['estado']}] Municipio {p['municipio']}")
                st.write(f"**Insumo Solicitado:** {p['insumo']} | **Cantidad:** {p['cantidad']}")
                st.info("🔒 _Identidad del productor protegida._")
                
                with st.form(f"form_cot_{p['id']}"):
                    c_a, c_b = st.columns(2)
                    with c_a:
                        tienda_nombre = st.text_input("Nombre de su Agrotienda:", key=f"tn_{p['id']}")
                        tienda_estado = st.selectbox("Estado de su Tienda:", ["Yaracuy", "Lara", "Carabobo"], key=f"te_{p['id']}")
                    with c_b:
                        precio_ofertado = st.number_input("Precio Total Ofertado (USD $):", min_value=0.0, format="%.2f", key=f"tp_{p['id']}")
                        st.caption(f"Equivalente en Bolívares BCV: ~{precio_ofertado * st.session_state.tasa_bcv:,.2f} VES")
                    
                    tiempo_entrega = st.text_input("Disponibilidad / Tiempo de Entrega:", key=f"tt_{p['id']}")
                    telefono_tienda = st.text_input("WhatsApp Comercial de Su Tienda:", key=f"tel_{p['id']}")
                    
                    if st.form_submit_button("💡 Enviar Puja Competitiva"):
                        if tienda_nombre and precio_ofertado > 0:
                            st.session_state.ofertas.append({
                                "pedido_id": p['id'], "tienda": tienda_nombre, "estado_tienda": tienda_estado,
                                "precio": precio_ofertado, "tiempo": tiempo_entrega, "telefono_tienda": telefono_tienda
                            })
                            st.toast("¡Puja enviada a la subasta!", icon="💰")
                            st.success("¡Oferta publicada exitosamente!")
                        else:
                            st.error("Ingrese su nombre comercial y un precio válido.")
                st.divider()

elif menu == "📝 Afiliación y Contrato Mercantil":
    st.header("📝 Contrato de Adhesión e Incorporación Comercial")
    tab_c1, tab_c2 = st.tabs(["📄 Contrato Legal de Corretaje", "✍️ Formulario de Registro"])
    
    with tab_c1:
        st.markdown(f"**CONTRATO DE ADHESIÓN MERCANTIL — {EMPRESA_NOMBRE} (RIF: {EMPRESA_RIF})**")
        st.write("PRIMERA: La agrotienda operará bajo el modelo de corretaje digital y subasta inversa.")
        st.write("SEGUNDA: Prohibida la elusión o trato directo fuera de plataforma previo a la adjudicación.")
        st.write(f"TERCERA: Operaciones bancarias centralizadas mediante {EMPRESA_BANCO}, Pagomóvil: {EMPRESA_TELEFONO}.")
        
    with tab_c2:
        with st.form("form_afilia_t"):
            t_nom = st.text_input("Nombre Comercial de la Agrotienda:")
            t_rif = st.text_input("RIF de la Empresa:")
            t_est = st.selectbox("Estado de Ubicación:", ["Yaracuy", "Lara", "Carabobo"])
            t_mun = st.text_input("Municipio:")
            t_tel = st.text_input("WhatsApp Comercial:")
            t_acepta = st.checkbox("✅ Acepto los términos del contrato de adhesión mercantil.")
            
            if st.form_submit_button("Firmar Adhesión y Registrar"):
                if t_acepta and t_nom and t_rif:
                    st.session_state.agrotiendas_registradas.append({"nombre": t_nom, "estado": t_est, "municipio": t_mun, "telefono": t_tel})
                    st.toast("¡Agrotienda Afiliada!", icon="🏢")
                    st.success(f"¡Felicidades! {t_nom} ha sido registrada exitosamente.")
                else:
                    st.error("Debe completar los campos obligatorios.")


# --- MÓDULOS DE ADMINISTRADOR ---
elif menu == "📊 Panel General y Tasa BCV (24h)":
    st.header("⚙️ Panel de Control del Administrador y Tasa Oficial")
    col_adm1, col_adm2 = st.columns(2)
    with col_adm1:
        st.subheader("💱 Actualizador de Tasa BCV (24h)")
        nueva_tasa = st.number_input("Modificar Tasa USD/VES Referencial:", value=float(st.session_state.tasa_bcv), format="%.2f")
        if st.button("🔄 Guardar y Actualizar Tasa BCV"):
            st.session_state.tasa_bcv = nueva_tasa
            st.toast("Tasa BCV Sincronizada", icon="💱")
            st.success(f"¡Tasa BCV actualizada a {nueva_tasa:.2f} VES/USD!")
        st.caption(f"📅 Última sincronización: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
    with col_adm2:
        st.subheader("📈 Resumen del Ecosistema")
        st.metric("Subastas Activas", len(st.session_state.pedidos))
        st.metric("Agrotiendas Afiliadas", len(st.session_state.agrotiendas_registradas))
        st.metric("Transacciones Cerradas", len(st.session_state.transacciones_cerradas))

elif menu == "📊 Reportes Contables Exportables":
    st.header("📊 Reportes Contables y Balances Exportables")
    st.markdown("Exporte el balance auditado de comisiones y transacciones a formato CSV/Excel.")
    
    if not st.session_state.transacciones_cerradas:
        st.info("Sin transacciones cerradas para exportar.")
    else:
        df_export = pd.DataFrame(st.session_state.transacciones_cerradas)
        st.dataframe(df_export, use_container_width=True)
        
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte de Transacciones (CSV)",
            data=csv_data,
            file_name=f"Reporte_AgroYaracuy_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

elif menu == "📑 Auditoría Detallada de Transacciones":
    st.header("📑 Auditoría Detallada de Transacciones Cerradas")
    if not st.session_state.transacciones_cerradas:
        st.info("No hay transacciones cerradas registradas actualmente.")
    else:
        for t in st.session_state.transacciones_cerradas:
            monto_ves_audit = t['precio'] * st.session_state.tasa_bcv
            with st.container():
                st.markdown(f"### 📋 Transacción ID #{t['id_transaccion']}")
                col_a, col_b, col_c = st.columns(3)
                with col_a: st.write(f"**🚜 Productor:** {t['productor']}\n\nTelf: {t['telefono_productor']}")
                with col_b: st.write(f"**🏪 Agrotienda:** {t['tienda']}\n\nTelf: {t['telefono_tienda']}")
                with col_c: st.write(f"**📦 Producto:** {t['insumo']}\n\nCantidad: {t['cantidad']}")
                st.markdown(f"💲 **Precio Pujado:** **${t['precio']:.2f} USD** (~{monto_ves_audit:,.2f} VES)")
                st.divider()

elif menu == "💸 Liquidación y Pagos a Agrotiendas":
    st.header("💸 Módulo de Liquidación y Pago a Agrotiendas")
    if not st.session_state.transacciones_cerradas:
        st.info("No hay transacciones cerradas para liquidar.")
    else:
        comision_porcentaje = st.slider("Margen / Comisión de Corretaje (%):", min_value=1.0, max_value=10.0, value=3.0, step=0.5)
        st.divider()
        
        for t in st.session_state.transacciones_cerradas:
            monto_total_usd = t['precio']
            comision_empresa_usd = monto_total_usd * (comision_porcentaje / 100.0)
            monto_neto_agrotienda_usd = monto_total_usd - comision_empresa_usd
            monto_neto_ves = monto_neto_agrotienda_usd * st.session_state.tasa_bcv
            
            with st.container():
                st.markdown(f"### 🧾 Liquidación Transacción #{t['id_transaccion']} - {t['tienda']}")
                st.write(f"• **Insumo:** {t['insumo']} ({t['cantidad']}) | **Monto Total:** ${monto_total_usd:.2f} USD")
                st.write(f"• **Comisión Empresa ({comision_porcentaje}%):** ${comision_empresa_usd:.2f} USD")
                st.success(f"💰 **Monto Neto Agrotienda:** **${monto_neto_agrotienda_usd:.2f} USD** (~{monto_neto_ves:,.2f} VES)")
                
                with st.form(f"form_liq_{t['id_transaccion']}"):
                    ref_pago_agro = st.text_input("Referencia de Transferencia a Agrotienda:")
                    if st.form_submit_button("Registrar Liquidación"):
                        if ref_pago_agro:
                            st.session_state.pagos_agrotiendas.append({
                                "id_transaccion": t['id_transaccion'], "agrotienda": t['tienda'],
                                "monto_neto_usd": monto_neto_agrotienda_usd, "referencia": ref_pago_agro
                            })
                            st.toast("Liquidación Registrada", icon="🏦")
                            st.success(f"¡Pago a {t['tienda']} registrado!")
                        else:
                            st.error("Ingrese número de referencia.")
                st.divider()

elif menu == "💬 Gestión de Agradecimiento":
    st.header("💬 Gestión de Agradecimiento a Productores")
    with st.form("form_agradecimiento_admin"):
        prod_telf_adm = st.text_input("Teléfono WhatsApp del Productor:")
        prod_nombre_adm = st.text_input("Nombre del Productor / Finca:")
        
        if st.form_submit_button("Generar Enlace WhatsApp"):
            if prod_telf_adm and prod_nombre_adm:
                msg_agradecimiento_adm = f"¡Estimado(a) {prod_nombre_adm}! De parte de {EMPRESA_NOMBRE} (AgroDigital Venezuela), le agradecemos la confianza al utilizar nuestra plataforma para potenciar su producción."
                url_wa_adm = f"https://wa.me/58{prod_telf_adm[-10:]}?text={urllib.parse.quote(msg_agradecimiento_adm)}"
                st.toast("Enlace Generado", icon="📲")
                st.markdown(f"[💬 Enviar mensaje vía WhatsApp]({url_wa_adm})", unsafe_allow_html=True)
            else:
                st.error("Complete los datos requeridos.")

elif menu == "📄 Generador de Notas de Entrega (PDF)":
    st.header("📄 Generador de Documentación Legal (PDF)")
    if not st.session_state.transacciones_cerradas:
        st.info("Sin transacciones cerradas.")
    else:
        for t in st.session_state.transacciones_cerradas:
            st.markdown(f"**Transacción #{t['id_transaccion']}** | {t['productor']} ➔ {t['tienda']} (${t['precio']:.2f} USD)")
            if st.button(f"📥 Descargar PDF #{t['id_transaccion']}", key=f"pdf_gen_{t['id_transaccion']}"):
                class PDF(FPDF):
                    def header(self):
                        self.set_font("Arial", "B", 14)
                        self.cell(0, 10, EMPRESA_NOMBRE, 0, 1, "C")
                        self.set_font("Arial", "", 10)
                        self.cell(0, 5, f"RIF: {EMPRESA_RIF}", 0, 1, "C")
                        self.ln(5)

                pdf = PDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "NOTA DE ENTREGA Y CERTIFICADO", 0, 1, "C")
                pdf.ln(5)
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 8, f"Transaccion ID: {t['id_transaccion']}", 0, 1)
                pdf.cell(0, 8, f"Zona: {t['zona']}", 0, 1)
                pdf.cell(0, 8, f"Productor: {t['productor']}", 0, 1)
                pdf.cell(0, 8, f"Agrotienda: {t['tienda']}", 0, 1)
                pdf.cell(0, 8, f"Insumo: {t['insumo']} ({t['cantidad']}) - ${t['precio']:.2f} USD", 0, 1)
                
                filename = f"Nota_Entrega_{t['id_transaccion']}.pdf"
                pdf.output(filename)
                
                with open(filename, "rb") as f_pdf:
                    st.download_button(label="⬇️ Descargar PDF", data=f_pdf, file_name=filename, mime="application/pdf")
            st.divider()
