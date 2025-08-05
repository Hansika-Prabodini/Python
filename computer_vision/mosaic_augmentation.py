"""Source: https://github.com/jason9075/opencv-mosaic-data-aug"""

import glob
import os
import random
from string import ascii_lowercase, digits

import cv2
import numpy as np

# Parameters
OUTPUT_SIZE = (720, 1280)  # Height, Width
SCALE_RANGE = (0.4, 0.6)  # if height or width lower than this scale, drop it.
FILTER_TINY_SCALE = 1 / 100
LABEL_DIR = ""
IMG_DIR = ""
OUTPUT_DIR = ""
NUMBER_IMAGES = 250


def main() -> None:
    """
    Get images list and annotations list from input dir.
    Update new images and annotations.
    Save images and annotations in output dir.
    """
    img_paths, annos = get_dataset(LABEL_DIR, IMG_DIR)
    for index in range(NUMBER_IMAGES):
        idxs = random.sample(range(len(annos)), 4)
        new_image, new_annos, path = update_image_and_anno(
            img_paths,
            annos,
            idxs,
            OUTPUT_SIZE,
            SCALE_RANGE,
            filter_scale=FILTER_TINY_SCALE,
        )

        # Get random string code: '7b7ad245cdff75241935e4dd860f3bad'
        letter_code = random_chars(32)
        file_name = path.split(os.sep)[-1].rsplit(".", 1)[0]
        file_root = f"{OUTPUT_DIR}/{file_name}_MOSAIC_{letter_code}"
        cv2.imwrite(f"{file_root}.jpg", new_image, [cv2.IMWRITE_JPEG_QUALITY, 85])
        print(f"Succeeded {index + 1}/{NUMBER_IMAGES} with {file_name}")
        annos_list = []
        for anno in new_annos:
            width = anno[3] - anno[1]
            height = anno[4] - anno[2]
            x_center = anno[1] + width / 2
            y_center = anno[2] + height / 2
            obj = f"{anno[0]} {x_center} {y_center} {width} {height}"
            annos_list.append(obj)
        with open(f"{file_root}.txt", "w") as outfile:
            outfile.write("\n".join(line for line in annos_list))


def get_dataset(label_dir: str, img_dir: str) -> tuple[list, list]:
    """
    - label_dir <type: str>: Path to label include annotation of images
    - img_dir <type: str>: Path to folder contain images
    Return <type: list>: List of images path and labels
    """
    img_paths = []
    labels = []
    for label_file in glob.glob(os.path.join(label_dir, "*.txt")):
        label_name = label_file.split(os.sep)[-1].rsplit(".", 1)[0]
        with open(label_file) as in_file:
            obj_lists = in_file.readlines()
        img_path = os.path.join(img_dir, f"{label_name}.jpg")

        boxes = []
        for obj_list in obj_lists:
            obj = obj_list.rstrip("\n").split(" ")
            xmin = float(obj[1]) - float(obj[3]) / 2
            ymin = float(obj[2]) - float(obj[4]) / 2
            xmax = float(obj[1]) + float(obj[3]) / 2
            ymax = float(obj[2]) + float(obj[4]) / 2

            boxes.append([int(obj[0]), xmin, ymin, xmax, ymax])
        if not boxes:
            continue
        img_paths.append(img_path)
        labels.append(boxes)
    return img_paths, labels


