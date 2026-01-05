def rule_based_strategy(image_count, text_length):
    """
    Returns (strategy, confidence)
    """
    if image_count > 15 and text_length < 2000:
        return "Image-heavy PDF", 0.9

    if text_length > 8000 and image_count < 5:
        return "Text-heavy PDF", 0.9

    return None, 0.0
