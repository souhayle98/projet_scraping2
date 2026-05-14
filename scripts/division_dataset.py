import os
import random
import shutil


INPUT_FOLDER  = r"C:\Users\J.P.M\Desktop\TD_S6\ApplicationIA\projet_2\data\augmentes"
OUTPUT_FOLDER = r"C:\Users\J.P.M\Desktop\TD_S6\ApplicationIA\projet_2\data\dataset_final"
FORMATS       = (".jpg", ".jpeg", ".png")

TRAIN_RATIO = 0.70
VAL_RATIO   = 0.15
TEST_RATIO  = 0.15



def diviser_liste(fichiers):
    random.shuffle(fichiers)
    total     = len(fichiers)
    n_train   = int(total * TRAIN_RATIO)
    n_val     = int(total * VAL_RATIO)

    train = fichiers[:n_train]
    val   = fichiers[n_train:n_train + n_val]
    test  = fichiers[n_train + n_val:]

    return train, val, test


def copier_fichiers(fichiers, dossier_source, dossier_destination):
    os.makedirs(dossier_destination, exist_ok=True)
    for fichier in fichiers:
        src = os.path.join(dossier_source, fichier)
        dst = os.path.join(dossier_destination, fichier)
        shutil.copy2(src, dst)


def diviser_dataset(input_folder, output_folder):

    classes = [c for c in os.listdir(input_folder)
               if os.path.isdir(os.path.join(input_folder, c))]

    for classe in classes:
        dossier_classe = os.path.join(input_folder, classe)
        fichiers= [f for f in os.listdir(dossier_classe)if f.lower().endswith(FORMATS)]
        train, val, test = diviser_liste(fichiers)
        copier_fichiers(train, dossier_classe, os.path.join(output_folder, "train", classe))
        copier_fichiers(val,   dossier_classe, os.path.join(output_folder, "val",   classe))
        copier_fichiers(test,  dossier_classe, os.path.join(output_folder, "test",  classe))

    print(f"\n✓ Dataset divisé dans : {output_folder}")


if __name__ == "__main__":
    diviser_dataset(INPUT_FOLDER, OUTPUT_FOLDER)