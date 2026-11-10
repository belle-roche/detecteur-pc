import os
import json
import re
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

# Fichiers de données
SEEN_FILE = "seen_ads.json"
RESULTS_FILE = "results.json"

# Headers pour simuler un navigateur standard
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
}

# --- LISTE DES RÈGLES ET EXCLUSIONS ---

EXCLUDES_PC = [
    "hs", "pour pièces", "pour pieces", "défectueux", "defectueux", "pins tordus", 
    "artefact", "boîte vide", "boite vide", "5600g", "5600gt", "5500", "a320", "a520", 
    "h610", "sodimm", "ecc", "ddr3"
]

EXCLUDES_VINYL = ["cd", "dvd", "blu-ray", "poster", "rayé", "raye"]

def evaluate_ad(title, price, platform, link):
    t = title.lower()

    # Exclusions PC
    if any(ex in t for ex in EXCLUDES_PC):
        return None

    # 1. PRIORITÉ 1 : LOTS COMPLETS (AMD AM4 & INTEL LGA1700)
    lot_triggers = ["b550", "b660", "b760", "z690", "kit evolution", "kit évolution", "combo", "pack", "cm", "carte mere", "carte mère"]
    is_cpu_amd = ("5600" in t or "5600x" in t) and not ("5600g" in t or "5600gt" in t)
    is_cpu_intel = any(k in t for k in ["12400f", "12400", "12600k", "12600kf", "13400f"])

    if (is_cpu_amd or is_cpu_intel) and any(trig in t for trig in lot_triggers):
        has_ram_32 = ("32" in t or "32go" in t or "32 go" in t or "2x16" in t) and "ddr4" in t
        cat_type = "pc" if is_cpu_amd else "new_add"
        if has_ram_32:
            if price <= 190:
                return {"id": hash(link), "cat": cat_type, "title": title, "price": price, "maxPrice": 190, "platform": platform, "link": link, "isJackpot": True, "tag": "LOT 32GO", "isFav": False}
            elif price <= 220:
                return {"id": hash(link), "cat": cat_type, "title": title, "price": price, "maxPrice": 220, "platform": platform, "link": link, "isJackpot": False, "tag": "LOT 32GO", "isFav": False}
        else:
            if price <= 165:
                return {"id": hash(link), "cat": cat_type, "title": title, "price": price, "maxPrice": 165, "platform": platform, "link": link, "isJackpot": False, "tag": "LOT SANS RAM", "isFav": False}

    # 2. PRIORITÉ 2 : RAM 32 GO (Token Matching Flexible)
    has_ram_capacity = any(k in t for k in ["32go", "32 go", "2x16go", "2x16"])
    if has_ram_capacity and "ddr4" in t:
        if price <= 55:
            return {"id": hash(link), "cat": "pc", "title": title, "price": price, "maxPrice": 55, "platform": platform, "link": link, "isJackpot": price <= 45, "tag": "RAM 32GO", "isFav": False}

    # 3. PROCESSEURS SOLO
    if any(k in t for k in ["5700x", "5800x"]):
        if price <= 105:
            return {"id": hash(link), "cat": "new_add", "title": title, "price": price, "maxPrice": 105, "platform": platform, "link": link, "isJackpot": price <= 90, "tag": "CPU 8C", "isFav": False}
    elif is_cpu_amd:
        if price <= 95:
            return {"id": hash(link), "cat": "pc", "title": title, "price": price, "maxPrice": 95, "platform": platform, "link": link, "isJackpot": price <= 80, "tag": "CPU AMD", "isFav": False}
    elif is_cpu_intel:
        if price <= 95:
            return {"id": hash(link), "cat": "new_add", "title": title, "price": price, "maxPrice": 95, "platform": platform, "link": link, "isJackpot": price <= 80, "tag": "CPU INTEL", "isFav": False}

    # 4. CARTES MÈRES SOLO (DDR4 REQUISE)
    if "ddr5" not in t:
        if "x570" in t and price <= 75:
            return {"id": hash(link), "cat": "new_add", "title": title, "price": price, "maxPrice": 75, "platform": platform, "link": link, "isJackpot": price <= 65, "tag": "CM X570", "isFav": False}
        if any(k in t for k in ["b660", "b760", "z690"]) and price <= 70:
            return {"id": hash(link), "cat": "new_add", "title": title, "price": price, "maxPrice": 70, "platform": platform, "link": link, "isJackpot": price <= 60, "tag": "CM INTEL DDR4", "isFav": False}
        if "b550" in t and price <= 65:
            return {"id": hash(link), "cat": "pc", "title": title, "price": price, "maxPrice": 65, "platform": platform, "link": link, "isJackpot": price <= 55, "tag": "CM B550", "isFav": False}
        if any(k in t for k in ["b450 tomahawk", "b450-f"]) and price <= 55:
            return {"id": hash(link), "cat": "new_add", "title": title, "price": price, "maxPrice": 55, "platform": platform, "link": link, "isJackpot": price <= 45, "tag": "CM B450", "isFav": False}

    # 5. CARTES GRAPHIQUES
    gpu_rules = [
        {"kw": ["rtx 4070", "rtx 4060 ti 16go", "4060ti 16g"], "max": 315, "cat": "new_add", "tag": "RTX 4070/4060Ti"},
        {"kw": ["rx 7800 xt", "rx 7800xt"], "max": 310, "cat": "new_add", "tag": "RX 7800 XT"},
        {"kw": ["rx 6800 xt", "rx 6800xt", "rtx 3080"], "max": 300, "cat": "pc", "tag": "GPU TOP 1440P"},
        {"kw": ["rx 6800"], "max": 275, "cat": "pc", "tag": "RX 6800 16G"},
        {"kw": ["rtx 3070 ti", "rtx 3070ti"], "max": 255, "cat": "pc", "tag": "RTX 3070 Ti"},
        {"kw": ["rtx 3070"], "max": 235, "cat": "pc", "tag": "RTX 3070"},
        {"kw": ["rx 6750 xt", "rx 6750xt"], "max": 230, "cat": "new_add", "tag": "RX 6750 XT"},
        {"kw": ["rx 6700 xt", "rx 6700xt"], "max": 210, "cat": "new_add", "tag": "RX 6700 XT"},
        {"kw": ["rtx 3060 ti", "rtx 3060ti"], "max": 200, "cat": "new_add", "tag": "RTX 3060 Ti"}
    ]
    for g in gpu_rules:
        if any(k in t for k in g["kw"]):
            if price <= g["max"]:
                return {"id": hash(link), "cat": g["cat"], "title": title, "price": price, "maxPrice": g["max"], "platform": platform, "link": link, "isJackpot": price <= (g["max"] * 0.9), "tag": g["tag"], "isFav": False}

    # 6. VINYLES
    if not any(ex in t for ex in EXCLUDES_VINYL):
        vinyl_artists = ["u2", "coldplay", "imagine dragons", "dropkick murphys", "linkin park", "meteora", "hybrid theory"]
        if any(v in t for v in vinyl_artists):
            max_p = 15 if any(single in t for single in ["45t", "45 tours", "single", "numb", "in the end"]) else 22
            if price <= max_p:
                return {"id": hash(link), "cat": "vinyl", "title": title, "price": price, "maxPrice": max_p, "platform": platform, "link": link, "isJackpot": price <= (max_p * 0.75), "tag": "VINYLE", "isFav": False}

    return None

