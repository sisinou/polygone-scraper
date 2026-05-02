# Scraper Polygone

Collecte des boutiques des 3 centres Polygone (Montpellier, Perpignan, Béziers) avec catégorie, téléphone, centre commercial et date de collecte. Résultat exporté en CSV prêt pour Power BI j'ai d'ailleurs tester powerbi et fait quelque graphe que vous pourrez voir dans le fichier `powerBiGraph.pbix`.

 Le script prend du temps à cause de l'enrichissement téléphone : chaque boutique nécessite une requête individuelle sur sa page. avce un delai aléatoire de 0.8 à 2 secondes appliqué entre chaque requête (voir `steps/step3_enrich.py`) pour imiter un comportement humain et éviter d'être bloqué par les sites.

**282 boutiques collectées** sur 3 centres commerciaux.

---

## Installation

```bash
pip install -r requirement.txt
```

---

## Lancement

### Mode local (pages HTML déjà téléchargées)

```bash
cd src
python run_parser_local.py
```

### Mode complet (téléchargement via Chrome + parsing)

```bash
cd src
python run_scraper.py
```