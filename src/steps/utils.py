from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

def initialiser_navigateur():
    """Configure et lance le navigateur Chrome."""
    options = Options()
    # options.add_argument("--headless=new") # Décommentez cette ligne pour que le navigateur s'exécute en arrière-plan, sans fenêtre visible.
    # On définit une grande taille d'écran pour être sûr de voir tous les éléments
    options.add_argument("--window-size=1920,1080")
    
    driver = Chrome(options=options)
    return driver