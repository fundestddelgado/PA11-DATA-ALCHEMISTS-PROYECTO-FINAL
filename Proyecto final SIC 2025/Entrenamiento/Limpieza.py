import os
import shutil
import random

RAW_ROOT = "data_raw"
SPLIT_ROOT = "data_splits"
RANDOM_SEED = 42
train_ratio = 0.7
val_ratio = 0.15  # el resto será test

random.seed(RANDOM_SEED)

classes = [d for d in os.listdir(RAW_ROOT) if os.path.isdir(os.path.join(RAW_ROOT, d))]

for split in ["train", "val", "test"]:
    for cls in classes:
        os.makedirs(os.path.join(SPLIT_ROOT, split, cls), exist_ok=True)

for cls in classes:
    class_dir = os.path.join(RAW_ROOT, cls)
    imgs = [f for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))]
    random.shuffle(imgs)

    n = len(imgs)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    n_test = n - n_train - n_val

    train_files = imgs[:n_train]
    val_files = imgs[n_train:n_train + n_val]
    test_files = imgs[n_train + n_val:]

    def move_files(files, split):
        for fname in files:
            src = os.path.join(class_dir, fname)
            dst = os.path.join(SPLIT_ROOT, split, cls, fname)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)  # o move2 si quieres mover en vez de copiar

    move_files(train_files, "train")
    move_files(val_files, "val")
    move_files(test_files, "test")

print("Split completado.")