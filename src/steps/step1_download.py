import os
import time
from .utils import initialiser_navigateur
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def telecharger_page(url, chemin_sauvegarde, pagination_config=None, cache_jours=7):
    """Télécharge le code source d'une URL. Gère la pagination si une configuration est fournie.
    Si le fichier HTML existe et a moins de cache_jours jours, il est réutilisé sans relancer Chrome.
    Mettre cache_jours=0 pour forcer le téléchargement."""
    # Vérification du cache
    if cache_jours > 0 and os.path.exists(chemin_sauvegarde):
        age_jours = (time.time() - os.path.getmtime(chemin_sauvegarde)) / 86400
        if age_jours < cache_jours:
            print(f"  Cache valide ({age_jours:.1f}j < {cache_jours}j) → {chemin_sauvegarde}")
            return True

    print(f"Téléchargement de {url}...")
    driver = initialiser_navigateur()
    try:
        driver.get(url)
        # 1. Gérer les cookies pour libérer l'écran
        try:
            bouton_cookies = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "tarteaucitronAllAllowed"))
            )
            bouton_cookies.click()
            print("Cookies acceptés.")
            time.sleep(1) # Petite pause pour laisser l'animation de la bannière se terminer
        except TimeoutException:
            print("Aucun bandeau de cookies détecté.")

        final_html = ""
        if pagination_config:
            print("Gestion de la pagination activée.")
            all_items_html_parts = []
            page_count = 1
            
            while True:
                print(f"Traitement de la page {page_count}...")
                # Attendre que le conteneur des articles soit présent
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, pagination_config["items_container_selector"]))
                )
                
                # Extraire le HTML du conteneur des articles
                items_container = driver.find_element(By.CSS_SELECTOR, pagination_config["items_container_selector"])
                all_items_html_parts.append(items_container.get_attribute('innerHTML'))
                
                # Chercher et cliquer sur le bouton "suivant"
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, pagination_config["next_button_selector"])
                    # Un clic Javascript est parfois plus fiable
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(3) # Attendre que la nouvelle page se charge
                    page_count += 1
                except NoSuchElementException:
                    print("C'est la dernière page.")
                    break # Sortir de la boucle s'il n'y a pas de bouton "suivant"
            
            # Construire un fichier HTML final contenant tous les articles de toutes les pages
            items_wrapper_html = "".join(all_items_html_parts)
            final_html = f'<html><body><div class="items">{items_wrapper_html}</div></body></html>'
            print(f"Total de {len(all_items_html_parts)} pages de boutiques agrégées.")

        else:
            print("Pas de pagination à gérer.")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
            time.sleep(2)
            final_html = driver.page_source
        
        # Sauvegarde du HTML final dans le dossier intermédiaire
        # S'assurer que le dossier de destination existe
        os.makedirs(os.path.dirname(chemin_sauvegarde), exist_ok=True)
        with open(chemin_sauvegarde, "w", encoding="utf-8") as fichier:
            fichier.write(final_html)
            
        print(f"✅ Succès ! Le code source a été sauvegardé dans : {chemin_sauvegarde}")
        return True

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        return False
        
    finally:
        driver.quit()