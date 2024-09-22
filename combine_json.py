import json
import sys
from PIL import Image

generate_num = 10
# if len(sys.argv) > 1 and sys.argv[1]:
#     generate_num = int(sys.argv[1])
get_image_id = (x for x in range (1000000)).__next__
get_annotation_id = (x for x in range (100000)).__next__
width = 0
height = 0
def find_category_id_by_name(name,categories):
    # use non-case-sensitive comparison
    return next((
                    x["id"]
                    for x in categories
                    if x["name"].lower().startswith(name.lower())
                    or name.lower().startswith(x["name"].lower())
                ),None)

def transform_coordinate(coordinate):
    global width,height
    return [
        coordinate[0] / 20 * width + width / 2,
        height / 2 - coordinate[1] / 20 * height,
    ]

def calc_bbox(segmentation):
    assert len(segmentation)>0 and len(segmentation)%2==0
    segmentation_x_coords = [segmentation[x] for x in range(0,len(segmentation),2)]
    segmentation_y_coords = [segmentation[x] for x in range(1,len(segmentation),2)]
    return [min(segmentation_x_coords),min(segmentation_y_coords),max(segmentation_x_coords)-min(segmentation_x_coords),max(segmentation_y_coords)-min(segmentation_y_coords)]
def format_shape_annotations(shape): # multiple annotations for 1 shape, each annotation for each attribute (category)
    annotations = []
    vertices = transform_coordinate(shape["position"])+[2]
    segmentation = []
    coordinates = shape["base_geometry"]["coordinates"][0]
    for coordinate in coordinates[:-1]:  
        transformed_coord = transform_coordinate(coordinate)
        vertices += transformed_coord              
        vertices.append(2)
        segmentation+= transformed_coord

    # find category id of the shape
    category_id = find_category_id_by_name(shape["shape"],categories=categories)

    shape_annotation = {
        "id": get_annotation_id(),
        "image_id": image_id,
        "category_id": category_id,
        "bbox": calc_bbox(segmentation),
        "segmentation": [segmentation], # real seg is nested list
        "keypoints": vertices,
        "num_keypoints": len(vertices)/3,
        # "score": 0.95,
        # "area": 45969,
        "iscrowd": 0,
    }
    annotations.append(shape_annotation)
    
    return annotations

def format_joint_annotation(joint):
    attach_types = [joint["attach_type_A"], joint["attach_type_B"]]
    if "CORNER" in attach_types or "ARC" in attach_types:
        category_id = find_category_id_by_name("intersectionDot", categories)
    elif attach_types[0]==attach_types[1]=="EDGE":  # edge overlapping
        category_id = find_category_id_by_name("intersectionLineSegment", categories)
    else: # arc overlapping, not likely to happen
        category_id = find_category_id_by_name("intersectionArc", categories)

    joint_coord = transform_coordinate(joint["position"])
    segmentation = joint_coord[:]
    keypoints = segmentation[:] + [2]
    neighbor_A_coord = transform_coordinate(next(
        (shape for shape in panel["shapes"] if shape["uid"] == joint["neighbor_A"]),
        None,
    )["position"])
    neighbor_B_coord = transform_coordinate(next(
        (shape for shape in panel["shapes"] if shape["uid"] == joint["neighbor_B"]),
        None,
    )["position"])
    keypoints += neighbor_A_coord + [2]
    keypoints += neighbor_B_coord + [2]
    segmentation += neighbor_A_coord
    segmentation += joint_coord
    segmentation += neighbor_B_coord # TODO: consider changing seg representation in case joint not properly contained
    
    joint_annotation = {
        "id": get_annotation_id(),
        "image_id": image_id,
        "category_id": category_id,
        "keypoints": keypoints,
        "segmentation": [segmentation],
        "bbox": calc_bbox(segmentation)
    }

    return joint_annotation

with open("./categories.json","r") as json_file:
    categories = list(json.load(json_file))

labels_dict = {"info":{},"licenses":[],"categories":[],"images":[],"annotations":[]}
for i in range (generate_num):
    image_id = get_image_id()
    license = {"id":image_id}
    with Image.open(f"./output_png/new{i}.png") as img:
        width, height = img.size
    image = {
        "id": image_id,
        "license": license["id"],
        "file_name": f"new{i}.png",
        "height": height,
        "width": width,
        "date_captured": None,
    }
    with open(f"./output_json/new{i}.json", "r") as file:
        data = json.load(file)
    for panel in data:
        for shape in panel["shapes"]:
            shape_annotations = format_shape_annotations(shape=shape)
            labels_dict["annotations"]+= shape_annotations
            
        for joint in panel["joints"]:
            joint_annotation = format_joint_annotation(joint=joint) # typically only 1 annotation for 1 joint
            labels_dict["annotations"].append(joint_annotation)

    # information unique to an image
    labels_dict["licenses"].append(license)
    labels_dict["images"].append(image)

labels_dict["categories"] = categories

with open("./my_dataset/labels.json","w") as json_file:
    json.dump(labels_dict,json_file,indent=4)
