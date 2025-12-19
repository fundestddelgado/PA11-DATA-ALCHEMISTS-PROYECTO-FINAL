# Script para restaurar (opcional, solo si quieres deshacer)
import os
import shutil

TRAIN_DIR = "data_splits/train"
BACKUP_DIR = "data_splits/train_backup_removed"

for cls in os.listdir(BACKUP_DIR):
    backup_cls_path = os.path.join(BACKUP_DIR, cls)
    train_cls_path = os.path.join(TRAIN_DIR, cls)

    for img in os.listdir(backup_cls_path):
        src = os.path.join(backup_cls_path, img)
        dst = os.path.join(train_cls_path, img)
        shutil.move(src, dst)

print(" Dataset restaurado al estado original")