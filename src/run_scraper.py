# src/run_scraper.py

import os
import re
import unicodedata

# Import fonctions de scrap
from steps.step1_download import telecharger_page
from steps.step2_parse import (
    lire_et_parser_html,
    ecrire_csv,
    consolider_csv,
    parser_polygone_montpellier,
    parser_polygone_perpignan,
    parser_polygone_beziers,
)
from steps.step3_enrich import enrichir_avec_telephone

SITES_A_SCRAPER = [
    {
        "nom": "polygone_montpellier",
        "centre_commercial": "Polygone Montpellier",
        "parser": parser_polygone_montpellier,
        # Chaque catégorie correspond à une URL dédiée sur le site
        "categories": {
            "Accessoires":         "https://www.polygone.com/shopping-1-accessoires.htm",
            "Beauté et bien-être": "https://www.polygone.com/shopping-2-beaute-et-bien-etre.htm",
            "Culture et loisirs":  "https://www.polygone.com/shopping-3-culture-et-loisirs.htm",
            "Maison":              "https://www.polygone.com/shopping-4-maison.htm",
            "Mode enfant":         "https://www.polygone.com/shopping-5-mode-enfant.htm",
            "Mode femme":          "https://www.polygone.com/shopping-6-mode-femme.htm",
            "Mode homme":          "https://www.polygone.com/shopping-7-mode-homme.htm",
            "Saveurs":             "https://www.polygone.com/shopping-8-saveurs.htm",
            "Services":            "https://www.polygone.com/shopping-9-services.htm",
        },
    },
    {
        "nom": "polygone_perpignan",
        "centre_commercial": "Polygone Perpignan",
        "url": "https://www.ccpolygone-perpignan.fr/shopping/",
        "parser": parser_polygone_perpignan,
        # Pas de découpage par catégorie identifié sur ce site
    },
    {
        "nom": "polygone_beziers",
        "centre_commercial": "Polygone Béziers",
        "parser": parser_polygone_beziers,
        # URLs réelles du site Polygone Béziers (numéros 10-20, noms différents de Montpellier)
        "categories": {
            "Accessoires":         "https://www.polygone-beziers.com/shopping-10-accessoires.htm",
            "Alimentaire":         "https://www.polygone-beziers.com/shopping-11-alimentaire.htm",
            "Beauté et bien-être": "https://www.polygone-beziers.com/shopping-12-beaute-bien-etre.htm",
            "Bébé/Enfant":         "https://www.polygone-beziers.com/shopping-13-bebe-enfant.htm",
            "Culture et loisirs":  "https://www.polygone-beziers.com/shopping-14-culture-loisirs.htm",
            "Maison":              "https://www.polygone-beziers.com/shopping-15-maison.htm",
            "Mode femme":          "https://www.polygone-beziers.com/shopping-16-mode-femme.htm",
            "Mode homme":          "https://www.polygone-beziers.com/shopping-17-mode-homme.htm",
            "Multimédia":          "https://www.polygone-beziers.com/shopping-18-multimedia.htm",
            "Saveurs":             "https://www.polygone-beziers.com/shopping-19-saveurs.htm",
            "Services":            "https://www.polygone-beziers.com/shopping-20-services.htm",
        },
    },
]


def slugify(texte):
    """Convertit un texte en slug ASCII utilisable comme partie de nom de fichier."""
    texte = unicodedata.normalize("NFKD", texte)
    texte = texte.encode("ascii", "ignore").decode("ascii")
    texte = texte.lower()
    texte = re.sub(r"[^a-z0-9]+", "_", texte)
    return texte.strip("_")


def main():
    print("--- Lancement du scraping de tous les centres ---")
    dossier_csv = os.path.join("data", "2_resultats_csv")

    for site in SITES_A_SCRAPER:
        print(f"\n--- Traitement de : {site['nom']} ---")
        toutes_boutiques = []

        if "categories" in site:
            # Télécharger et parser une page par catégorie — pas de pagination nécessaire
            # car chaque page de catégorie contient déjà toutes les boutiques du filtre
            for cat_nom, cat_url in site["categories"].items():
                slug_cat = slugify(cat_nom)
                chemin_html = os.path.join("data", "1_pages_html", f"{site['nom']}_{slug_cat}.html")
                print(f"  > Catégorie : {cat_nom}")
                if telecharger_page(cat_url, chemin_html, pagination_config=None):
                    boutiques = lire_et_parser_html(chemin_html, site["parser"], categorie=cat_nom)
                    toutes_boutiques.extend(boutiques)
        else:
            # Page unique sans filtrage par catégorie
            chemin_html = os.path.join("data", "1_pages_html", f"{site['nom']}.html")
            if telecharger_page(site["url"], chemin_html, pagination_config=None):
                boutiques = lire_et_parser_html(chemin_html, site["parser"], categorie=None)
                toutes_boutiques.extend(boutiques)

        if toutes_boutiques:
            print(f"  Enrichissement téléphone...")
            enrichir_avec_telephone(toutes_boutiques)
            chemin_csv = os.path.join(dossier_csv, f"boutiques_{site['nom']}.csv")
            ecrire_csv(chemin_csv, toutes_boutiques, site["centre_commercial"])

    # Consolidation finale : un seul fichier CSV global prêt pour Power BI
    chemin_global = os.path.join(dossier_csv, "boutiques_global.csv")
    consolider_csv(dossier_csv, chemin_global)
    print("\n--- Scraping terminé ---")


if __name__ == "__main__":
    main()