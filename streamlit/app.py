import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Simulación y Análisis de Cadenas de Márkov")

modo = st.selectbox("Selecciona el modo", ["Simular secuencias", "Analizar secuencias"])

nombres_ia = ["ChatGPT", "Gemini", "Claude", "Copilot", "Perplexity"]

if modo == "Simular secuencias":
    st.title("Simulación de Cadenas de Márkov")

    st.subheader("Usuarios por herramienta (en millones)")

    usuarios_por_ia = []
    valores_defecto = [100, 50, 30, 20, 25]
    for i, nombre in enumerate(nombres_ia):
        usuarios = st.number_input(
            f"{nombre}",
            min_value=0,
            value=valores_defecto[i],
            step=1
        )
        usuarios_por_ia.append(usuarios)

    usuarios_por_ia = np.array(usuarios_por_ia)
    total_usuarios = np.sum(usuarios_por_ia)

    st.subheader("Distribución inicial de usuarios")
    if total_usuarios == 0:
        vector_inicial = np.array([1/len(nombres_ia)] * len(nombres_ia))
    else:
        vector_inicial = usuarios_por_ia / total_usuarios

    df_vector = pd.DataFrame({
        "IA": nombres_ia,
        "Probabilidad": vector_inicial.round(4)
    })
    st.dataframe(df_vector, use_container_width=True)

    st.subheader("Parámetro de permanencia")
    stay_weight = st.slider(
        "Probabilidad de que un usuario se quede en la misma IA",
        min_value=0.0,
        max_value=1.0,
        value=0.6,
        step=0.05
    )

    # 🔵 CAMBIO AQUÍ: se sigue generando la matriz, pero NO se muestra
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
    num_usuarios = st.number_input("Número de usuarios a simular", min_value=1, value=5)
    pasos = st.number_input("Número de pasos por usuario", min_value=1, value=5)

    if st.button("Simular secuencias"):
        secuencias = []
        for _ in range(num_usuarios):
            estado = np.random.choice(len(vector_inicial), p=vector_inicial)
            historial = [estado]
            for _ in range(pasos):
                estado = np.random.choice(len(P), p=P[estado])
                historial.append(estado)
            secuencias.append(historial)

        st.subheader("Secuencias simuladas")
        for idx, secuencia in enumerate(secuencias, start=1):
            nombres = [nombres_ia[i] for i in secuencia]
            st.write(f"Usuario {idx}: {' → '.join(nombres)}")

        df_secuencias = pd.DataFrame(secuencias)
        
        csv = df_secuencias.to_csv(index=False, header=False)

        st.download_button(
            "Descargar como CSV",
            csv,
            file_name="secuencias_simuladas.csv",
            mime="text/csv"
        )

elif modo == "Analizar secuencias":
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
            matriz_transicion_real = np.divide(
                conteo, suma_filas, 
                out=np.zeros_like(conteo),
                where=suma_filas != 0
            )

            # 🔵 CAMBIO AQUÍ: ahora mostramos la matriz en el análisis
            st.subheader("Matriz de transición observada")
            df_real = pd.DataFrame(matriz_transicion_real, index=nombres_ia[:num_estados], columns=nombres_ia[:num_estados]).round(4)
            st.dataframe(df_real, use_container_width=True)

            st.subheader("Vector de estado inicial observado")
            primeros_estados = df.iloc[:, 0]
            conteo_inicial = primeros_estados.value_counts(normalize=True).sort_index()
            vector_inicial_real = conteo_inicial.values

            df_inicial_real = pd.DataFrame({
                "IA": nombres_ia[:num_estados],
                "Probabilidad": vector_inicial_real.round(4)
            })
            st.dataframe(df_inicial_real, use_container_width=True)


            pasos_pronostico = st.number_input("Número de pasos a pronosticar", min_value=1, value=5)
            estado_futuro = np.matmul(np.linalg.matrix_power(matriz_transicion_real, pasos_pronostico), vector_inicial_real)

            st.subheader("Pronóstico de usuarios futuros")
            df_estado_futuro = pd.DataFrame({
                "IA": nombres_ia[:num_estados],
                f"Probabilidad a {pasos_pronostico} pasos": estado_futuro.round(4)
            })
            st.dataframe(df_estado_futuro, use_container_width=True)

            P_infinito = np.linalg.matrix_power(matriz_transicion_real, 1000)
            estado_largo_plazo = P_infinito[0]

            st.subheader("Distribución estable de largo plazo")
            df_largo_plazo = pd.DataFrame({
                "IA": nombres_ia[:num_estados],
                "Probabilidad estable": estado_largo_plazo.round(4)
            })
            st.dataframe(df_largo_plazo, use_container_width=True)

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
