import os
import random
import logging
import imagehash
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageFilter


BASE_DIR = r"C:\Users\J.P.M\Desktop\TD_S6\ApplicationIA\projet_2\data\brutes"
LOG_FILE     = r"C:\Users\J.P.M\Desktop\TD_S6\ApplicationIA\projet_2\rapports\nettoyage.log"
TAILLE_MIN_PX = 200
SEUIL_HASH    = 10
NB_APERCU     = 10


def configurer_logger():
    os.makedirs("rapports", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger("nettoyage")

logger = configurer_logger()



def lister_images(dossier):
    extensions = (".jpg", ".jpeg", ".png", ".webp")
    chemins = []
    for nom in os.listdir(dossier):
        if nom.lower().endswith(extensions):
            chemins.append(os.path.join(dossier, nom))
    return chemins



"""
    On calcule un hash (empreinte visuelle) pour chaque image.
    Si deux images ont des hashs très proches, c'est un doublon → on supprime le 2ème.
"""
def supprimer_doublons(dossier):
    images    = lister_images(dossier)
    #dictionnaire des images hashees : {chemin:hash}
    hashes    = {}  
    supprimes = 0

    for chemin in images:
        try:
            img = Image.open(chemin)
            #Le hash représente le contenu visuel de l’image
            h   = imagehash.phash(img)   
        except Exception:
            continue

        est_doublon = False
        for chemin_ref, h_ref in hashes.items():
            if abs(h - h_ref) <= SEUIL_HASH:   
                os.remove(chemin)
                logger.info("Doublon supprimé : %s", os.path.basename(chemin))
                supprimes += 1
                est_doublon = True
                break

        if not est_doublon:
            hashes[chemin] = h

    logger.info("[Doublons] %d supprimé(s)", supprimes)
    return supprimes




"""
Supprime les images trop petites.
Si la largeur OU la hauteur est inférieure à TAILLE_MIN_PX → suppression.
"""
def filtrer_par_taille(dossier):
    images    = lister_images(dossier)
    supprimes = 0

    for chemin in images:
        try:
            img= Image.open(chemin)
            largeur, hauteur = img.size
            if largeur < TAILLE_MIN_PX or hauteur < TAILLE_MIN_PX:
                os.remove(chemin)
                logger.info("Trop petite (%dx%d) : %s", largeur, hauteur, os.path.basename(chemin))
                supprimes += 1
        except Exception:
            continue

    logger.info("[Taille] %d supprimée(s)", supprimes)
    return supprimes





"""
Supprime les images corrompues (fichiers cassés ou illisibles).
On essaie d'ouvrir et de lire complètement chaque image.
Si ça échoue → l'image est corrompue → suppression.
"""
def supprimer_corrompues(dossier):
    images    = lister_images(dossier)
    supprimes = 0

    for chemin in images:
        try:
            img = Image.open(chemin)
            img.load()           # force la lecture complète du fichier
            img.convert("RGB")   # vérifie que les canaux couleur sont valides
        except Exception:
            os.remove(chemin)
            logger.info("Corrompue supprimée : %s", os.path.basename(chemin))
            supprimes += 1

    logger.info("[Corruption] %d supprimée(s)", supprimes)
    return supprimes




"""
detection des textes sur les images
"""
def a_un_filigrane(chemin):
    try:
        img   = Image.open(chemin).convert("L")      # niveaux de gris
        bords = np.array(img.filter(ImageFilter.FIND_EDGES))  # contours
        h, w  = bords.shape
        marge = max(1, int(min(h, w) * 0.10))        # bordure de 10 %

        # extraire uniquement la zone périphérique
        bordure = np.concatenate([
            bords[:marge, :].ravel(),    # haut
            bords[-marge:, :].ravel(),   # bas
            bords[:, :marge].ravel(),    # gauche
            bords[:, -marge:].ravel(),   # droite
        ])

        ratio = np.mean(bordure > 10)   # proportion de pixels avec contour fort
        return float(ratio) > 0.30

    except Exception:
        return False



"""Supprime toutes les images détectées comme ayant un filigrane."""
def supprimer_filigranes(dossier):
    images    = lister_images(dossier)
    supprimes = 0

    for chemin in images:
        if a_un_filigrane(chemin):
            os.remove(chemin)
            logger.info("Filigrane probable supprimé : %s", os.path.basename(chemin))
            supprimes += 1

    logger.info("[Filigrane] %d supprimée(s)", supprimes)
    return supprimes



def afficher_apercu(dossier, nom_classe):
    images = lister_images(dossier)
    if not images:
        print("Aucune image dans", dossier)
        return

    echantillon = random.sample(images, min(NB_APERCU, len(images)))

    plt.figure(figsize=(15, 6))
    plt.suptitle(f"Vérification — {nom_classe}", fontsize=13, fontweight="bold")

    for i, chemin in enumerate(echantillon):
        plt.subplot(2, 5, i + 1)
        try:
            img = Image.open(chemin).convert("RGB")
            plt.imshow(img)
        except Exception:
            plt.text(0.5, 0.5, "ERREUR", ha="center", va="center", color="red")
        plt.title(os.path.basename(chemin), fontsize=6)
        plt.axis("off")

    plt.tight_layout()
    plt.show()


#lance la verification pour toute les classes
def verification_manuelle(base_dir=BASE_DIR):
    for nom in sorted(os.listdir(base_dir)):
        dossier = os.path.join(base_dir, nom)
        if os.path.isdir(dossier):
            afficher_apercu(dossier, nom_classe=nom)




def nettoyer_dossier(dossier):
    logger.info("=== Nettoyage : %s ===", dossier)

    stats = {
        "corrompues"  : supprimer_corrompues(dossier),
        "trop_petites": filtrer_par_taille(dossier),
        "doublons"    : supprimer_doublons(dossier),
        "filigranes"  : supprimer_filigranes(dossier),
        "restantes"   : len(lister_images(dossier)),
    }

    logger.info("Résumé : %s\n", stats)

    return stats


if __name__ == "__main__":
    dossiers = [
    "hibou_grand_duc",
    "flamant_rose",
    "martin_pecheur",
    "cygne_tubercule",
    "pic_vert"
    ]
    for dossier in dossiers:
        chemin = os.path.join(BASE_DIR, dossier)
        nettoyer_dossier(chemin)
