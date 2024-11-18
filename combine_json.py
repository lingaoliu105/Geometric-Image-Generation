from enum import Enum
import json
import sys
from PIL import Image
from matplotlib.pyplot import xkcd

from entities.simple_shape import SimpleShape
import img_params
from common_types import *

get_image_id = (x for x in range(1000000)).__next__
get_annotation_id = (x for x in range(100000)).__next__
width = 0
height = 0


def find_category_id_by_name(name: str, categories):
    # use non-case-sensitive comparison
    name = name.replace("_", "")
    catid = next(
        (x["id"] for x in categories if x["name"].lower() == name.lower()),
        None,
    )
    if catid == None:
        catid = next(
            (
                x["id"]
                for x in categories
                if x["name"].lower().startswith(name.lower())
                or name.lower().startswith(x["name"].lower())
            ),
            None,
        )
    if catid == None:
        raise
    return catid


def transform_coordinate(coordinate:Coordinate):
    """transform the coordinate on the latex canvas to coordinate on the png image (by pixels)"""
    global width, height
    return [
        coordinate[0] / 20 * width + width / 2,
        height / 2 - coordinate[1] / 20 * height,
    ]


def calc_bbox(segmentation):
    assert len(segmentation) > 0 and len(segmentation) % 2 == 0
    segmentation_x_coords = [segmentation[x] for x in range(0, len(segmentation), 2)]
    segmentation_y_coords = [segmentation[x] for x in range(1, len(segmentation), 2)]
    return [
        min(segmentation_x_coords),
        min(segmentation_y_coords),
        max(segmentation_x_coords) - min(segmentation_x_coords),
        max(segmentation_y_coords) - min(segmentation_y_coords),
    ]


def calc_relative_category(
    upper_bound: float, lower_bound: float, actual: float, category: type
):
    assert issubclass(category, Enum)
    enum_list = list(category)
    if issubclass(
        category, img_params.VerticalPosition
    ):  # vertical position is ranked from high to low so need to reverse
        enum_list.reverse()
    num_cats = len(enum_list)
    nums = [x / (num_cats + 1) for x in range(1, num_cats + 1)]

    item = enum_list[
        nums.index(
            min(
                nums,
                key=lambda x: abs(
                    (actual - lower_bound) / (upper_bound - lower_bound) - x
                ),
            )
        )
    ]
    # if issubclass(category, img_params.HorizontalPosition):
    #     print((actual - lower_bound) / (upper_bound - lower_bound), ",", item)
    return item


def format_shape_annotations(
    shape, panel_top_left, panel_bottom_right
):  # multiple annotations for 1 shape, each annotation for each attribute (category)
    annotations = []

    # form boundary coordinates and segmentation and bounding box
    vertices = transform_coordinate(shape["position"]) + [2]
    segmentation = []
    coordinates = (
        shape["base_geometry"]["coordinates"][0]
        if shape["base_geometry"]["type"] != "LineString"
        else shape["base_geometry"]["coordinates"]
    )
    polygon_shapes = [
        "triangle",
        "square",
        "rectangle",
        "pentagon",
        "hexagon",
        "heptagon",
        "octagon",
        "nonagon",
        "decagon",
    ]
    for coordinate in coordinates[:-1]:
        transformed_coord = transform_coordinate(coordinate)
        if "shape" in shape and shape["shape"] in polygon_shapes:
            vertices += transformed_coord
            vertices.append(2)
        segmentation += transformed_coord
    bbox = calc_bbox(segmentation)

    # find category id of the shape
    if "shape" in shape:
        category_id = find_category_id_by_name(shape["shape"], categories=categories)
    else:
        category_id=1000
    shape_annotation = {
        "id": get_annotation_id(),
        "image_id": image_id,
        "category_id": category_id,
        "bbox": bbox,
        "segmentation": [segmentation],  # real seg is nested list
        "keypoints": vertices,
        "num_keypoints": len(vertices) / 3,
        # "score": 0.95,
        # "area": 45969,
        "iscrowd": 0,
    }
    annotations.append(shape_annotation)

    # find category of the horizontal position and vertical position
    hori_ann, vert_ann = shape_annotation.copy(), shape_annotation.copy()
    hori_param = calc_relative_category(
        panel_bottom_right[0],
        panel_top_left[0],
        shape["position"][0],
        img_params.HorizontalPosition,
    )
    vert_param = calc_relative_category(
        panel_top_left[1],
        panel_bottom_right[1],
        shape["position"][1],
        img_params.VerticalPosition,
    )
    hori_ann["category_id"] = find_category_id_by_name(
        hori_param.name, categories=categories
    )
    vert_ann["category_id"] = find_category_id_by_name(
        vert_param.name, categories=categories
    )
    annotations.append(hori_ann)
    annotations.append(vert_ann)

    # COMMENTED FOR SAVING TIME, UNCOMMENT TO PRODUCE ANNOTATION ON ALL CATEGORIES
    # for attr_name in SimpleShape.direct_categories:
    #     attr_value = shape[attr_name]
    #     category_id = find_category_id_by_name(attr_value,categories=categories)
    #     attr_annotation = {
    #         "id": get_annotation_id(),
    #         "image_id": image_id,
    #         "category_id": category_id,
    #         "bbox": bbox,
    #         "segmentation": [segmentation], # real seg is nested list
    #         # omit keypoints for attribute annotations for simplicity
    #         # "score": 0.95,
    #         # "area": 45969,
    #         "iscrowd": 0,
    #     }
    #     annotations.append(attr_annotation)

    return annotations


