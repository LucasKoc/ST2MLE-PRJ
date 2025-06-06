import requests
from bs4 import BeautifulSoup
import pandas as pd

# Liste des écoles : chaque tuple contient (nom_ecole, url de base)
ecoles = [
    ("HETIC", "https://www.letudiant.fr/etudes/annuaire-enseignement-superieur/etablissement/etablissement-hetic-la-grande-ecole-du-web-7868.html"),
    ("ESIEA", "https://www.letudiant.fr/etudes/annuaire-enseignement-superieur/etablissement/etablissement-ecole-d-ingenieurs-du-monde-numerique-9712.html"),
    ("CESI-ROUEN", "https://www.letudiant.fr/etudes/annuaire-enseignement-superieur/etablissement/etablissement-ecole-d-ingenieurs-du-cesi-centre-de-rouen-mont-saint-aignan-70411.html"),
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

MAX_PAGES = 1000  # Limite max de pages à scrapper par école

avis_list = []

for ecole, base_url in ecoles:
    print(f"Début du scraping pour {ecole}")
    page = 1
    while page <= MAX_PAGES:
        url = f"{base_url}?page={page}#avis-authentifies"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        avis_divs = soup.find_all("div", class_="tw-w-full tw-mb-2 tw-border-solid tw-border tw-border-gray-500 tw-rounded-large")

        if not avis_divs:
            print(f"Aucun avis trouvé à la page {page} pour {ecole}, arrêt du scraping de cette école.")
            break

        for avis in avis_divs:
            auteur_date_p = avis.select_one("p.tw-text-sans")
            if auteur_date_p:
                auteur_span = auteur_date_p.select_one("span.tw-font-medium")
                auteur = auteur_span.get_text(strip=True) if auteur_span else ""
                full_text = auteur_date_p.get_text(strip=True)
                date = full_text.replace(auteur, "").replace("a publié un avis le", "").strip()
            else:
                auteur, date = "", ""

            note_span = avis.select_one("span.tw-text-primary.tw-font-heading")
            note = note_span.get_text(strip=True).replace(",", ".") if note_span else ""

            contenu_p = avis.select_one("p.tw-break-words")
            contenu = contenu_p.get_text(strip=True) if contenu_p else ""

            avis_list.append({
                "ecole": ecole,
                "contenu": contenu
                "auteur": auteur,
                "date": date,
                "note": note,
                "url": base_url,  
            })

        print(f"Page {page} traitée avec {len(avis_divs)} avis pour {ecole}.")

        if len(avis_divs) < 20:
            print(f"Moins de 20 avis à la page {page} pour {ecole}, fin du scraping de cette école.")
            break

        page += 1
    else:
        print(f"Limite max de pages ({MAX_PAGES}) atteinte pour {ecole}, arrêt du scraping de cette école.")

print(f"Total avis collectés : {len(avis_list)}")

df = pd.DataFrame(avis_list)
df.to_csv("avis_toutes_ecoles.csv", index=False, encoding='utf-8-sig')

print("Scraping terminé : avis_toutes_ecoles.csv créé.")
