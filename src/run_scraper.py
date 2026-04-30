# src/run_scraper.py

# Import fonction de scrap
from step1_download import telecharger_page
from step2_parse import extraire_donnees, parser_polygone_montpellier, parser_polygone_perpignan, parser_polygone_beziers

SITES_A_SCRAPER = [
    {
        "nom": "polygone_montpellier",
        "url": "https://www.polygone.com/shopping.htm",
        "parser": parser_polygone_montpellier,
        "pagination": {
            "next_button_selector": "div.pagination a.next",
            "items_container_selector": "div.items" 
        }
    },
    {
         "nom": "polygone_perpignan",
         "url": "https://www.ccpolygone-perpignan.fr/shopping/",
         "parser": parser_polygone_perpignan,
    },
    {
         "nom": "polygone_beziers",
         "url": "https://www.polygone-beziers.com/shopping.htm",
         "parser": parser_polygone_beziers,
         "pagination": {
            "next_button_selector": "div.pagination a.next",
            "items_container_selector": "div.items" 
        }
    },

]

def main():
    print("--- Lancement du scraping de tous les centres ---")
    for site in SITES_A_SCRAPER:
        print(f"\n--- Traitement de : {site['nom']} ---")
        
        chemin_html = f"data/1_pages_html/{site['nom']}.html"
        chemin_csv = f"data/2_resultats_csv/boutiques_{site['nom']}.csv"
        
        # On récupère la configuration de pagination si elle existe
        pagination_config = site.get("pagination", None)
        
        if telecharger_page(site["url"], chemin_html, pagination_config=pagination_config):
            extraire_donnees(chemin_html, chemin_csv, site["parser"])

if __name__ == "__main__":
    main()