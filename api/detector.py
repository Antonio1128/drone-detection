import random

def run_inference(image_bytes: bytes) -> tuple[bool, float]:
    """
    Replace this function body with the real ML model.
    Returns (is_drone, confidence).
    """
    confidence = round(random.uniform(0.0, 1.0), 4)
    is_drone = confidence >= 0.5
    return is_drone, confidence
