import math

# Takes time in seconds and converts to MM:SS.CC format
def timeFormat(time):
    mins = math.floor(time / 60)
    secs = math.floor(time % 60)
    cents = int((time - math.floor(time)) * 100)
    
    formatted_time = '{:02d}'.format(mins) + ":"
    formatted_time +='{:02d}'.format(secs) + "."
    formatted_time += '{:02d}'.format(cents)

    return formatted_time