def format_joint_annotation(joint):
    attach_types = [joint["attach_type_A"], joint["attach_type_B"]]
    if "CORNER" in attach_types or "ARC" in attach_types:
        category_id = find_category_id_by_name("intersectionDot", categories)
    elif attach_types[0] == attach_types[1] == "EDGE":  # edge overlapping
        category_id = find_category_id_by_name("intersectionLineSegment", categories)
    else:  # arc overlapping, not likely to happen
        category_id = find_category_id_by_name("intersectionArc", categories)

    joint_coord = transform_coordinate(joint["position"])
    segmentation = joint_coord[:]
    keypoints = segmentation[:] + [2]
    neighbor_A_coord = transform_coordinate(
        next(
            (shape for shape in panel["shapes"] if shape["uid"] == joint["neighbor_A"]),
            None,
        )["position"]
    )
    neighbor_B_coord = transform_coordinate(
        next(
            (shape for shape in panel["shapes"] if shape["uid"] == joint["neighbor_B"]),
            None,
        )["position"]
    )
    keypoints += neighbor_A_coord + [2]
    keypoints += neighbor_B_coord + [2]
    segmentation += neighbor_A_coord
    segmentation += joint_coord
    segmentation += neighbor_B_coord  # TODO: consider changing seg representation in case joint not properly contained

    joint_annotation = {
        "id": get_annotation_id(),
        "image_id": image_id,
        "category_id": category_id,
        # "keypoints": keypoints,
        "segmentation": [segmentation],
        "bbox": calc_bbox(segmentation),
    }

    return joint_annotation


generate_num = 1
if len(sys.argv) >= 2 and sys.argv[1]:
    generate_num = int(sys.argv[1])

if len(sys.argv) >= 3 and sys.argv[2]:
    file_prefix = sys.argv[2]
with open("./categories.json", "r") as json_file:
    categories = list(json.load(json_file))

labels_dict = {
    "info": {},
    "licenses": [],
    "categories": [],
    "images": [],
    "annotations": [],
}
for i in range(generate_num):
    image_id = get_image_id()
    license = {"id": image_id}
    with Image.open(f"./output_png/{file_prefix}{i}.png") as img:
        width, height = img.size
    image = {
        "id": image_id,
        "license": license["id"],
        "file_name": f"{file_prefix}{i}.png",
        "height": height,
        "width": width,
        "date_captured": None,
    }
    with open(f"./output_json/{file_prefix}{i}.json", "r") as file:
        data = json.load(file)
    for panel in data:
        for shape in panel["shapes"]:
            shape_annotations = format_shape_annotations(
                shape=shape,
                panel_bottom_right=panel["bottom_right"],
                panel_top_left=panel["top_left"],
            )
            labels_dict["annotations"] += shape_annotations

        for joint in panel["joints"]:
            joint_annotation = format_joint_annotation(
                joint=joint
            )  # typically only 1 annotation for 1 joint
            labels_dict["annotations"].append(joint_annotation)

    # information unique to an image
    labels_dict["licenses"].append(license)
    labels_dict["images"].append(image)

labels_dict["categories"] = categories

with open("./my_dataset/labels.json", "w") as json_file:
    json.dump(labels_dict, json_file, indent=4)
