import csv

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

ecoles = []
with open("data/liens_fiches_ecoles.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ecoles.append(row["url"])

headers = {"User-Agent": "Mozilla/5.0"}

avis_list = []

# Progress bar for schools
for base_url in tqdm(ecoles, desc="Scraping schools", unit="school"):
    page = 1
    page_pbar = tqdm(desc=f"Pages for {base_url}", unit="page", leave=False)
    
    while True:
        url = f"{base_url}?page={page}#avis-authentifies"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        avis_divs = soup.find_all(
            "div",
            class_="tw-w-full tw-mb-2 tw-border-solid tw-border tw-border-gray-500 tw-rounded-large",
        )

        if not avis_divs:
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

            ecole = base_url.split("/")[-1].replace(".html", "").replace("-", " ").title()

            avis_list.append(
                {
                    'ecole': ecole,
                    "auteur": auteur,
                    "date": date,
                    "note": note,
                    "contenu": contenu,
                    "url": base_url,
                }
            )

        if len(avis_divs) < 20:
            break

        page += 1
        page_pbar.update(1)
        page_pbar.set_postfix({"Total reviews": len(avis_list)})
    
    page_pbar.close()

print(f"Total avis collectés : {len(avis_list)}")

df = pd.DataFrame(avis_list)
df.to_csv("textual_dataset.csv", index=False, encoding='utf-8-sig')

print("Scraping terminé : textual_dataset.csv créé.")
