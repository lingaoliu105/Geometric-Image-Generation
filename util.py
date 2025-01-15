"""
This module includes pure computation functions used in the code base
"""

from enum import Enum
import random
from typing import List, Type
import numpy as np
import shapely

import common_types
import generation_config
import img_params


from scipy.stats import beta

def compute_angle_between_vectors(
    point_out: np.ndarray,
    point_in: np.ndarray,
    vertex1: np.ndarray,
    vertex2: np.ndarray,
) -> float:
    """
    Compute the angle between the vector from point_in to point_out and the vector from vertex1 to vertex2.

    Args:
        point_out (np.ndarray): The point whose angle is being calculated (2D coordinate).
        point_in (np.ndarray): The reference point (2D coordinate).
        vertex1 (np.ndarray): The first point defining the line (2D coordinate).
        vertex2 (np.ndarray): The second point defining the line (2D coordinate).

    Returns:
        float: The angle in radians.
    """

    # Step 1: Compute the direction vector of the line (vertex2 - vertex1)
    direction_vector = vertex2 - vertex1

    # Step 2: Compute the vector from point_in to point_out
    point_vector = point_out - point_in

    # Step 3: Compute the dot product and magnitudes of the vectors
    dot_product = np.dot(direction_vector, point_vector)
    magnitude_direction = np.linalg.norm(direction_vector)
    magnitude_point = np.linalg.norm(point_vector)

    # Step 4: Compute the cosine of the angle
    cos_theta = dot_product / (magnitude_direction * magnitude_point)

    # Step 5: Compute the angle in radians using arccos
    angle = np.arccos(cos_theta)

    return angle


def compute_opposite_angle_range(
    point_out: np.ndarray,
    point_in: np.ndarray,
    vertex1: np.ndarray,
    vertex2: np.ndarray,
):
    """
    Compute the angle range opposite to the line formed by vertex1 and vertex2, opposite to point_out.

    Args:
        point_out (np.ndarray): The point off the line (2D coordinate).
        point_in (np.ndarray): The reference point on the line (2D coordinate).
        vertex1 (np.ndarray): The first point defining the line (2D coordinate).
        vertex2 (np.ndarray): The second point defining the line (2D coordinate).

    Returns:
        tuple: A tuple representing the start and end angles (in radians) of the range opposite point_out.
    """

    # Compute the direction vector of the line (vertex2 - vertex1)
    direction_vector = vertex2 - vertex1
    direction_angle = np.arctan2(direction_vector[1], direction_vector[0])

    # Compute the vector from point_in to point_out
    point_vector = point_out - point_in
    point_angle = np.arctan2(point_vector[1], point_vector[0])

    # Calculate the angle difference between the line direction and the point_out vector
    angle_difference = np.mod(point_angle - direction_angle, 2 * np.pi)

    # Determine the opposite angle range
    opposite_start = np.mod(direction_angle + angle_difference + np.pi, 2 * np.pi)
    opposite_end = np.mod(direction_angle + angle_difference - np.pi, 2 * np.pi)

    return (opposite_start, opposite_end)


def cubic_bezier(t, P0, P1, P2, P3):
    """Calculate a point on a cubic Bezier curve."""
    return (
        (1 - t) ** 3 * P0
        + 3 * (1 - t) ** 2 * t * P1
        + 3 * (1 - t) * t**2 * P2
        + t**3 * P3
    )


def generate_bezier_curve(P0, P1, P2, P3, num_points=100,scale = 1)->np.ndarray:
    """Generate points on a cubic Bezier curve."""
    t_values = np.linspace(0, 1, num_points)
    curve = np.array([scale*cubic_bezier(t, P0, P1, P2, P3) for t in t_values])
    return curve

def generate_bezier_curve_single_param(curvature:float)->np.ndarray: 
    """generate points on a cubic Bezier curve, which curvature is controled by the single input, 
        and 2 endpoints at (-1,0) and (1,0). can be scaled up according to usage

    Args:
        curvature (float): the curvature that you expect the curve to be. the curve bends more when this number is larger
    """    
    
    return generate_bezier_curve(np.array([-1,0]),np.array([-0.5,curvature]),np.array([0.5,-curvature]),np.array([1,0]),scale=8)

def generate_circle_curve(radius:float)->np.ndarray:
    return np.array(shapely.Point(0,0).buffer(radius).exterior.coords)


def get_points_on_line(start, end, n=100):
    """
    在给定的起点和终点之间生成等间距的 n 个点。

    参数:
    start -- 起点坐标，二元数组，例如 [x1, y1]
    end -- 终点坐标，二元数组，例如 [x2, y2]
    n -- 要生成的等间距点数

    返回:
    points -- n 个等间距的点的列表
    """
    start = np.array(start)
    end = np.array(end)

    # 生成包含 n 个点的等差数列，并根据比例计算每个点的坐标
    points = np.array([((1 - t) * start + t * end).tolist() for t in np.linspace(0, 1, n)])

    return points

def get_line_rotation(pt1:common_types.Coordinate,pt2:common_types.Coordinate)->float:
    delta = pt1-pt2
    # 使用 arctan2 计算角度，并转换为度数
    angle = np.degrees(np.arctan2(delta[1], delta[0]))
    return angle


