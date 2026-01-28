"""
Image processing utilities.
"""
from typing import Tuple, List, Dict
import numpy as np
from PIL import Image
from io import BytesIO
from config import ServiceConfig

def image_to_numpy(file_bytes: bytes, max_size: int = None) -> np.ndarray:
    """
    Convert image bytes to numpy array.
    
    Args:
        file_bytes: Image file bytes
        max_size: Maximum dimension (defaults to ServiceConfig.IMAGE_MAX_SIZE)
        
    Returns:
        Numpy array of image in RGB format
    """
    if max_size is None:
        max_size = ServiceConfig.IMAGE_MAX_SIZE
        
    image = Image.open(BytesIO(file_bytes))
    
    if image.width > max_size or image.height > max_size:
        image.thumbnail((max_size, max_size), Image.BILINEAR)
    
    image = image.convert('RGB')
    return np.array(image)


def calculate_scale_factors(original_size: Tuple[int, int], resized_size: Tuple[int, int]) -> Tuple[float, float]:
    """Calculate scale factors for coordinate conversion."""
    scale_x = original_size[0] / resized_size[0]
    scale_y = original_size[1] / resized_size[1]
    return scale_x, scale_y


def scale_bbox(bbox: np.ndarray, scale_x: float, scale_y: float) -> List[int]:
    """Scale bounding box coordinates from resized to original image size."""
    return [
        int(bbox[0] * scale_x),
        int(bbox[1] * scale_y),
        int(bbox[2] * scale_x),
        int(bbox[3] * scale_y)
    ]


def calculate_head_guide_box(face_bbox: np.ndarray, image_size: Tuple[int, int]) -> Dict[str, int]:
    """
    Calculate head guide box from face bounding box.
    
    Args:
        face_bbox: Face bounding box [x1, y1, x2, y2]
        image_size: (width, height) of resized image
        
    Returns:
        Dict with x, y, width, height of head guide box
    """
    x1, y1, x2, y2 = face_bbox.astype(int)
    face_width = x2 - x1
    face_height = y2 - y1
    resized_width, resized_height = image_size
    
    head_top = max(0, int(y1 - face_height * 0.5))
    head_left = max(0, int(x1 - face_width * 0.25))
    head_right = min(resized_width, int(x2 + face_width * 0.25))
    head_bottom = min(resized_height, int(y2 + face_height * 0.15))
    
    return {
        'x': head_left,
        'y': head_top,
        'width': head_right - head_left,
        'height': head_bottom - head_top
    }
