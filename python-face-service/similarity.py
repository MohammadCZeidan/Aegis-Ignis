"""
Similarity calculation functions optimized with precomputed norms.
"""
from typing import Optional, List, Dict, Tuple
import numpy as np
from config import ServiceConfig


def calculate_similarity_matrix(
    embeddings_matrix: np.ndarray, 
    query_embedding: np.ndarray,
    precomputed_norms: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Calculate cosine similarity between query embedding and all cached embeddings.
    Optimized with precomputed norms for faster computation.
    
    Args:
        embeddings_matrix: Matrix of cached embeddings (N x D)
        query_embedding: Query embedding vector (D,)
        precomputed_norms: Precomputed norms of embeddings_matrix (optional, for speed)
        
    Returns:
        Array of similarity scores (N,)
    """
    if precomputed_norms is not None:
        # Use precomputed norms (much faster - avoids recalculating)
        query_norm = np.linalg.norm(query_embedding)
        norms = precomputed_norms * query_norm
    else:
        # Fallback: compute norms on the fly
        norms = np.linalg.norm(embeddings_matrix, axis=1) * np.linalg.norm(query_embedding)
    
    similarities = np.dot(embeddings_matrix, query_embedding) / norms
    return similarities


def find_best_match(
    embeddings_matrix: np.ndarray,
    employee_info: List[Dict],
    query_embedding: np.ndarray,
    threshold: float,
    precomputed_norms: Optional[np.ndarray] = None
) -> Tuple[Optional[Dict], float]:
    """
    Find best matching employee for given embedding.
    Optimized with precomputed norms for faster computation.
    
    Args:
        embeddings_matrix: Matrix of cached embeddings
        employee_info: List of employee info dicts
        query_embedding: Query embedding to match
        threshold: Minimum similarity threshold
        precomputed_norms: Precomputed norms for speed (optional)
        
    Returns:
        Tuple of (matched_employee_dict, similarity_score) or (None, score) if no match
    """
    if len(embeddings_matrix) == 0 or len(employee_info) == 0:
        return None, 0.0
    
    similarities = calculate_similarity_matrix(embeddings_matrix, query_embedding, precomputed_norms)
    max_idx = np.argmax(similarities)
    max_similarity = float(similarities[max_idx])
    
    if max_similarity >= threshold:
        return employee_info[max_idx], max_similarity
    
    return None, max_similarity
