# Script 2 : Lit les fichiers HTML de l'étape 1 et crée le fichier CSV

# src/step2_parse.py
import os
import csv
from datetime import date
from bs4 import BeautifulSoup


def parser_polygone_montpellier(code_html, categorie=None):
    """Fonction spécifique pour extraire les boutiques du site Polygone Montpellier."""
    soup = BeautifulSoup(code_html, "html.parser")
    boutiques_html = soup.find_all("a", class_="item")
    liste_boutiques = []
    for boutique in boutiques_html:
        titre_brut = boutique.get("title")
        if titre_brut:
            nom = str(titre_brut).replace("en savoir plus sur ", "").strip()
            url = "https://www.polygone.com/" + str(boutique.get("href", "")).lstrip("/")
            liste_boutiques.append({"Nom de la boutique": nom, "Catégorie": categorie or "", "URL": url, "Téléphone": ""})
    return liste_boutiques


def parser_polygone_perpignan(code_html, categorie=None):
    """Fonction spécifique pour extraire les boutiques du site Polygone Perpignan."""
    soup = BeautifulSoup(code_html, "html.parser")

    # Construire le mapping slug → label depuis les boutons de filtre de la navbar
    mapping_categories = {}
    for btn in soup.find_all("button", attrs={"data-taxonomy": True}):
        slug = btn.get("data-taxonomy", "")
        if slug and slug != "*":
            # Prendre le premier <span> qui contient le nom (pas le span du compteur)
            span = btn.find("span")
            if span:
                mapping_categories[slug] = span.get_text(strip=True)

    conteneur_principal = soup.find("div", class_="w-grid-list")
    liste_boutiques = []
    if conteneur_principal:
        for article in conteneur_principal.find_all("article", class_="w-grid-item"):
            lien = article.find("a", class_="w-grid-item-anchor")
            if not lien:
                continue
            nom_brut = lien.get("aria-label")
            if not nom_brut:
                continue
            nom = str(nom_brut).strip()

            # La catégorie est encodée dans les classes CSS : us_portfolio_category-{slug}
            cat_trouvee = ""
            for cls in article.get("class", []):
                if cls.startswith("us_portfolio_category-") and not cls.endswith("-shopping"):
                    slug = cls.replace("us_portfolio_category-", "")
                    cat_trouvee = mapping_categories.get(slug, slug.replace("-", " ").title())
                    break

            url = str(lien.get("href", ""))
            liste_boutiques.append({"Nom de la boutique": nom, "Catégorie": cat_trouvee or categorie or "", "URL": url, "Téléphone": ""})
    else:
        print("Erreur : Le conteneur 'w-grid-list' est introuvable sur la page de Perpignan.")
    return liste_boutiques


def parser_polygone_beziers(code_html, categorie=None):
    """Fonction spécifique pour extraire les boutiques du site Polygone Beziers."""
    # Ce site a la même structure que celui de Montpellier.
    soup = BeautifulSoup(code_html, "html.parser")
    boutiques_html = soup.find_all("a", class_="item")
    liste_boutiques = []
    for boutique in boutiques_html:
        titre_brut = boutique.get("title")
        if titre_brut:
            nom = str(titre_brut).replace("en savoir plus sur ", "").strip()
            url = "https://www.polygone-beziers.com/" + str(boutique.get("href", "")).lstrip("/")
            liste_boutiques.append({"Nom de la boutique": nom, "Catégorie": categorie or "", "URL": url, "Téléphone": ""})
    return liste_boutiques


def lire_et_parser_html(chemin_html, fonction_parseur, categorie=None):
    """Lit un fichier HTML, applique une fonction de parsing et retourne la liste des boutiques."""
    if not os.path.exists(chemin_html):
        print(f"❌ Erreur : Le fichier {chemin_html} n'existe pas. Lancez step1_download.py d'abord.")
        return []
    with open(chemin_html, "r", encoding="utf-8") as fichier:
        code_html = fichier.read()
    return fonction_parseur(code_html, categorie)


def ecrire_csv(chemin_csv, liste_boutiques, centre_commercial):
    """Écrit la liste de boutiques dans un CSV avec les colonnes standardisées."""
    os.makedirs(os.path.dirname(chemin_csv), exist_ok=True)
    date_collecte = date.today().isoformat()  # format YYYY-MM-DD
    with open(chemin_csv, "w", newline="", encoding="utf-8-sig") as fichier_csv:
        writer = csv.writer(fichier_csv)
        writer.writerow(["Nom de la boutique", "Catégorie", "Téléphone", "Centre commercial", "Date de collecte"])
        for boutique in liste_boutiques:
            writer.writerow([boutique["Nom de la boutique"], boutique["Catégorie"], boutique.get("Téléphone", ""), centre_commercial, date_collecte])
    print(f"✅ {len(liste_boutiques)} boutiques écrites dans : {chemin_csv}")


def consolider_csv(dossier_csv, chemin_sortie):
    """Met à jour le fichier global par upsert : ajoute les nouvelles boutiques et met à jour les existantes."""
    print(f"\n--- Consolidation des données ---")
    nom_fichier_sortie = os.path.basename(chemin_sortie)
    COLONNES = ["Nom de la boutique", "Catégorie", "Téléphone", "Centre commercial", "Date de collecte"]

    # 1. Charger les données existantes du global comme base (si le fichier existe déjà)
    donnees_globales = {}
    if os.path.exists(chemin_sortie):
        with open(chemin_sortie, "r", encoding="utf-8-sig") as f:
            for ligne in csv.DictReader(f):
                cle = (
                    ligne.get("Nom de la boutique", "").strip().lower(),
                    ligne.get("Centre commercial", "").strip().lower(),
                )
                donnees_globales[cle] = {col: ligne.get(col, "").strip() for col in COLONNES}
    nb_avant = len(donnees_globales)

    # 2. Upsert : les données fraîchement scrapées écrasent ou complètent les données existantes
    for nom_fichier in sorted(os.listdir(dossier_csv)):
        if nom_fichier.endswith(".csv") and nom_fichier != nom_fichier_sortie:
            chemin = os.path.join(dossier_csv, nom_fichier)
            with open(chemin, "r", encoding="utf-8-sig") as f:
                for ligne in csv.DictReader(f):
                    cle = (
                        ligne.get("Nom de la boutique", "").strip().lower(),
                        ligne.get("Centre commercial", "").strip().lower(),
                    )
                    donnees_globales[cle] = {col: ligne.get(col, "").strip() for col in COLONNES}

    nb_apres = len(donnees_globales)
    nb_nouveaux = nb_apres - nb_avant

    # 3. Trier et écrire
    donnees_propres = sorted(donnees_globales.values(), key=lambda x: (x["Centre commercial"], x["Nom de la boutique"]))

    with open(chemin_sortie, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLONNES)
        writer.writeheader()
        writer.writerows(donnees_propres)

    if nb_nouveaux > 0:
        print(f"✅ Fichier global mis à jour : {nb_apres} boutiques (+{nb_nouveaux} nouvelles) → {chemin_sortie}")
    else:
        print(f"✅ Fichier global mis à jour : {nb_apres} boutiques (données rafraîchies) → {chemin_sortie}")


