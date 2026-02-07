import screen_brightness_control as sbc

def set_brightness(level):
    """
    Sets the screen brightness to a specific level (0-100).
    """
    try:
        # Ensure level is between 0 and 100
        level = max(0, min(100, int(level)))
        sbc.set_brightness(level)
        return f"Brightness set to {level}%"
    except Exception as e:
        return f"Error setting brightness: {e}"

def get_brightness():
    """
    Gets the current screen brightness.
    """
    try:
        current = sbc.get_brightness()
        return f"Current brightness is {current}%"
    except Exception as e:
        return f"Error getting brightness: {e}"
