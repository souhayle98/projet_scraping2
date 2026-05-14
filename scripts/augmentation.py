import os
import random
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt

INPUT_FOLDER     = r"C:\Users\J.P.M\Desktop\TD_S6\ApplicationIA\projet_2\data\finales"
OUTPUT_FOLDER    = r"C:\Users\J.P.M\Desktop\TD_S6\ApplicationIA\projet_2\data\augmentes"
NB_AUGMENTATIONS = 5
FORMATS          = (".jpg")


def augmenter(image):
    image = image.rotate(random.uniform(-15, 15))
    if random.random() > 0.5:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)

    w, h   = image.size
    f      = random.uniform(0.9, 1.1)
    nw, nh = int(w / f), int(h / f)
    x1     = max(0, w // 2 - nw // 2)
    y1     = max(0, h // 2 - nh // 2)
    image  = image.crop((x1, y1, x1 + nw, y1 + nh)).resize((w, h), Image.LANCZOS)

    image = ImageEnhance.Brightness(image).enhance(random.uniform(0.8, 1.2))

    image = ImageEnhance.Contrast(image).enhance(random.uniform(0.8, 1.2))

    return image


def generer_dataset(input_folder, output_folder, nb_augmentations):

    os.makedirs(output_folder, exist_ok=True)
    resultats = {}

    for classe in os.listdir(input_folder):
        dossier_classe = os.path.join(input_folder, classe)

        if not os.path.isdir(dossier_classe):
            continue

        dossier_sortie_classe = os.path.join(output_folder, classe)
        os.makedirs(dossier_sortie_classe, exist_ok=True)

        fichiers = [f for f in os.listdir(dossier_classe) if f.lower().endswith(FORMATS)]

        for fichier in fichiers:
            chemin_original = os.path.join(dossier_classe, fichier)
            image_orig      = Image.open(chemin_original).convert("RGB")
            nom, ext        = os.path.splitext(fichier)

            # Sauvegarder l'image originale dans le dossier de sortie
            chemin_orig_copie = os.path.join(dossier_sortie_classe, fichier)
            image_orig.save(chemin_orig_copie)

            chemins_aug = []
            for i in range(1, nb_augmentations + 1):
                image_aug     = augmenter(image_orig)
                chemin_sortie = os.path.join(dossier_sortie_classe, f"{nom}_aug_{i}{ext}")
                image_aug.save(chemin_sortie)
                chemins_aug.append(chemin_sortie)

            resultats[chemin_original] = chemins_aug
            print(f"[{classe}] {fichier} + {nb_augmentations} variantes sauvegardées")

    print(f"\n✓ {len(resultats)} images traitées → {len(resultats) * (nb_augmentations + 1)} images au total")
    return resultats

def afficher_grille(resultats, nb_exemples=3):

    exemples = list(resultats.items())[:nb_exemples]
    nb_cols  = NB_AUGMENTATIONS + 1

    fig, axes = plt.subplots(len(exemples), nb_cols, figsize=(3 * nb_cols, 3 * len(exemples)))

    for ligne, (chemin_orig, chemins_aug) in enumerate(exemples):
        tous_chemins = [chemin_orig] + chemins_aug
        titres       = ["Originale"] + [f"Aug {i}" for i in range(1, nb_cols)]

        for col, (chemin, titre) in enumerate(zip(tous_chemins, titres)):
            axes[ligne][col].imshow(Image.open(chemin).convert("RGB"))
            axes[ligne][col].set_title(titre, fontsize=9)
            axes[ligne][col].axis("off")

    plt.suptitle("Data Augmentation", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    resultats = generer_dataset(INPUT_FOLDER, OUTPUT_FOLDER, NB_AUGMENTATIONS)
    afficher_grille(resultats, nb_exemples=3)
