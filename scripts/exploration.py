import os
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image


BASE_DIR = r"C:\Users\J.P.M\Desktop\TD_S6\ApplicationIA\projet_2\data\brutes"

ESPECES = {
    "hibou_grand_duc" : "Hibou grand-duc",
    "flamant_rose"    : "Flamant rose",
    "martin_pecheur"  : "Martin-pêcheur",
    "cygne_tubercule" : "Cygne tuberculé",
    "pic_vert"        : "Pic vert",
}

EXTENSIONS   = (".jpg", ".jpeg", ".png", ".webp")
SEUIL_ALERTE = 70

def lister_images(dossier):
    if not os.path.isdir(dossier):
        print(f"[!] Dossier introuvable : {dossier}")
        return []
    return [
        os.path.join(dossier, f)
        for f in os.listdir(dossier)
        if f.lower().endswith(EXTENSIONS)
    ]


def afficher_grille(espece_cle, nb_images=12):
    if espece_cle not in ESPECES:
        print(f"[!] Espèce inconnue : {espece_cle}")
        print(f"    Choix possibles : {', '.join(ESPECES)}")
        return

    dossier     = os.path.join(BASE_DIR, espece_cle)
    images      = lister_images(dossier)

    if not images:
        print(f"[!] Aucune image trouvée dans {dossier}")
        return

    echantillon = random.sample(images, min(nb_images, len(images)))

    nb_cols   = 4
    nb_lignes = -(-len(echantillon) // nb_cols)  

    fig, axes = plt.subplots(nb_lignes, nb_cols,
                             figsize=(nb_cols * 3, nb_lignes * 3 + 0.8))
    fig.suptitle(
        f"{ESPECES[espece_cle]}  —  {len(echantillon)} images "
        f"(sur {len(images)} disponibles)",
        fontsize=13, fontweight="bold"
    )

    if nb_lignes == 1:
        axes = list(axes) if nb_cols > 1 else [axes]
    else:
        axes = axes.flatten()

    for i, ax in enumerate(axes):
        if i < len(echantillon):
            try:
                img = Image.open(echantillon[i]).convert("RGB")
                ax.imshow(img)
                ax.set_title(os.path.basename(echantillon[i]),
                             fontsize=6, color="gray")
            except Exception:
                ax.text(0.5, 0.5, "Erreur", ha="center", va="center",
                        color="red", transform=ax.transAxes)
        ax.axis("off")

    plt.tight_layout()
    plt.show()

def afficher_distribution_tailles():
    couleurs = {
        "hibou_grand_duc" : "#D4821A",
        "flamant_rose"    : "#E75480",
        "martin_pecheur"  : "#2196F3",
        "cygne_tubercule" : "#546E7A",
        "pic_vert"        : "#388E3C",
    }

    fig, (ax_scatter, ax_hist) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Distribution des tailles originales (avant redimensionnement)",
                 fontsize=13, fontweight="bold")

    for cle, nom in ESPECES.items():
        dossier          = os.path.join(BASE_DIR, cle)
        images           = lister_images(dossier)
        largeurs, hauteurs = [], []

        for chemin in images:
            try:
                with Image.open(chemin) as img:
                    w, h = img.size
                    largeurs.append(w)
                    hauteurs.append(h)
            except Exception:
                continue

        if not largeurs:
            continue

        couleur = couleurs[cle]

        # nuage de points  largeur x hauteur
        ax_scatter.scatter(largeurs, hauteurs,
                           alpha=0.5, s=20,
                           color=couleur, label=nom)

        # histogramme des largeurs
        ax_hist.hist(largeurs, bins=20, alpha=0.55,
                     color=couleur, label=nom, edgecolor="none")

    # ligne cible 224 px
    ax_scatter.axvline(224, color="red", linewidth=1.4,
                       linestyle="--", label="Cible 224 px")
    ax_scatter.axhline(224, color="red", linewidth=1.4, linestyle="--")
    ax_hist.axvline(224, color="red", linewidth=1.4,
                    linestyle="--", label="Cible 224 px")

    ax_scatter.set_xlabel("Largeur (px)")
    ax_scatter.set_ylabel("Hauteur (px)")
    ax_scatter.set_title("Largeur x Hauteur par espèce")
    ax_scatter.legend(fontsize=8)

    ax_hist.set_xlabel("Largeur (px)")
    ax_hist.set_ylabel("Nombre d'images")
    ax_hist.set_title("Histogramme des largeurs")
    ax_hist.legend(fontsize=8)

    plt.tight_layout()
    plt.show()


# ─────────────────────────────────────────────────────────────────────────────
def afficher_priorites_collecte():
    # compter les images disponibles par espèce
    comptage = {
        cle: len(lister_images(os.path.join(BASE_DIR, cle)))
        for cle in ESPECES
    }

    # tri croissant → espèces prioritaires en haut du graphique
    tri      = sorted(comptage.items(), key=lambda x: x[1])
    labels   = [ESPECES[cle] for cle, _ in tri]
    valeurs  = [nb for _, nb in tri]
    couleurs = [
        "#E53935" if nb < SEUIL_ALERTE else "#43A047"
        for nb in valeurs
    ]

    fig, ax = plt.subplots(figsize=(10, 5))
    barres  = ax.barh(labels, valeurs, color=couleurs, height=0.5)

    # valeur à droite de chaque barre
    for barre, val in zip(barres, valeurs):
        ax.text(
            barre.get_width() + 0.5,
            barre.get_y() + barre.get_height() / 2,
            str(val),
            va="center", fontsize=10, fontweight="bold"
        )

    # ligne seuil d'alerte
    ax.axvline(SEUIL_ALERTE, color="orange", linewidth=1.8,
               linestyle="--", label=f"Seuil d'alerte ({SEUIL_ALERTE})")

    patch_ok    = mpatches.Patch(color="#43A047", label="Suffisant")
    patch_alert = mpatches.Patch(color="#E53935",
                                 label=f"Prioritaire (< {SEUIL_ALERTE})")
    ax.legend(handles=[patch_ok, patch_alert], fontsize=9)

    ax.set_xlabel("Nombre d'images disponibles")
    ax.set_title("Priorités de collecte par espèce",
                 fontsize=13, fontweight="bold")
    ax.set_xlim(0, max(valeurs) * 1.15)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    afficher_grille("flamant_rose", nb_images=12)
    afficher_distribution_tailles()
    afficher_priorites_collecte()