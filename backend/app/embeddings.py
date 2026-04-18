"""
Sistema de embeddings semánticos para matching inteligente de candidatos.

Utiliza Sentence Transformers para convertir texto en vectores de embeddings
y calcular similitud semántica entre consultas y perfiles de candidatos.
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Modelo de embeddings liviano pero efectivo para español e inglés
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    """
    Convierte texto en un vector de embeddings.

    Args:
        text (str): Texto a convertir en embedding

    Returns:
        numpy.ndarray: Vector de embeddings de 384 dimensiones
    """
    return model.encode(text)

def similarity(vec1, vec2):
    """
    Calcula la similitud coseno entre dos vectores de embeddings.

    Args:
        vec1 (numpy.ndarray): Primer vector de embeddings
        vec2 (numpy.ndarray): Segundo vector de embeddings

    Returns:
        float: Similitud coseno entre 0 y 1 (1 = idéntico, 0 = diferente)
    """
    return cosine_similarity([vec1], [vec2])[0][0]