"""
File to scrape data from a website and save it to a CSV file.
"""

import csv
import re
import time
from urllib.parse import urldefrag, urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.letudiant.fr"
RANKING = f"{BASE}/classements/classement-des-ecoles-d-ingenieurs.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
}


class ScrappingLetudiant:
    """
    Class to scrape data from a website and save it to a CSV file.
    """

    def __init__(self):
        self.url_ranking_page = "https://www.letudiant.fr/classements/classement-des-ecoles-d-ingenieurs.html"

    def extract_rows(self, html: str) -> list[tuple[str, str]]:
        soup = BeautifulSoup(html, "lxml")
        rows = []

        # "Voir la fiche complète"
        for btn in soup.find_all(
            "a",
            href=True,
            string=lambda t: t and "Voir la fiche complète".lower() in t.lower(),
        ):
            url = urldefrag(urljoin(BASE, btn["href"])).url
            # ancre précédente avec le même href = nom de l'école
            name_a = btn.find_previous("a", href=re.compile(re.escape(btn["href"])))
            if name_a:
                school = name_a.get_text(" ", strip=True)
                rows.append((school, url))
        return rows

    def extract_ranking_page(self) -> list[tuple[str, str]]:
        """
        Extracts the ranking page from the website.
        """
        all_rows = []
        for page in range(1, 10):
            url = RANKING if page == 1 else f"{RANKING}?page={page}"
            html = requests.get(url, headers=HEADERS, timeout=10).text
            page_rows = self.extract_rows(html)
            all_rows.extend(page_rows)
            print(f"Page {page} -> +{len(page_rows)} lignes (total {len(all_rows)})")
            time.sleep(1)

        print(f"Total final : {len(all_rows)} liens")
        with open("liens_fiches_ecoles.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "url"])
            writer.writerows(all_rows)

        return all_rows


if __name__ == "__main__":
    scrapping = ScrappingLetudiant()
    rows = scrapping.extract_ranking_page()

    """schools = pd.DataFrame([row[1] for row in rows], columns=["url"])
    schools["duplicated"] = schools.duplicated()
    print(schools)"""
