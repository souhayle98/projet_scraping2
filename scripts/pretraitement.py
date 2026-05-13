import os
import numpy as np
from PIL import Image


CLEAN_DIR  = r"C:\Users\J.P.M\Desktop\TD_S6\ApplicationIA\projet_2\data\nettoyees"
FINAL_DIR  = r"C:\Users\J.P.M\Desktop\TD_S6\ApplicationIA\projet_2\data\finales"
TAILLE     = (224, 224)   
QUALITE    = 95           # qualité JPG (0-100)

def lister_images(dossier):
    extensions = (".jpg", ".jpeg", ".png", ".webp")
    chemins = []
    for nom in os.listdir(dossier):
        if nom.lower().endswith(extensions):
            chemins.append(os.path.join(dossier, nom))
    return chemins

def redimensionner(img, taille=TAILLE):
    return img.resize(taille, Image.LANCZOS)

def normaliser(img):
    tableau = np.array(img, dtype=np.float32)
    return tableau / 255.0

"""
Reconvertit un tableau numpy [0, 1] vers une image PIL [0, 255].
Nécessaire pour sauvegarder l'image après normalisation.
"""
def denormaliser(tableau):
    pixels = (tableau * 255).astype(np.uint8)
    return Image.fromarray(pixels)

def convertir_en_jpg(img):
    return img.convert("RGB")

def creer_dossier_final(nom_classe, final_dir=FINAL_DIR):
    dossier = os.path.join(final_dir, nom_classe)
    os.makedirs(dossier, exist_ok=True)
    return dossier


def sauvegarder_image(img, dossier_dest, nom_fichier, qualite=QUALITE):
    nom_jpg    = os.path.splitext(nom_fichier)[0] + ".jpg"
    chemin_dst = os.path.join(dossier_dest, nom_jpg)
    img.save(chemin_dst, format="JPEG", quality=qualite)
    return chemin_dst


def pretraiter_image(chemin_src, dossier_dest):
    try:
        img = Image.open(chemin_src)

        img = convertir_en_jpg(img)           
        img = redimensionner(img)            
        tableau = normaliser(img)             
        img = denormaliser(tableau)          

        nom_fichier = os.path.basename(chemin_src)
        sauvegarder_image(img, dossier_dest, nom_fichier)
        return True

    except Exception as e:
        print(f"Erreur sur {os.path.basename(chemin_src)} : {e}")
        return False


def pretraiter_dossier(dossier_src, nom_classe):

    images       = lister_images(dossier_src)
    dossier_dest = creer_dossier_final(nom_classe)
    succes       = 0

    for chemin in images:
        if pretraiter_image(chemin, dossier_dest):
            succes += 1

    print(f"[{nom_classe}] {succes}/{len(images)} images prétraitées")
    return succes


def pipeline_pretraitement(clean_dir=CLEAN_DIR):
    
    os.makedirs(FINAL_DIR, exist_ok=True)
    total = 0

    for nom in sorted(os.listdir(clean_dir)):
        dossier = os.path.join(clean_dir, nom)
        if os.path.isdir(dossier):
            total += pretraiter_dossier(dossier, nom_classe=nom)

    print(f"\nPrétraitement terminé — {total} images sauvegardées dans {FINAL_DIR}")


if __name__ == "__main__":
    pipeline_pretraitement()