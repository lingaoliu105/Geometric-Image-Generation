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
            vertices = transform_coordinate(shape["position"])+[2]
            segmentation = []
            coordinates = shape["base_geometry"]["coordinates"][0]
            for coordinate in coordinates[:-1]:  
                transformed_coord = transform_coordinate(coordinate)
                vertices += transformed_coord              
                vertices.append(2)
                segmentation+= transformed_coord
            segmentation_x_coords = [segmentation[x] for x in range(0,len(segmentation),2)]
            segmentation_y_coords = [segmentation[x] for x in range(1,len(segmentation),2)]

            # find category id of the shape
            category_id = find_category_id_by_name(shape["shape"],categories=categories)

            shape_annotation = {
                "id": get_annotation_id(),
                "image_id": image_id,
                "category_id": category_id,
                "bbox": [min(segmentation_x_coords),min(segmentation_y_coords),max(segmentation_x_coords)-min(segmentation_x_coords),max(segmentation_y_coords)-min(segmentation_y_coords)],
                "segmentation": [segmentation],
                "keypoints": vertices,
                "num_keypoints": len(vertices)/3,
                # "score": 0.95,
                # "area": 45969,
                "iscrowd": 0,
            }
            labels_dict["annotations"].append(shape_annotation)

        for joint in panel["joints"]:
            attach_types = [joint["attach_type_A"],joint["attach_type_B"]]
            if "CORNER" in attach_types:
                category_id = find_category_id_by_name("intersectionDot",categories)
            elif "ARC" in attach_types:
                category_id = find_category_id_by_name("intersectionArc",categories)
            else: # assume the rest is edge overlapping
                category_id = find_category_id_by_name("intersectionLineSegment",categories)
            keypoints = transform_coordinate(joint["position"]) + [2]
            neighbor_A = next((shape for shape in panel["shapes"] if shape["uid"]==joint["neighbor_A"]),None)
            neighbor_B = next((shape for shape in panel["shapes"] if shape["uid"]==joint["neighbor_B"]),None)
            keypoints += transform_coordinate(neighbor_A["position"])+[2]
            keypoints += transform_coordinate(neighbor_B["position"])+[2]
            joint_annotation = {
                "id": get_annotation_id(),
                "image_id": image_id,
                "category_id":category_id,
                "keypoints": keypoints
            }
            labels_dict["annotations"].append(shape_annotation)

    # information unique to an image
    labels_dict["licenses"].append(license)
    labels_dict["images"].append(image)

    labels_dict["annotations"].append(shape_annotation)
labels_dict["categories"] = categories

with open("./my_dataset/labels.json","w") as json_file:
    json.dump(labels_dict,json_file,indent=4)