def get_random_rotation()->int:
    return random.choice(list(img_params.Angle)).value * random.randint(0, 23)
def get_point_distance(point1: np.ndarray, point2: np.ndarray) -> float:
    # Calculate the difference between the points
    diff = point1 - point2

    # Compute the Euclidean distance
    distance = np.linalg.norm(diff)

    return distance


def almost_equal(a, b, tol=1e-6):
    """
    Check if two numbers (float or int) or two NumPy arrays are approximately equal within a tolerance.

    Parameters:
    a, b : float, int, or np.ndarray
        The values or arrays to compare.
    tol : float
        The tolerance for comparison. Default is 1e-6.

    Returns:
    bool
        True if `a` and `b` are approximately equal within the specified tolerance, otherwise False.
    """
    # Convert lists or tuples to numpy arrays for uniform handling
    if isinstance(a, (list, tuple)):
        a = np.array(a)
    if isinstance(b, (list, tuple)):
        b = np.array(b)

    # Check if both inputs are numbers (int or float)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= tol

    # Check if both inputs are numpy arrays
    elif isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
        return np.allclose(a, b, atol=tol)

    else:
        raise TypeError(
            "Inputs must both be numbers (int/float) or both be NumPy arrays."
        )


def generate_random_points_around_point(center, distance):
    """
    Generate two random points such that the line between them
    is at a specified distance from a given center point.

    Parameters:
    center (tuple): The coordinates of the center point (x, y).
    distance (float): The perpendicular distance of the line from the center point.

    Returns:
    tuple: A tuple of two points, each being a tuple (x, y).
    """
    # Unpack center point
    x, y = center

    # Random angle for line orientation
    angle = np.random.uniform(0, 2 * np.pi)

    # Compute the offsets along the direction perpendicular to the desired line
    dx = distance * np.cos(angle + np.pi / 2)
    dy = distance * np.sin(angle + np.pi / 2)

    # Two points on the line at the specified distance from the center point
    point1 = (x + dx, y + dy)
    point2 = (x - dx, y - dy)

    return point1, point2


def generate_beta_random_with_mode(mode, alpha, min_val=0.0, max_val=1.0):
    """
    根据给定的众数 (mode) 和 α 参数生成 Beta 分布，并返回一个在 [min_val, max_val] 范围内的随机数。

    参数:
    mode (float): 期望的众数 (0到1之间的某数)
    alpha (float): Beta 分布的 α 参数 (大于1, 越大越尖)
    min_val (float): 随机数返回的最小值 (默认是0)
    max_val (float): 随机数返回的最大值 (默认是1)

    返回:
    float: 按指定 Beta 分布生成的随机数
    """
    if not (0 < mode < 1):
        raise ValueError("Mode must be between 0 and 1.")

    if alpha <= 1:
        raise ValueError("Alpha must be greater than 1 for a proper distribution.")

    # 根据众数和α参数反推β参数
    beta_param = (alpha - 1) * (1 - mode) / mode + 1

    # 生成标准 Beta 分布随机数
    sample = beta.rvs(alpha, beta_param)

    # 将随机数缩放到 [min_val, max_val] 范围
    scaled_sample = min_val + sample * (max_val - min_val)

    return scaled_sample


def choose_param_with_beta(mode, param_class, alpha = 2):
    assert(issubclass(param_class,Enum))
    rand_num = generate_beta_random_with_mode(mode=mode, alpha=alpha)
    param_num = len(list(param_class))
    params_float_list = [i * 1.0/param_num for i in range(param_num)]
    nearest_index = min([i for i in range(param_num)],key=lambda x: abs(params_float_list[x] - rand_num))
    return list(param_class)[nearest_index]

def get_rand_point()->np.ndarray:
    """get a random point in the range of the canvas"""
    x = random.uniform(generation_config.GenerationConfig.left_canvas_bound,generation_config.GenerationConfig.right_canvas_bound)
    y = random.uniform(generation_config.GenerationConfig.lower_canvas_bound,generation_config.GenerationConfig.upper_canvas_bound)
    return np.array([x,y])


def rotate_point(original_point,pivot_point, theta):
    
    x,y,x0,y0 = list(original_point)+list(pivot_point)

    # 将角度转换为弧度
    theta_rad = np.radians(theta)

    # 平移到旋转中心
    x_shifted = x - x0
    y_shifted = y - y0

    # 应用旋转矩阵
    x_rotated = x_shifted * np.cos(theta_rad) - y_shifted * np.sin(theta_rad)
    y_rotated = x_shifted * np.sin(theta_rad) + y_shifted * np.cos(theta_rad)

    # 平移回原位置
    x_final = x_rotated + x0
    y_final = y_rotated + y0

    return x_final, y_final

def choose_color(color_distribution:List[float])->img_params.Color:
    return choose_item_by_distribution(img_params.Color,color_distribution)

def choose_item_by_distribution(enum:Type[Enum],distribution:List[float]):
    if len(distribution) != len(list(enum)):
        raise ValueError(
            "Distribution must have correct number of probabilities."
        )
    if not abs(sum(distribution) - 1.0) < 1e-6:
        raise ValueError("Color distribution probabilities must sum to 1.")
    selected = random.choices(
        list(enum), weights=distribution, k=1
    )[0]
    return selected
