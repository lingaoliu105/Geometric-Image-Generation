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
)
dataset.default_skeleton = fo.KeypointSkeleton(
    labels=["center", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9"],
    edges=[[0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8], [0, 9]],
)

# dataset.save()
# dataset = foz.load_zoo_dataset(
#     "coco-2017",
#     split="validation",
#     dataset_name="coco-2017-validation",
# )

# while True:
#     pass

# Start the FiftyOne app to visualize the dataset
session = fo.launch_app(dataset)
session.wait()
