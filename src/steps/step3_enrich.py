# src/step3_enrich.py
# Étape 3 : enrichit les boutiques avec le numéro de téléphone
# en téléchargeant chaque page individuelle (urllib, sans Selenium).

import re
import time
import random
import urllib.request
from bs4 import BeautifulSoup

_PATTERN_TELEPHONE = re.compile(r"0[1-9](?:[\s.\-]?\d{2}){4}")


def telecharger_html_simple(url):
    """Télécharge une page statique avec urllib (rapide, sans Chrome)."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"⚠️  Erreur : {e}")
        return ""


def extraire_telephone(code_html):
    """Extrait le premier numéro de téléphone français trouvé dans le HTML."""
    if not code_html:
        return ""
    texte = BeautifulSoup(code_html, "html.parser").get_text()
    m = _PATTERN_TELEPHONE.search(texte)
    if m:
        chiffres = re.sub(r"[^\d]", "", m.group())
        return " ".join(chiffres[i:i + 2] for i in range(0, 10, 2))
    return ""


def enrichir_avec_telephone(liste_boutiques):
    """
    Pour chaque boutique ayant une URL, télécharge sa page individuelle
    et extrait le numéro de téléphone. Modifie la liste en place et la retourne.
    """
    avec_url = [b for b in liste_boutiques if b.get("URL")]
    total = len(avec_url)
    if total == 0:
        return liste_boutiques

    print(f"  Enrichissement téléphone ({total} boutiques)...")
    traite = 0
    for boutique in liste_boutiques:
        url = boutique.get("URL", "")
        if not url:
            boutique.setdefault("Téléphone", "")
            continue
        traite += 1
        print(f"    [{traite}/{total}] {boutique['Nom de la boutique']}...", end=" ", flush=True)
        html = telecharger_html_simple(url)
        tel = extraire_telephone(html)
        boutique["Téléphone"] = tel
        print(tel if tel else "(non trouvé)")
        # Délai aléatoire façon humain pour éviter les blocages
        time.sleep(random.uniform(0.8, 2.0))

    return liste_boutiques
