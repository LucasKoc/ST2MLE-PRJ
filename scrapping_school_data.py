'''!pip install selenium
!apt-get update # pour les dépendances de Chrome
!apt install chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin'''

import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from IPython.display import display

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.binary_location = "/usr/bin/chromium-browser"

urls = {
    "polytechnique": "https://www.letudiant.fr/etudes/annuaire-enseignement-superieur/etablissement/etablissement-ecole-polytechnique-7681.html#classement-des-ecoles-d-ingenieurs",
    "efrei": "https://www.letudiant.fr/fiches/etudes/fiche/efrei-ecole-d-ingenieurs.html"
}

thematic_ids = [425, 426, 427, 429, 430, 431]

data = []
driver = webdriver.Chrome(options=chrome_options)

for school_key, url in urls.items():
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    for thematic_id in thematic_ids:
        # Recherche des divs par suffixe dans l'id
        header_div = soup.find("div", id=lambda x: x and x.endswith(f"{thematic_id}-header"))
        titre = header_div.find("h2").text.strip() if header_div else f"Thématique {thematic_id}"

        thematic_div = soup.find("div", id=lambda x: x and x.endswith(f"{thematic_id}-criteria"))
        if not thematic_div:
            print(f"[!] Section {thematic_id} introuvable pour {school_key}.")
            continue

        rows = thematic_div.find_all("div", class_="criterion-row")
        for row in rows:
            try:
                label = row.find("span", class_="tw-font-medium").get_text(strip=True)
                score_div = row.find("div", class_="tw-bg-ranking-green")
                score = score_div.get_text(strip=True) if score_div else "N/A"
                note_div = row.find("div", class_="tw-text-right")
                note = note_div.get_text(strip=True) if note_div else "N/A"

                data.append({
                    "École": school_key,
                    "Thématique": titre,
                    "ID Thématique": thematic_id,
                    "Critère": label,
                    "Score /10": score,
                    "Note brute": note
                })
            except Exception as e:
                print(f"⚠️ Problème ligne ({school_key}, thématique {thematic_id}): {e}")

driver.quit()

# Écriture dans le CSV
csv_filename = "ecoles_thematiques.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["École", "Thématique", "ID Thématique", "Critère", "Score /10", "Note brute"])
    writer.writeheader()
    writer.writerows(data)

print(f"✅ Fichier CSV généré : {csv_filename}")

# Création du DataFrame
df = pd.DataFrame(data)

# Sauvegarde en CSV
df.to_csv("classements_letudiant.csv", index=False, encoding="utf-8")

display(df)