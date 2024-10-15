from enum import Enum
import random
import numpy as np

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

def get_random_rotation()->int:
    return random.choice(list(img_params.Rotation)).value * random.randint(0, 23)
def get_point_distance(point1: np.ndarray, point2: np.ndarray) -> float:
    # Calculate the difference between the points
    diff = point1 - point2

    # Compute the Euclidean distance
    distance = np.linalg.norm(diff)

    return distance


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