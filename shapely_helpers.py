from shapely.geometry import LineString,Polygon,Point
from shapely.ops import nearest_points
from shapely.geometry.base import BaseGeometry

from SimpleShape import SimpleShape
def find_touching_point(shape1:SimpleShape, shape2:SimpleShape, buffer_distance=0.001)-> Point:
    # Create buffers around the shapes
    buffer1 = shape1.base_geometry.buffer(buffer_distance)
    buffer2 = shape2.base_geometry.buffer(buffer_distance)

    # Find the intersection of the buffers
    intersection = buffer1.intersection(buffer2)

    if not intersection.is_empty:
        # If there's an intersection, return its centroid
        return intersection.centroid
    else:
        # If there's no intersection, find the nearest points between the original shapes
        point1, point2 = nearest_points(shape1.base_geometry, shape2.base_geometry)
        # Return the midpoint between the nearest points
        return LineString([point1, point2]).centroid


def find_edge_with_point(polygon, point, tolerance=1e-1):

    # Get the coordinates of the polygon
    coords = list(polygon.exterior.coords)

    # Iterate through the edges
    for i in range(
        len(coords) - 1
    ):  # -1 because the last point is the same as the first
        edge = LineString([coords[i], coords[i + 1]])

        # Check if the point is on this edge
        if edge.distance(point) < tolerance:
            return edge

    # If we get here, we didn't find the edge (shouldn't happen if the point is truly on the boundary)
    raise ValueError("did not find edge containing the point")
