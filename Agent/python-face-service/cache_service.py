"""
Cache service for managing employee data cache.
"""
import logging
import json
import time
import signal
from contextlib import contextmanager
import numpy as np
from typing import List, Dict, Tuple
from config import ServiceConfig
from cache import ThreadSafeCache
from api_client import fetch_employees_from_api

logger = logging.getLogger(__name__)

@contextmanager
def timeout_context(seconds):
    """Context manager for timeout (Windows-compatible)."""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    # On Windows, signal.SIGALRM is not available, so we use a simpler approach
    # For Windows compatibility, we rely on requests timeout instead
    try:
        yield
    except Exception as e:
        raise


def refresh_employee_cache(cache: ThreadSafeCache) -> bool:
    """
    Refresh cached employee data from backend and precompute embeddings matrix.
    Includes maximum timeout protection to prevent hanging.
    
    Args:
        cache: ThreadSafeCache instance to update
        
    Returns:
        True if successful, False otherwise
    """
    max_total_time = 15  # Maximum total time for cache refresh (seconds)
    start_time = time.time()
    
    try:
        logger.info("Starting cache refresh...")
        employees = fetch_employees_from_api()
        
        elapsed = time.time() - start_time
        if elapsed > max_total_time:
            logger.error(f"Cache refresh took too long ({elapsed:.1f}s) - aborting")
            return False
        
        if employees is None:
            logger.warning("Failed to fetch employees from API")
            return False
        
        parse_start = time.time()
        embeddings_list, employee_info_list = parse_employee_embeddings(employees)
        parse_time = (time.time() - parse_start) * 1000
        
        if embeddings_list:
            embeddings_matrix = np.array(embeddings_list)
            cache.update(employees, embeddings_matrix, employee_info_list)
            total_time = (time.time() - start_time) * 1000
            logger.info(
                f"Cache updated in {total_time:.0f}ms (parse: {parse_time:.0f}ms): "
                f"{len(employees)} employees, {len(embeddings_list)} with embeddings"
            )
        else:
            cache.update(employees, None, [])
            total_time = (time.time() - start_time) * 1000
            logger.info(
                f"Cache updated in {total_time:.0f}ms: "
                f"{len(employees)} employees, 0 with embeddings"
            )
        
        return True
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Cache refresh failed after {elapsed:.1f}s: {e}", exc_info=True)
        return False


def parse_employee_embeddings(employees: List[Dict]) -> Tuple[List[np.ndarray], List[Dict]]:
    """
    Parse and validate employee embeddings from API response.
    
    Args:
        employees: List of employee dicts from API
        
    Returns:
        Tuple of (embeddings_list, valid_employee_info_list)
    """
    embeddings_list = []
    employee_info_list = []
    
    for employee in employees:
        if not employee.get('face_embedding'):
            continue
        
        try:
            stored_embedding = json.loads(employee['face_embedding'])
            
            if len(stored_embedding) != ServiceConfig.EXPECTED_EMBEDDING_DIM:
                logger.warning(
                    f"Skipping employee {employee.get('id')} - "
                    f"Invalid embedding dimension: {len(stored_embedding)} "
                    f"(expected {ServiceConfig.EXPECTED_EMBEDDING_DIM})"
                )
                continue
            
            embeddings_list.append(stored_embedding)
            employee_info_list.append(employee)
        except Exception as e:
            logger.warning(f"Skipping employee {employee.get('id')} - Invalid embedding: {e}")
            continue
    
    return embeddings_list, employee_info_list


def refresh_employee_cache(cache: ThreadSafeCache) -> bool:
    """
    Refresh cached employee data from backend and precompute embeddings matrix.
    
    Args:
        cache: ThreadSafeCache instance to update
        
    Returns:
        True if successful, False otherwise
    """
    employees = fetch_employees_from_api()
    if employees is None:
        return False
    
    start_time = time.time()
    embeddings_list, employee_info_list = parse_employee_embeddings(employees)
    
    if embeddings_list:
        embeddings_matrix = np.array(embeddings_list)
        cache.update(employees, embeddings_matrix, employee_info_list)
        total_time = (time.time() - start_time) * 1000
        logger.info(
            f"Cache updated in {total_time:.0f}ms: "
            f"{len(employees)} employees, {len(embeddings_list)} with embeddings"
        )
    else:
        cache.update(employees, None, [])
        total_time = (time.time() - start_time) * 1000
        logger.info(
            f"Cache updated in {total_time:.0f}ms: "
            f"{len(employees)} employees, 0 with embeddings"
        )
    
    return True


def ensure_cache_fresh(cache: ThreadSafeCache) -> None:
    """Refresh cache if it's stale or empty."""
    if cache.is_stale():
        refresh_employee_cache(cache)
