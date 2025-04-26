import numpy as np

def generar_vector_inicial(usuarios):
    usuarios = np.array(usuarios)
    total = usuarios.sum()
    if total == 0:
        return np.array([1/len(usuarios)] * len(usuarios))
    return usuarios / total

def generar_matriz_transicion(vector_inicial, permanencia):
    n = len(vector_inicial)
    matriz = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i == j:
                matriz[i, j] = permanencia
            else:
                otros_total = 1 - vector_inicial[i]
                if otros_total == 0:
                    matriz[i, j] = (1 - permanencia) / (n - 1)
                else:
                    matriz[i, j] = (1 - permanencia) * (vector_inicial[j] / otros_total)
                    
    return matriz