def fetch_rss_feed(url, platform_name):
    ads = []
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            soup = BeautifulSoup(xml_data, 'xml')
            items = soup.find_all('item')
            for item in items:
                title = item.title.text if item.title else ""
                link = item.link.text if item.link else ""
                description = item.description.text if item.description else ""
                
                # Extraction du prix via regex
                price_match = re.search(r'(\d+)\s*€', title + " " + description)
                if price_match:
                    price = int(price_match.group(1))
                    evaluated = evaluate_ad(title, price, platform_name, link)
                    if evaluated:
                        ads.append(evaluated)
    except Exception as e:
        print(f"Erreur lors de la récupération du flux {platform_name}: {e}")
    return ads

def main():
    print("Moteur de scraping en cours d'exécution...")

    # Chargement des données existantes
    seen_ids = set()
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            seen_ids = set(json.load(f))

    current_results = []
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            current_results = json.load(f)

    # Flux à scanner (Feeds d'annonces d'occasion)
    feeds = [
        ("https://www.leboncoin.fr/recherche?text=ryzen%205600", "Leboncoin"),
        ("https://www.leboncoin.fr/recherche?text=rtx%203070", "Leboncoin"),
        ("https://www.leboncoin.fr/recherche?text=vinyle%20u2", "Leboncoin")
    ]

    new_ads_found = []
    for feed_url, platform in feeds:
        fetched = fetch_rss_feed(feed_url, platform)
        for ad in fetched:
            if ad["id"] not in seen_ids:
                seen_ids.add(ad["id"])
                new_ads_found.append(ad)

    if new_ads_found:
        print(f"{len(new_ads_found)} nouvelle(s) annonce(s) trouvée(s) !")
        current_results = new_ads_found + current_results
        # On garde les 50 annonces les plus récentes
        current_results = current_results[:50]

        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(current_results, f, ensure_ascii=False, indent=2)

        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen_ids), f, ensure_ascii=False, indent=2)
    else:
        print("Aucune nouvelle annonce correspondant aux critères lors de ce passage.")

if __name__ == "__main__":
    main()