def update_image_and_anno(
    all_img_list: list,
    all_annos: list,
    idxs: list[int],
    output_size: tuple[int, int],
    scale_range: tuple[float, float],
    filter_scale: float = 0.0,
) -> tuple[list, list, str]:
    """
    - all_img_list <type: list>: list of all images
    - all_annos <type: list>: list of all annotations of specific image
    - idxs <type: list>: index of image in list
    - output_size <type: tuple>: size of output image (Height, Width)
    - scale_range <type: tuple>: range of scale image
    - filter_scale <type: float>: the condition of downscale image and bounding box
    Return:
        - output_img <type: narray>: image after resize
        - new_anno <type: list>: list of new annotation after scale
        - path[0] <type: string>: get the name of image file
    """
    output_img = np.zeros([output_size[0], output_size[1], 3], dtype=np.uint8)
    scale_x = scale_range[0] + random.random() * (scale_range[1] - scale_range[0])
    scale_y = scale_range[0] + random.random() * (scale_range[1] - scale_range[0])
    divid_point_x = int(scale_x * output_size[1])
    divid_point_y = int(scale_y * output_size[0])

    all_new_annos_np_list = []
    path_list = []
    for i, index in enumerate(idxs):
        path = all_img_list[index]
        path_list.append(path)
        img_annos = all_annos[index]
        img = cv2.imread(path)

        if not img_annos:  # Handle cases where img_annos might be empty
            if i == 0:  # top-left
                img = cv2.resize(img, (divid_point_x, divid_point_y))
                output_img[:divid_point_y, :divid_point_x, :] = img
            elif i == 1:  # top-right
                img = cv2.resize(img, (output_size[1] - divid_point_x, divid_point_y))
                output_img[:divid_point_y, divid_point_x : output_size[1], :] = img
            elif i == 2:  # bottom-left
                img = cv2.resize(img, (divid_point_x, output_size[0] - divid_point_y))
                output_img[divid_point_y : output_size[0], :divid_point_x, :] = img
            else:  # bottom-right
                img = cv2.resize(
                    img, (output_size[1] - divid_point_x, output_size[0] - divid_point_y)
                )
                output_img[
                    divid_point_y : output_size[0], divid_point_x : output_size[1], :
                ] = img
            continue # Skip to the next iteration if no annotations

        # Convert to numpy array, separating class_ids and coords
        class_ids = np.array([bbox[0] for bbox in img_annos]).reshape(-1, 1)
        coords = np.array([bbox[1:] for bbox in img_annos], dtype=np.float32)

        if i == 0:  # top-left
            img = cv2.resize(img, (divid_point_x, divid_point_y))
            output_img[:divid_point_y, :divid_point_x, :] = img
            transformed_coords = coords * np.array([scale_x, scale_y, scale_x, scale_y])
        elif i == 1:  # top-right
            img = cv2.resize(img, (output_size[1] - divid_point_x, divid_point_y))
            output_img[:divid_point_y, divid_point_x : output_size[1], :] = img
            transformed_coords = coords * np.array([(1 - scale_x), scale_y, (1 - scale_x), scale_y])
            transformed_coords[:, [0, 2]] = scale_x + transformed_coords[:, [0, 2]]
        elif i == 2:  # bottom-left
            img = cv2.resize(img, (divid_point_x, output_size[0] - divid_point_y))
            output_img[divid_point_y : output_size[0], :divid_point_x, :] = img
            transformed_coords = coords * np.array([scale_x, (1 - scale_y), scale_x, (1 - scale_y)])
            transformed_coords[:, [1, 3]] = scale_y + transformed_coords[:, [1, 3]]
        else:  # bottom-right
            img = cv2.resize(
                img, (output_size[1] - divid_point_x, output_size[0] - divid_point_y)
            )
            output_img[
                divid_point_y : output_size[0], divid_point_x : output_size[1], :
            ] = img
            transformed_coords = coords * np.array([(1 - scale_x), (1 - scale_y), (1 - scale_x), (1 - scale_y)])
            transformed_coords[:, [0, 2]] = scale_x + transformed_coords[:, [0, 2]]
            transformed_coords[:, [1, 3]] = scale_y + transformed_coords[:, [1, 3]]

        combined_anno_np = np.hstack((class_ids, transformed_coords))
        all_new_annos_np_list.append(combined_anno_np)

    # Concatenate all annotations
    new_anno_np = np.vstack(all_new_annos_np_list) if all_new_annos_np_list else np.empty((0, 5))

    # Remove bounding box small than scale of filter
    if filter_scale > 0:
        widths = new_anno_np[:, 3] - new_anno_np[:, 1]
        heights = new_anno_np[:, 4] - new_anno_np[:, 2]
        mask = (widths > filter_scale) & (heights > filter_scale)
        new_anno_np = new_anno_np[mask]

    new_anno = new_anno_np.tolist()

    return output_img, new_anno, path_list[0]


def random_chars(number_char: int) -> str:
    """
    Automatic generate random 32 characters.
    Get random string code: '7b7ad245cdff75241935e4dd860f3bad'
    >>> len(random_chars(32))
    32
    """
    assert number_char > 1, "The number of character should greater than 1"
    letter_code = ascii_lowercase + digits
    return "".join(random.choice(letter_code) for _ in range(number_char))


if __name__ == "__main__":
    main()
    print("DONE ✅")
