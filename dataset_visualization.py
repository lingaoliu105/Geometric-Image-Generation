import fiftyone as fo
import fiftyone.utils.data as foud
import fiftyone.types as fot
import fiftyone.zoo as foz


# Path to your dataset (images or videos)
# dataset_dir = "./coco_dataset/example"
dataset_dir = "./my_dataset"

# # Create a dataset from COCO format
dataset = fo.Dataset.from_dir(
    dataset_type=fot.COCODetectionDataset,
    dataset_dir=dataset_dir,
    label_types=["detections", "segmentations","keypoints"],
)


# dataset = foz.load_zoo_dataset(
#     "coco-2017",
#     split="validation",
#     dataset_name="coco-2017-validation",
#     label_types=["detections","segmentations"],  # Load only detection labels
# )

# while True:
#     pass

# Start the FiftyOne app to visualize the dataset
session = fo.launch_app(dataset)
session.wait()
