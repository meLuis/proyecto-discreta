import numpy as np

def simular_secuencias(vector_inicial, matriz_transicion, pasos, cantidad_usuarios):
    secuencias = []
    
    for _ in range(cantidad_usuarios):
        estado = np.random.choice(len(vector_inicial), p=vector_inicial)
        historial = [estado]
        
        for _ in range(pasos):
            estado = np.random.choice(len(vector_inicial), p=matriz_transicion[estado])
            historial.append(estado)
        
        secuencias.append(historial)
    
    return secuencias
