import unittest
import numpy as np
from util import *

class TestComputeOppositeAngleRange(unittest.TestCase):
    def test_horizontal_line_point_above(self):
        point_out = np.array([0, 1])
        point_in = np.array([0, 0])
        vertex1 = np.array([0, 0])
        vertex2 = np.array([1, 0])

        angle_range = compute_opposite_angle_range(
            point_out, point_in, vertex1, vertex2
        )
        self.assertAlmostEqual(np.degrees(angle_range[0]), 90, places=5)
        self.assertAlmostEqual(np.degrees(angle_range[1]), 270, places=5)

    def test_horizontal_line_point_below(self):
        point_out = np.array([0, -1])
        point_in = np.array([0, 0])
        vertex1 = np.array([0, 0])
        vertex2 = np.array([1, 0])

        angle_range = compute_opposite_angle_range(
            point_out, point_in, vertex1, vertex2
        )
        self.assertAlmostEqual(np.degrees(angle_range[0]), 270, places=5)
        self.assertAlmostEqual(np.degrees(angle_range[1]), 90, places=5)

    def test_diagonal_line_point_above(self):
        point_out = np.array([1, 2])
        point_in = np.array([0, 0])
        vertex1 = np.array([0, 0])
        vertex2 = np.array([1, 1])

        angle_range = compute_opposite_angle_range(
            point_out, point_in, vertex1, vertex2
        )
        self.assertAlmostEqual(np.degrees(angle_range[0]), 135, places=2)
        self.assertAlmostEqual(np.degrees(angle_range[1]), 315, places=2)

    def test_vertical_line_point_right(self):
        point_out = np.array([1, 0])
        point_in = np.array([0, 0])
        vertex1 = np.array([0, 0])
        vertex2 = np.array([0, 1])

        angle_range = compute_opposite_angle_range(
            point_out, point_in, vertex1, vertex2
        )
        self.assertAlmostEqual(np.degrees(angle_range[0]), 0, places=5)
        self.assertAlmostEqual(np.degrees(angle_range[1]), 180, places=5)

    def test_vertical_line_point_left(self):
        point_out = np.array([-1, 0])
        point_in = np.array([0, 0])
        vertex1 = np.array([0, 0])
        vertex2 = np.array([0, 1])

        angle_range = compute_opposite_angle_range(
            point_out, point_in, vertex1, vertex2
        )
        self.assertAlmostEqual(np.degrees(angle_range[0]), 180, places=5)
        self.assertAlmostEqual(np.degrees(angle_range[1]), 0, places=5)


if __name__ == "__main__":
    unittest.main()
