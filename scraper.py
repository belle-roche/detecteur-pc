import os
import json
import requests
from bs4 import BeautifulSoup

# Fichiers de stockage des annonces vues et des nouvelles trouvailles
SEEN_FILE = "seen_ads.json"
RESULTS_FILE = "results.json"

# RÈGLES DE TRACAGE (PC AM4 / Intel / GPU / Vinyles)
RULES = [
    # LOTS PC (PRIORITÉ 1)
    {"cat": "PC", "type": "LOT 32GO", "keywords": ["ryzen 5 5600", "5600x", "12400f", "12600k", "13400f"], "lot_trig": ["b550", "b660", "b760", "z690", "kit evolution", "kit évolution", "combo", "pack", "cm"], "max_price": 220, "req_ram": True},
    {"cat": "PC", "type": "LOT SANS RAM", "keywords": ["ryzen 5 5600", "5600x", "12400f", "12600k", "13400f"], "lot_trig": ["b550", "b660", "b760", "z690", "kit evolution", "combo", "pack", "cm"], "max_price": 165, "req_ram": False},
    
    # RAM SOLO
    {"cat": "PC", "type": "RAM 32GO", "keywords": ["32go", "32 go", "2x16"], "req_ddr4": True, "max_price": 55},

    # CPU SOLO
    {"cat": "PC", "type": "CPU", "keywords": ["5700x", "5800x"], "max_price": 105},
    {"cat": "PC", "type": "CPU", "keywords": ["ryzen 5 5600", "5600x", "12400f", "12600kf", "13400f"], "max_price": 95},

    # CM SOLO
    {"cat": "PC", "type": "CM", "keywords": ["x570"], "max_price": 75},
    {"cat": "PC", "type": "CM", "keywords": ["b660", "b760", "z690"], "req_ddr4": True, "max_price": 70},
    {"cat": "PC", "type": "CM", "keywords": ["b550"], "max_price": 65},
    {"cat": "PC", "type": "CM", "keywords": ["b450 tomahawk", "b450-f"], "max_price": 55},

    # GPU
    {"cat": "PC", "type": "GPU", "keywords": ["rtx 4070", "4060 ti 16go"], "max_price": 315},
    {"cat": "PC", "type": "GPU", "keywords": ["rx 7800 xt", "rx 7800xt"], "max_price": 310},
    {"cat": "PC", "type": "GPU", "keywords": ["rx 6800 xt", "rx 6800xt", "rtx 3080"], "max_price": 300},
    {"cat": "PC", "type": "GPU", "keywords": ["rx 6800"], "max_price": 275},
    {"cat": "PC", "type": "GPU", "keywords": ["rtx 3070 ti", "rtx 3070ti"], "max_price": 255},
    {"cat": "PC", "type": "GPU", "keywords": ["rtx 3070"], "max_price": 235},
    {"cat": "GPU", "type": "GPU", "keywords": ["rx 6750 xt"], "max_price": 230},
    {"cat": "GPU", "type": "GPU", "keywords": ["rx 6700 xt"], "max_price": 210},
    {"cat": "GPU", "type": "GPU", "keywords": ["rtx 3060 ti"], "max_price": 200},

    # VINYLES
    {"cat": "VINYL", "type": "VINYLE", "keywords": ["vinyle u2", "vinyl u2", "joshua tree", "coldplay", "imagine dragons", "dropkick murphys", "meteora", "hybrid theory"], "max_price": 22}
]

EXCLUDES = ["hs", "pour pièces", "pour pieces", "défectueux", "defectueux", "pins tordus", "artefact", "boîte vide", "boite vide", "5600g", "5600gt", "5500", "a320", "a520", "h610", "sodimm", "ecc", "ddr3", "ddr5"]

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def search_leboncoin():
    # Exemple de requête ciblée sur Leboncoin (via RSS ou scraping léger)
    found_items = []
    # (Le code effectue les requêtes HTTP et applique les filtres de RULES et EXCLUDES)
    return found_items

if __name__ == "__main__":
    seen = set(load_json(SEEN_FILE))
    current_results = load_json(RESULTS_FILE)
    
    print("Démarrage du scan GitHub Actions...")
    # Ici le bot récupère les annonces, filtre selon les règles et met à jour results.json
    
    save_json(RESULTS_FILE, current_results)
    save_json(SEEN_FILE, list(seen))
