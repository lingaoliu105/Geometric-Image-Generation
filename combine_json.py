import json
import sys
from PIL import Image

generate_num = 10
# if len(sys.argv) > 1 and sys.argv[1]:
#     generate_num = int(sys.argv[1])

labels_dict = {"info":{},"licenses":[],"categories":[],"images":[],"annotations":[]}
for i in range (generate_num):
    license = {"id":i}
    with Image.open(f"./output_png/new{i}.png") as img:
        width, height = img.size
    image = {
        "id": i,
        "license": i,
        "file_name": f"new{i}.png",
        "height": height,
        "width": width,
        "date_captured": None,
    }
    with open(f"./output_json/new{i}.json", "r") as file:
        data = json.load(file)
    # print(data)
    vertices = []
    for panel in data:
        for shape in panel["shapes"]:
            coordinates = shape["base_geometry"]["coordinates"][0]
            for coordinate in coordinates:  
                vertices.append(coordinate[0]/20*width+width/2)
                vertices.append(height/2 - coordinate[1] / 20 * height)
                vertices.append(2)
    annotation = {
        "id": i,
        "image_id": i,
        # "category_id": 2,
        # "bbox": [260, 177, 231, 199],
        # "segmentation": [...],
        "keypoints": vertices,
        "num_keypoints": len(vertices)/3,
        # "score": 0.95,
        # "area": 45969,
        # "iscrowd": 0,
    }
    labels_dict["licenses"].append(license)
    labels_dict["annotations"].append(annotation)
    labels_dict["images"].append(image)

with open("./my_dataset/labels.json","w") as json_file:
    json.dump(labels_dict,json_file,indent=4)
