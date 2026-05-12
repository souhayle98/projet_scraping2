import os
import time
import random
import logging
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from PIL import Image #bibiolteque pillow
from io import BytesIO
import json

BIRDS = [
    "hibou grand duc",
    "flamant rose",
    "martin pecheur",
    "cygne tubercule",
    "pic vert"
]

BASE_DIR      = "data/brutes/"
LOG_FILE      = "rapports/scraping.log"
NB_IMAGES     = 100
DELAI_MIN     = 1.0
DELAI_MAX     = 3.0
TIMEOUT       = 10
TAILLE_MIN_KO = 5

#gestion systeme de log et retourner un logger
def configuer_logger():
    try:
        os.makedirs("rapports",exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers = [
                logging.FileHandler(LOG_FILE,encoding="utf-8"),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger("scraper")
    except Exception as e :
        print(e)

logger = configuer_logger()

"""
Configuration du navigateur Chrome pour Selenium.

Le driver est l’objet qui contrôle le navigateur.
Les options utilisées permettent :
- d’exécuter Chrome sans interface graphique (--headless)
- de désactiver le sandbox de sécurité (--no-sandbox)
- d’éviter certains problèmes mémoire (--disable-dev-shm-usage)
- de définir une taille de fenêtre stable (--window-size)

Ces paramètres rendent le scraping plus rapide et plus stable.
"""

def creer_driver():
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        return webdriver.Chrome(options=options)
    except Exception as e:
        print(e)


 # exemple de la fonction : dataset\Flamant_rose       
def creer_dossier(bird):
    try:
        chemin = os.path.join(BASE_DIR,bird.replace(" ","_"))
        os.makedirs(chemin,exist_ok=True)
        return chemin
    except Exception as e :
        print(e)
#generer un nombre decimal pour ne surcharge pas le serveur
def attendre():
    try:
        time.sleep(random.uniform(DELAI_MIN,DELAI_MAX))
    except Exception as e :
        print(e)

def charger_page_bing(driver,bird):
    try:
        query = bird.replace(" ","+")
        url = f"https://www.bing.com/images/search?q={query}&count=150"
        driver.get(url)
        attendre()
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            attendre()
    except Exception as e:
        print(e)

def extraire_urls(driver):
    try:
        soup = BeautifulSoup(driver.page_source,"html.parser")
        urls = []
        for tag in soup.find_all("a",class_="iusc"):
            try:
                # transforme a un dictionnaire 
                meta = json.loads(tag.get("m","{}"))
                murl = meta.get("murl","")
                if murl:
                    urls.append(murl)
            except Exception:
                continue
        return list(set(urls))
    except Exception as e :
        print(e)


#1byte = 1octet
#1kb = 1024bytes
#1ko = 1024bytes
def telecharger_image(url,dossier,index):
    # le site peuvent echouer
    for tentative in range(1,4):
        try:
            attendre()
            reponse = requests.get(url,timeout=TIMEOUT)
            #se lance seulement s il y a erreur
            reponse.raise_for_status()

            contenu = reponse.content
            if (len(contenu)) / 1024 < TAILLE_MIN_KO:
                logger.warning("Trop petite : %s", url[:70])
                return False

            #transforme contenu du bytes vers un fichier 
            #en memoire car Image a besoin de ca
            #BytesIO : simule un fichier sans l'ecrire 
            #dans le disque dans un fichier virtuel
            img = Image.open(BytesIO(contenu))
            img.verify()
            # image soit png , jpg , webp
            ext = (img.format or "jpg").lower().replace("jpeg","jpg")
            #exemple : dataset/Flamant_rose/image_0005.jpg
            chemin = os.path.join(dossier,f"image_{index:04d}.{ext}")
            with open(chemin,"wb") as f:
                f.write(contenu)
                return True

        except requests.exceptions.Timeout:
            logger.warning("Timeout tentative %d/3 : %s", tentative, url[:70])

        except requests.exceptions.HTTPError as e:
            logger.error("HTTP %s : %s", e.response.status_code, url[:70])
            return False

        except requests.exceptions.ConnectionError:
            logger.warning("Connexion échouée tentative %d/3 : %s", tentative, url[:70])

        except Exception as e:
            logger.error("Erreur : %s | %s", e, url[:70])
            return False

        time.sleep(1.5)
    logger.error("ECHEC après 3 tentatives : %s", url[:70])
    return False

def scraper_bird(driver,bird):
    logger.info("=== Début : %s ===", bird)

    dossier = creer_dossier(bird)
    charger_page_bing(driver,bird)
    urls=extraire_urls(driver)
    logger.info("%d URLs trouvées pour %s", len(urls), bird)

    succes = 0
    for i , url in enumerate(urls):
        if succes >= NB_IMAGES:
            break
        if telecharger_image(url,dossier,i):
            succes+=1
    logger.info("=== Fin : %s → %d/%d images ===\n", bird, succes, NB_IMAGES)

def main():
    driver = creer_driver()
    try:
        for bird in BIRDS:
            scraper_bird(driver,bird)
    finally:
        driver.quit()
        logger.info("Scraping terminé")
if __name__ == "__main__":
    main()







