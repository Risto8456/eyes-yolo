# -*- coding: utf-8 -*-

import os
import random
import shutil

TRAIN_RATIO = 0.9
IMAGE_EXTS = ('.jpg', '.jpeg', '.png')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
LABELS_DIR = os.path.join(BASE_DIR, 'labels')

TRAIN_IMG_DIR = os.path.join(IMAGES_DIR, 'train')
VAL_IMG_DIR   = os.path.join(IMAGES_DIR, 'val')
TRAIN_LBL_DIR = os.path.join(LABELS_DIR, 'train')
VAL_LBL_DIR   = os.path.join(LABELS_DIR, 'val')


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def main():
    for d in [TRAIN_IMG_DIR, VAL_IMG_DIR, TRAIN_LBL_DIR, VAL_LBL_DIR]:
        mkdir(d)

    image_files = [
        f for f in os.listdir(IMAGES_DIR)
        if f.lower().endswith(IMAGE_EXTS)
    ]

    image_ids = []
    for img in image_files:
        stem = os.path.splitext(img)[0]
        label_path = os.path.join(LABELS_DIR, stem + '.txt')
        if os.path.exists(label_path):
            image_ids.append(stem)
        else:
            print("[WARN] Missing label for:", stem)

    print("Found image-label pairs:", len(image_ids))

    random.shuffle(image_ids)

    split_idx = int(len(image_ids) * TRAIN_RATIO)
    train_ids = image_ids[:split_idx]
    val_ids   = image_ids[split_idx:]

    def move_files(ids, img_dst, lbl_dst):
        for stem in ids:
            for ext in IMAGE_EXTS:
                src_img = os.path.join(IMAGES_DIR, stem + ext)
                if os.path.exists(src_img):
                    shutil.move(src_img, os.path.join(img_dst, stem + ext))
                    break

            src_lbl = os.path.join(LABELS_DIR, stem + '.txt')
            shutil.move(src_lbl, os.path.join(lbl_dst, stem + '.txt'))

    move_files(train_ids, TRAIN_IMG_DIR, TRAIN_LBL_DIR)
    move_files(val_ids, VAL_IMG_DIR, VAL_LBL_DIR)

    print("Done")
    print("Train samples:", len(train_ids))
    print("Val samples  :", len(val_ids))


if __name__ == "__main__":
    main()

