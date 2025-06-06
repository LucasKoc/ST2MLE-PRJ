"""
File to scrape data from a website and save it to a CSV file.
"""
import requests, time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://www.letudiant.fr"
RANKING = f"{BASE}/classements/classement-des-ecoles-d-ingenieurs.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"}


class ScrappingLetudiant:
    """
    Class to scrape data from a website and save it to a CSV file.
    """

    def __init__(self):
        self.url_ranking_page = "https://www.letudiant.fr/classements/classement-des-ecoles-d-ingenieurs.html"

    def extract_links(self, html: str) -> set[str]:
        soup = BeautifulSoup(html, "lxml")
        links = {
            urljoin(BASE, a["href"])
            for a in soup.find_all("a", href=True)
            if a.get_text(strip=True) == "Voir la fiche complète"
        }
        return links

    def extract_ranking_page(self):
        """
        Extracts the ranking page from the website.
        """

        all_links = set()
        for page in range(1, 10):  # 1 … 9
            url = RANKING if page == 1 else f"{RANKING}?page={page}"
            html = requests.get(url, headers=HEADERS, timeout=10).text
            extracted_links = self.extract_links(html)
            all_links |= extracted_links
            print(f"Page {page} -> {len(all_links)} liens uniques (+{len(extracted_links)})")
            time.sleep(1)

        print(f"Total final : {len(all_links)} liens")
        with open("liens_fiches_ecoles.csv", "w", encoding="utf-8") as f:
            f.write("url\n")
            f.write("\n".join(sorted(all_links)))


if __name__ == "__main__":
    scrapping = ScrappingLetudiant()
    scrapping.extract_ranking_page()
