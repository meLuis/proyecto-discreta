import base64
import os
import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Simulación y Análisis de Cadenas de Márkov")

# --- Fondo personalizado ---
def set_background(image_file):
    path = os.path.join(os.path.dirname(__file__), image_file)
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

set_background("fondo.jpg")


# --- Estilos para botones con imagen ---
st.markdown("""
<style>
.boton-opcion {
    display: inline-block;
    margin: 40px;
    text-align: center;
    cursor: pointer;
    transition: transform 0.2s ease;
}
.boton-opcion img {
    width: 150px;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.boton-opcion:hover {
    transform: scale(1.05);
}
.boton-opcion p {
    margin-top: 10px;
    font-size: 1.2rem;
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --- Nombres de IA ---
nombres_ia = ["ChatGPT", "Gemini", "Claude", "Copilot", "Perplexity"]

# --- Manejo del estado ---
if "modo" not in st.session_state:
    st.session_state.modo = None

# --- Pantalla inicial con botones visuales ---
if st.session_state.modo is None:
    st.markdown("""
    <div style="text-align: center; background-color: rgba(0, 0, 0, 0.6); padding: 20px; border-radius: 15px; margin-bottom: 30px;">
        <h2 style="color: white; margin: 0;">Desarrollado por Cade Korv</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: white; margin-bottom: 30px;'>¿Qué deseas hacer?</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        c1, c2 = st.columns(2)

        with c1:
            if st.button("🌀 Simular secuencias", key="simular"):
                st.session_state.modo = "Simular secuencias"
                st.rerun()
            st.markdown("""
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stButton > button {
                background-image: url('https://img.icons8.com/clouds/200/000000/process.png');
                background-repeat: no-repeat;
                background-position: center top;
                background-size: 80px;
                padding-top: 100px;
                padding-bottom: 20px;
                font-size: 1.1rem;
                font-weight: bold;
                border-radius: 15px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
                height: 160px;
                width: 160px;
                margin: auto;
            }
            </style>
            """, unsafe_allow_html=True)

        with c2:
            if st.button("📊 Analizar secuencias", key="analizar"):
                st.session_state.modo = "Analizar secuencias"
                st.rerun()
            st.markdown("""
            <style>
            .stButton > button:nth-child(2) {
                background-image: url('https://img.icons8.com/clouds/200/000000/analytics.png');
                background-repeat: no-repeat;
                background-position: center top;
                background-size: 80px;
                padding-top: 100px;
                padding-bottom: 20px;
                font-size: 1.1rem;
                font-weight: bold;
                border-radius: 15px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
                height: 160px;
                width: 160px;
                margin: auto;
            }
            </style>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; background-color: rgba(0, 0, 0, 0.6); padding: 15px 20px; border-radius: 15px; margin-top: 40px;">
        <h3 style="color: white; margin-bottom: 10px;">Integrantes:</h3>
        <p style="color: white; font-size: 18px; line-height: 1.5; margin: 0;">
            Cabezas Díaz, Denis Alexis<br>
            Gomero Del Rio, Mauro<br>
            Espinoza Navarrete, Luis Manuel<br>
            Loyola Rodriguez, Stefano Isaac
        </p>
    </div>
    """, unsafe_allow_html=True)


# --- Simular secuencias ---
elif st.session_state.modo == "Simular secuencias":
    st.title("Simulación de Cadenas de Márkov")

    st.subheader("Usuarios por herramienta (en millones)")
    usuarios_por_ia = []
    valores_defecto = [100, 50, 30, 20, 25]
    for i, nombre in enumerate(nombres_ia):
        usuarios = st.slider(nombre, 0, 200, valores_defecto[i], 1)
        usuarios_por_ia.append(usuarios)

    usuarios_por_ia = np.array(usuarios_por_ia)
    total_usuarios = np.sum(usuarios_por_ia)

    st.subheader("Distribución inicial de usuarios")
    if total_usuarios == 0:
        vector_inicial = np.array([1/len(nombres_ia)] * len(nombres_ia))
    else:
        vector_inicial = usuarios_por_ia / total_usuarios

    st.dataframe(pd.DataFrame({
        "IA": nombres_ia,
        "Probabilidad": vector_inicial.round(4)
    }), use_container_width=True)

    st.subheader("Parámetro de permanencia")
    stay_weight = st.slider(
        "Probabilidad de que un usuario se quede en la misma IA",
        0.0, 1.0, 0.6, 0.05
    )

    # Crear matriz de transición
    P = []
    for i in range(len(vector_inicial)):
        fila = []
        for j in range(len(vector_inicial)):
            if i == j:
                fila.append(stay_weight)
            else:
                total_otros = 1 - vector_inicial[i]
                if total_otros == 0:
                    fila.append((1 - stay_weight) / (len(vector_inicial) - 1))
                else:
                    fila.append((1 - stay_weight) * (vector_inicial[j] / total_otros))
        P.append(fila)
    P = np.array(P)

    st.subheader("Parámetros de simulación")
    st.subheader("Cantidad de usuarios a simular")


    num_usuarios = st.number_input("Cantidad de usuarios a simular", min_value=1, max_value=1000, value=100, step=1)
    pasos = st.number_input("Cantidad de pasos a simular", min_value=1, max_value=100, value=5, step=1)

    if st.button("Simular secuencias"):
        secuencias = []
        for _ in range(num_usuarios):
            estado = np.random.choice(len(vector_inicial), p=vector_inicial)
            historial = [estado]
            for _ in range(pasos):
                estado = np.random.choice(len(P), p=P[estado])
                historial.append(estado)
            secuencias.append(historial)

        df_secuencias = pd.DataFrame(secuencias)
        csv = df_secuencias.to_csv(index=False, header=False)

        st.markdown("<h4 style='color: white;'>⬇️ ¡Listo! Descarga las secuencias aquí:</h4>", unsafe_allow_html=True)
        st.download_button("Descargar como CSV", csv, "secuencias_simuladas.csv", "text/csv")


    if st.button("🔙 Volver al inicio"):
        st.session_state.modo = None
        st.rerun()

# --- Analizar secuencias ---
elif st.session_state.modo == "Analizar secuencias":
    st.title("Análisis de Secuencias de Cadenas de Márkov")

    uploaded_file = st.file_uploader("Sube un archivo CSV con las secuencias", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file, header=None)
            num_estados = len(nombres_ia)
            conteo = np.zeros((num_estados, num_estados))

            for _, fila in df.iterrows():
                for i in range(len(fila) - 1):
                    origen = int(fila[i])
                    destino = int(fila[i+1])
                    conteo[origen, destino] += 1

            suma_filas = conteo.sum(axis=1, keepdims=True)
            matriz_transicion = np.divide(conteo, suma_filas, out=np.zeros_like(conteo), where=suma_filas != 0)

            primeros_estados = df.iloc[:, 0]
            conteo_inicial = primeros_estados.value_counts(normalize=True).sort_index()
            vector_inicial_real = conteo_inicial.values

            st.subheader("Vector de estado inicial observado")
            st.dataframe(pd.DataFrame({
                "IA": nombres_ia[:num_estados],
                "Probabilidad": vector_inicial_real.round(4)
            }), use_container_width=True)

            st.subheader("Matriz de transición observada")
            st.dataframe(pd.DataFrame(matriz_transicion, index=nombres_ia, columns=nombres_ia).round(4), use_container_width=True)

            pasos_pronostico = st.number_input("Número de pasos a pronosticar", 1, 100, 5)
            estado_futuro = np.matmul(np.linalg.matrix_power(matriz_transicion, pasos_pronostico), vector_inicial_real)

            st.subheader("Pronóstico de usuarios futuros")
            st.dataframe(pd.DataFrame({
                "IA": nombres_ia,
                f"Vector de probabilidad en el periodo n={pasos_pronostico}": estado_futuro.round(4)
            }), use_container_width=True)

            P_infinito = np.linalg.matrix_power(matriz_transicion, 1000)
            estado_largo_plazo = P_infinito[0]

            st.subheader("Distribución estable de largo plazo")
            st.dataframe(pd.DataFrame({
                "IA": nombres_ia,
                "Vector de probabilidad estacionario": estado_largo_plazo.round(4)
            }), use_container_width=True)

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

    if st.button("🔙 Volver al inicio"):
        st.session_state.modo = None
        st.rerun()
