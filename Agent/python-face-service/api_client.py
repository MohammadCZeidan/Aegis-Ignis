
import logging
import requests
import time
from typing import Optional, List, Dict
from config import ServiceConfig

logger = logging.getLogger(__name__)

def fetch_employees_from_api() -> Optional[List[Dict]]:
    """
    Fetch employees from Laravel API with retry logic.
    
    Returns:
        List of employee dicts or None if failed
    """
    for attempt in range(1, ServiceConfig.MAX_RETRIES + 1):
        try:
            start_time = time.time()
            logger.info(f"Fetching employees from API (attempt {attempt}/{ServiceConfig.MAX_RETRIES}, timeout={ServiceConfig.REQUEST_TIMEOUT}s)")
            
            response = requests.get(
                f"{ServiceConfig.LARAVEL_API_URL}/api/v1/employees/registered-faces",
                timeout=ServiceConfig.REQUEST_TIMEOUT,
                headers={
                    "Accept": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                }
            )
            
            fetch_time = (time.time() - start_time) * 1000
            logger.info(f"API response received in {fetch_time:.0f}ms (status: {response.status_code})")
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                logger.info(f"Fetched {len(data)} employees from API")
                return data
            else:
                logger.error(f"API returned status {response.status_code}: {response.text[:200]}")
                if attempt < ServiceConfig.MAX_RETRIES:
                    logger.warning(f"Retrying in {ServiceConfig.RETRY_DELAY} seconds...")
                    time.sleep(ServiceConfig.RETRY_DELAY)
                    continue
                return None
                
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            logger.error(f"API request timeout after {elapsed:.1f}s (>{ServiceConfig.REQUEST_TIMEOUT}s)")
            if attempt < ServiceConfig.MAX_RETRIES:
                logger.warning(f"Retrying in {ServiceConfig.RETRY_DELAY} seconds...")
                time.sleep(ServiceConfig.RETRY_DELAY)
                continue
            return None
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to API at {ServiceConfig.LARAVEL_API_URL}: {e}")
            if attempt < ServiceConfig.MAX_RETRIES:
                logger.warning(f"Retrying in {ServiceConfig.RETRY_DELAY} seconds...")
                time.sleep(ServiceConfig.RETRY_DELAY)
                continue
            return None
            
        except Exception as e:
            logger.error(f"Error fetching employees: {e}", exc_info=True)
            if attempt < ServiceConfig.MAX_RETRIES:
                logger.warning(f"Retrying in {ServiceConfig.RETRY_DELAY} seconds...")
                time.sleep(ServiceConfig.RETRY_DELAY)
                continue
            return None
    
    logger.error(f"Failed to fetch employees after {ServiceConfig.MAX_RETRIES} attempts")
    return None
