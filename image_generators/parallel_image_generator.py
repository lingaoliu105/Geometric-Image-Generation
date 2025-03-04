import random
import math
from typing import List, Tuple
import numpy as np
from shapely.geometry import LineString, Polygon

from entities.line_segment import LineSegment
from generation_config import GenerationConfig
from image_generators.image_generator import ImageGenerator
from shape_group import ShapeGroup


class ParallelImageGenerator(ImageGenerator):
    def __init__(self):
        super().__init__()

        # Define the range of the number of sub-element groups generated at different angles
        self.alignments = {
            15: [2, 4],
            45: [5, 8],
        }
        # Define the region as a rectangle: [ (min_x, min_y), (max_x, max_y) ]
        self.region = (
            (GenerationConfig.left_canvas_bound, GenerationConfig.lower_canvas_bound),
            (GenerationConfig.right_canvas_bound, GenerationConfig.upper_canvas_bound),
        )
        # Dictionary to store alignment modes and their probabilities
        self.alignment_probabilities = {
            "left": 1.0,
            "leftish": 0.0,
            "center": 0.0,
            "rightish": 0.0,
            "right": 0.0,
        }
        # Flag to control the visibility of the main axis
        self.show_main_axis = True

        # Scale factor for sub-elements
        self.sub_element_scale_range = (0.2, 0.4)

    def generate(self):

        for rotation in self.alignments:
            num_groups = random.randint(
                self.alignments[rotation][0], self.alignments[rotation][1]
            )

            # Generate the main axis if it is set to be shown
            main_axis = None
            if self.show_main_axis:
                main_axis = self.generate_main_axis(rotation)
                if main_axis:
                    # Create a ShapeGroup for the main axis
                    main_axis_group = ShapeGroup([main_axis])
                    self.shapes.add_shape(main_axis)

            # Generate the sub-element groups perpendicular to the main axis
            if main_axis:
                self.generate_perpendicular_groups(rotation, num_groups, main_axis)
            else:
                self.generate_random_groups(rotation, num_groups)

        return self.shapes

    def generate_main_axis(self, angle: float) -> LineSegment:
        """
        Generate the main axis for a given angle.
        """
        min_x, min_y = self.region[0]
        max_x, max_y = self.region[1]
        angle_rad = math.radians(angle)
        direction = np.array([math.cos(angle_rad), math.sin(angle_rad)])
        center = np.array([(min_x + max_x) / 2, (min_y + max_y) / 2])
        region_diag = math.sqrt((max_x - min_x) ** 2 + (max_y - min_y) ** 2)
        start = center - (region_diag / 2) * direction
        end = center + (region_diag / 2) * direction
        start, end = self.clip_line_to_region(start, end)
        if start is not None and end is not None:
            return LineSegment(start, end)
        return None


    def generate_perpendicular_groups(
        self, angle: float, num_groups: int, main_axis: LineSegment
    ):
        """
        Generate sub-element groups perpendicular to the main axis.
        All sub-elements will be parallel to each other and equally spaced along the main axis.
        The alignment mode (left, right, center, etc.) determines how they're positioned relative to the main axis.
        """
        min_x, min_y = self.region[0]
        max_x, max_y = self.region[1]

        # Calculate main axis properties
        main_start = main_axis.endpt_left
        main_end = main_axis.endpt_right
        main_vector = main_end - main_start

        # Choose alignment mode
        alignment_mode = random.choices(
            list(self.alignment_probabilities.keys()),
            weights=list(self.alignment_probabilities.values()),
            k=1,
        )[0]

        for i in range(num_groups):
            # Calculate position along main axis
            t = (i + 1) / (num_groups + 1)
            axis_pos = main_start + t * main_vector

            # Generate and transform sub-group
            sub_group = self.choose_sub_generator().generate()
            
            # Apply transformations
            scale = random.uniform(*self.sub_element_scale_range)
            sub_group.scale(scale)
            perp_angle = angle + 90
            sub_group.rotate(perp_angle)

            # Calculate local coordinate system
            perp_rad = math.radians(perp_angle)
            local_x_dir = np.array([math.cos(perp_rad), math.sin(perp_rad)])
            current_center = sub_group.center.copy()

            # Collect all geometry points with robust handling
            all_points = []
            for shape in sub_group.flattened():
                try:
                    geom = getattr(shape, 'base_geometry', None)
                    
                    # Handle different geometry types
                    if geom is not None:
                        if geom.geom_type == 'Point':
                            all_points.append(geom.coords[0])
                        elif geom.geom_type in ['LineString', 'LinearRing']:
                            all_points.extend(geom.coords)
                        elif geom.geom_type == 'Polygon':
                            all_points.extend(geom.exterior.coords)
                            all_points.extend([interior.coords for interior in geom.interiors])
                        elif geom.geom_type.startswith('Multi'):
                            for sub_geom in geom.geoms:
                                if sub_geom.geom_type == 'Polygon':
                                    all_points.extend(sub_geom.exterior.coords)
                                    all_points.extend([interior.coords for interior in sub_geom.interiors])
                                else:
                                    all_points.extend(sub_geom.coords)
                    elif hasattr(shape, 'vertices'):
                        all_points.extend(shape.vertices)
                except Exception as e:
                    print(f"Error processing shape: {e}")
                    continue

            # Handle empty points case
            if not all_points:
                print("Warning: Empty geometry group, skipping alignment")
                self.shapes.add_group(sub_group)
                continue

            # Calculate projections
            projections = [np.dot(p, local_x_dir) for p in all_points]
            min_proj = min(projections)
            max_proj = max(projections)
            center_proj = np.dot(current_center, local_x_dir)

            # Calculate edge offset based on alignment
            if alignment_mode == "left":
                offset = local_x_dir * (max_proj - center_proj)
            elif alignment_mode == "right":
                offset = local_x_dir * (min_proj - center_proj)
            else:
                offset = {
                    "leftish": local_x_dir * (max_proj - center_proj - (max_proj - min_proj)/4),
                    "center": np.zeros(2),
                    "rightish": local_x_dir * (min_proj - center_proj + (max_proj - min_proj)/4)
                }[alignment_mode]

            # Apply final transformation
            final_center = axis_pos + offset
            sub_group.shift(final_center - current_center)
            self.shapes.add_group(sub_group)
    def generate_random_groups(self, angle: float, num_groups: int):
        """
        Generate random sub-element groups when no main axis is provided.
        """
        min_x, min_y = self.region[0]
        max_x, max_y = self.region[1]

        for i in range(num_groups):
            # Generate random position within the region
            position = np.array(
                [random.uniform(min_x, max_x), random.uniform(min_y, max_y)]
            )

            # Generate a sub-element group using a sub-generator
            sub_generator = self.choose_sub_generator()
            sub_group = sub_generator.generate()

            # Transform the sub-group
            sub_group.shift(position)

            # Scale the sub-group
            scale_factor = random.uniform(
                self.sub_element_scale_range[0], self.sub_element_scale_range[1]
            )
            sub_group.scale(scale_factor)

            # Rotate the sub-group
            sub_group.rotate(angle + 90)  # Perpendicular to the specified angle

            # Add the sub-group to the shapes collection
            self.shapes.add_group(sub_group)

    def clip_line_to_region(
        self, start: np.ndarray, end: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Clip the line segment to the defined region.
        """
        min_x, min_y = self.region[0]
        max_x, max_y = self.region[1]

        # Construct the polygon of the entire region
        region_polygon = Polygon(
            [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
        )

        # Construct the line segment to be clipped
        line = LineString([start, end])
        clipped_line = line.intersection(region_polygon)

        if clipped_line.is_empty:
            return None, None

        if isinstance(clipped_line, LineString):
            coords = list(clipped_line.coords)
            return np.array(coords[0]), np.array(coords[-1])

        if clipped_line.geom_type == "MultiLineString":
            # If the returned object is a MultiLineString, select the longest segment
            longest = max(clipped_line, key=lambda seg: seg.length)
            coords = list(longest.coords)
            return np.array(coords[0]), np.array(coords[-1])

        return None, None
