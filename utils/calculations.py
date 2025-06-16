# utils/calculations.py

def calculate_lod(agr):
    if agr is None or agr == 0:
        return "N/A"
    if agr > 1000:
        return "LoD 2.0"
    elif 500 <= agr <= 1000:
        return "LoD 2.1 - 2.3"
    elif 250 <= agr < 500:
        return "LoD 3.0 - 3.3"
    else:
        return "LoD 3.3 - LoD 4"

def calculate_gsd(sensor_size, focal_length, flight_height, image_width):
    try:
        return ((sensor_size / image_width) * (flight_height * 1000 / focal_length))
    except ZeroDivisionError:
        return 0.0

def model_resolution_control(gsd, agr):
    if agr == 0:
        return 0.0
    return gsd / agr
