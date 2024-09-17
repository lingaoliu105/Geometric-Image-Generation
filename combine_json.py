import json
import sys
from PIL import Image

generate_num = 10
# if len(sys.argv) > 1 and sys.argv[1]:
#     generate_num = int(sys.argv[1])
get_image_id = (x for x in range (1000000)).__next__
get_annotation_id = (x for x in range (100000)).__next__

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
            vertices = []
            segmentation = []
            coordinates = shape["base_geometry"]["coordinates"][0]
            for coordinate in coordinates:  
                transformed_coord = [coordinate[0]/20*width+width/2,height/2 - coordinate[1] / 20 * height]
                vertices += transformed_coord              
                vertices.append(2)
                segmentation+= transformed_coord
            segmentation_x_coords = [segmentation[x] for x in range(0,len(segmentation),2)]
            segmentation_y_coords = [segmentation[x] for x in range(1,len(segmentation),2)]

            # find category id of the shape
            category_id = next(
                (
                    x["id"]
                    for x in categories
                    if x["name"].startswith(shape["shape"].lower())
                    or shape["shape"].lower().startswith(x["name"])
                ),
                None,
            )
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

    # information unique to an image
    labels_dict["licenses"].append(license)
    labels_dict["images"].append(image)

    labels_dict["annotations"].append(shape_annotation)
labels_dict["categories"] = categories

with open("./my_dataset/labels.json","w") as json_file:
    json.dump(labels_dict,json_file,indent=4)
