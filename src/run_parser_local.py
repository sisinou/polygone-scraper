# src/run_parser_local.py
# Parse les fichiers HTML déjà téléchargés SANS relancer Selenium.
# Utile pour régénérer les CSV après une modification des parseurs.

import os

from step2_parse import (
    lire_et_parser_html,
    ecrire_csv,
    consolider_csv,
    parser_polygone_montpellier,
    parser_polygone_perpignan,
    parser_polygone_beziers,
)
from step3_enrich import enrichir_avec_telephone

DOSSIER_HTML = os.path.join("data", "1_pages_html")
DOSSIER_CSV  = os.path.join("data", "2_resultats_csv")

# Même configuration que run_scraper.py mais sans URLs — uniquement les fichiers locaux
SITES_A_PARSER = [
    {
        "nom": "polygone_montpellier",
        "centre_commercial": "Polygone Montpellier",
        "parser": parser_polygone_montpellier,
        "categories": {
            "Accessoires":         "polygone_montpellier_accessoires.html",
            "Beauté et bien-être": "polygone_montpellier_beaute_et_bien_etre.html",
            "Culture et loisirs":  "polygone_montpellier_culture_et_loisirs.html",
            "Maison":              "polygone_montpellier_maison.html",
            "Mode enfant":         "polygone_montpellier_mode_enfant.html",
            "Mode femme":          "polygone_montpellier_mode_femme.html",
            "Mode homme":          "polygone_montpellier_mode_homme.html",
            "Saveurs":             "polygone_montpellier_saveurs.html",
            "Services":            "polygone_montpellier_services.html",
        },
    },
    {
        "nom": "polygone_perpignan",
        "centre_commercial": "Polygone Perpignan",
        "parser": parser_polygone_perpignan,
        "fichier": "polygone_perpignan.html",
    },
    {
        "nom": "polygone_beziers",
        "centre_commercial": "Polygone Béziers",
        "parser": parser_polygone_beziers,
        "categories": {
            "Accessoires":         "polygone_beziers_accessoires.html",
            "Alimentaire":         "polygone_beziers_alimentaire.html",
            "Beauté et bien-être": "polygone_beziers_beaute_et_bien_etre.html",
            "Bébé/Enfant":         "polygone_beziers_bebe_enfant.html",
            "Culture et loisirs":  "polygone_beziers_culture_et_loisirs.html",
            "Maison":              "polygone_beziers_maison.html",
            "Mode femme":          "polygone_beziers_mode_femme.html",
            "Mode homme":          "polygone_beziers_mode_homme.html",
            "Multimédia":          "polygone_beziers_multimedia.html",
            "Saveurs":             "polygone_beziers_saveurs.html",
            "Services":            "polygone_beziers_services.html",
        },
    },
]


def main():
    print("--- Parsing local (sans téléchargement) ---\n")

    for site in SITES_A_PARSER:
        print(f"--- {site['centre_commercial']} ---")
        toutes_boutiques = []

        if "categories" in site:
            for cat_nom, nom_fichier in site["categories"].items():
                chemin_html = os.path.join(DOSSIER_HTML, nom_fichier)
                if not os.path.exists(chemin_html):
                    print(f"  ⚠️  Fichier manquant (ignoré) : {nom_fichier}")
                    continue
                boutiques = lire_et_parser_html(chemin_html, site["parser"], categorie=cat_nom)
                print(f"  {cat_nom} -> {len(boutiques)} boutiques")
                toutes_boutiques.extend(boutiques)
        else:
            chemin_html = os.path.join(DOSSIER_HTML, site["fichier"])
            if not os.path.exists(chemin_html):
                print(f"  ⚠️  Fichier manquant (ignoré) : {site['fichier']}")
                continue
            boutiques = lire_et_parser_html(chemin_html, site["parser"])
            print(f"  Page unique → {len(boutiques)} boutiques")
            toutes_boutiques.extend(boutiques)

        if toutes_boutiques:
            enrichir_avec_telephone(toutes_boutiques)
            chemin_csv = os.path.join(DOSSIER_CSV, f"boutiques_{site['nom']}.csv")
            ecrire_csv(chemin_csv, toutes_boutiques, site["centre_commercial"])
        print()

    chemin_global = os.path.join(DOSSIER_CSV, "boutiques_global.csv")
    consolider_csv(DOSSIER_CSV, chemin_global)
    print("\n--- Terminé ---")


if __name__ == "__main__":
    main()
