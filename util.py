def clamp(x, min_val, max_val):
    return min(max_val, max(min_val, x))

def number_map_u24(in_min: float, in_max: float, out_min: float, out_max: float, x: float) -> float:
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
