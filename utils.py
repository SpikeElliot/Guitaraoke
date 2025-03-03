import math


def time_format(time: float) -> str:
    """Takes time in seconds and returns a time string converted to MM:SS.CC format."""
    mins = math.floor(time / 60)
    secs = math.floor(time % 60)
    cents = int((time - math.floor(time)) * 100)
    
    formatted_time = '{:02d}'.format(mins) + ":"
    formatted_time +='{:02d}'.format(secs) + "."
    formatted_time += '{:02d}'.format(cents)

    return formatted_time

def hex_to_rgb(hex_string: str) -> tuple:
    """Takes a hex triplet and converts it to RGB values."""
    return tuple(int(hex_string.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))