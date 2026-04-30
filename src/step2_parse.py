# Script 2 : Lit les fichiers HTML de l'étape 1 et crée le fichier CSV

# src/step2_parse.py
import os
import csv
from bs4 import BeautifulSoup

def parser_polygone_montpellier(code_html):
    """Fonction spécifique pour extraire les boutiques du site Polygone Montpellier."""
    soup = BeautifulSoup(code_html, "html.parser")
    boutiques_html = soup.find_all("a", class_="item")
    liste_boutiques = []
    for boutique in boutiques_html:
        titre_brut = boutique.get("title")
        if titre_brut:
            nom = titre_brut.replace("en savoir plus sur ", "").strip()
            liste_boutiques.append([nom])
    return liste_boutiques

def parser_polygone_perpignan(code_html):
    """Fonction spécifique pour extraire les boutiques du site Polygone Perpignan."""
    soup = BeautifulSoup(code_html, "html.parser")
    conteneur_principal = soup.find("div", class_="w-grid-list")
    liste_boutiques = []
    if conteneur_principal:
        boutiques_html = conteneur_principal.find_all("a", class_="w-grid-item-anchor")
        for boutique in boutiques_html:
            nom_brut = boutique.get("aria-label")
            
            if nom_brut:
                nom = nom_brut.strip()
                liste_boutiques.append([nom])
    else:
        print("Erreur : Le conteneur 'w-grid-list' est introuvable sur la page de Perpignan.")  
    return liste_boutiques

def parser_polygone_beziers(code_html):
    """Fonction spécifique pour extraire les boutiques du site Polygone Beziers."""
    # Ce site a la même structure que celui de Montpellier.
    soup = BeautifulSoup(code_html, "html.parser")
    boutiques_html = soup.find_all("a", class_="item")
    liste_boutiques = []
    for boutique in boutiques_html:
        titre_brut = boutique.get("title")
        if titre_brut:
            nom = titre_brut.replace("en savoir plus sur ", "").strip()
            liste_boutiques.append([nom])
    return liste_boutiques

def extraire_donnees(chemin_html, chemin_csv, fonction_parseur):
    """Lit un fichier HTML, applique une fonction de parsing et sauvegarde en CSV."""
    print(f"Étape 2 : Extraction de {chemin_html} vers {chemin_csv}...")

    if not os.path.exists(chemin_html):
        print(f"❌ Erreur : Le fichier {chemin_html} n'existe pas. Lancez step1_download.py d'abord.")
        return
    with open(chemin_html, "r", encoding="utf-8") as fichier:
        code_html = fichier.read()
    # Appeler la fonction de parsing spécifique fournie en argument
    liste_donnees = fonction_parseur(code_html) 
    os.makedirs(os.path.dirname(chemin_csv), exist_ok=True)
    with open(chemin_csv, "w", newline="", encoding="utf-8") as fichier_csv:
        writer = csv.writer(fichier_csv)
        writer.writerow(["Nom de la boutique"])
        writer.writerows(liste_donnees)
    print(f"✅ Succès ! {len(liste_donnees)} boutiques extraites dans : {chemin_csv}")

def main():
    """Exemple d'exécution pour le site Polygone."""
    print("Étape 2 : Lancement de l'extraction pour Polygone (exemple)")
    chemin_html_polygone_montpellier = "data/1_pages_html/polygone_montpellier.html"
    chemin_csv_polygone_montpellier = "data/2_resultats_csv/boutiques_polygone_montpellier.csv"
    
    # On appelle la fonction générique en lui spécifiant le parser pour Polygone Montpellier
    extraire_donnees(chemin_html_polygone_montpellier, chemin_csv_polygone_montpellier, parser_polygone_montpellier)
if __name__ == "__main__":
    main()