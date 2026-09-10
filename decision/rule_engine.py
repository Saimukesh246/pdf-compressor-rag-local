def rule_based_strategy(image_count, text_length, is_scanned=False, page_count=1):
    """
    Evaluates rule-based heuristics on PDF metrics.
    
    Returns:
        (strategy, confidence): Tuple of (str or None, float)
    """
    if is_scanned:
        return "Scanned PDF", 0.95

    avg_images = image_count / page_count if page_count > 0 else image_count

    if image_count > 15 or (avg_images >= 2 and text_length < 3000):
        return "Image-heavy PDF", 0.9

    if text_length > 8000 and image_count < 5:
        return "Text-heavy PDF", 0.9

    return None, 0.0
