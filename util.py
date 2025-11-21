from dataclasses import dataclass
import math
def clamp(x, min_val, max_val):
    return min(max_val, max(min_val, x))

def number_map_u24(in_min: float, in_max: float, out_min: float, out_max: float, x: float) -> float:
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def num_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def get_dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
def point_dist(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)
def point_avg(p1, p2):
    return Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2, (p1.z + p2.z) / 2)
def sign(x):
    return -1 if x < 0 else 1
def abs_clamp(x, min, max):
    if(abs(x) > max):
        return max * sign(x)
    elif abs(x) < min:
        return min * sign(x)
    else:
        return x
def abs_deadzone(x, min):
    if(abs(x) < min):
        return 0
    else:
        return x
def extend(start, end, distance):
    cur_dist = get_dist(start, end)
    xcomp = (end[0] - start[0]) / cur_dist
    ycomp = (end[1] - start[1]) / cur_dist
    return [start[0] + xcomp * distance, start[1] + ycomp * distance]


def get_ang(start, end):
    return math.atan2(end[1] - start[1], end[0] - start[0])
def collinearity_measure(p1, p2, p3):
    """0 = perfect colinearity"""
    x1, y1 = p1.x, p1.y
    x2, y2 = p2.x, p2.y
    x3, y3 = p3.x, p3.y

    deviation = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)

    return abs(deviation)

def calculate_line_angle(A, B, C):
    """
    Calculates the angle between lines AB and BC. Between -180, 180. Counterclockwise
    """
    # Calculate angles relative to the x-axis
    angle_BA = math.degrees(math.atan2(A.y - B.y, A.x - B.x))
    angle_BC = math.degrees(math.atan2(C.y - B.y, C.x - B.x))
    if angle_BA < 0:
        angle_BA += 360
    if angle_BC < 0:
        angle_BC += 360
    return angle_BA - angle_BC

def ang_diff(a1, a2):
    diff = a1 - a2
    return ((diff + 180.0) % 360.0) - 180.0
@dataclass
class Point:
    x: float
    y: float
    z: float