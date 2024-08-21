import numpy as np


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

