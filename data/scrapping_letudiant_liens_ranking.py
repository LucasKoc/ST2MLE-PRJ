"""
File to scrape data from a website and save it to a CSV file.
"""

import csv
import time
from urllib.parse import quote_plus, urldefrag, urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from config import Config


class ScrappingLetudiant:
    """
    Class to scrape data from a website and save it to a CSV file.
    """

    def __init__(self):
        self.url_ranking_page = (
            "https://www.letudiant.fr/classements/classement-des-ecoles-d-ingenieurs.html"
        )
        self.false_positive = {}

    def load_false_positive(self, path: str) -> None:
        """
        Load false positive URLs from a CSV file.
        Format: {'name': 'url'}
        :param path: Path to the CSV file containing false positive URLs.
        """
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.false_positive[row["name"]] = row["url"]

    def extract_rows(self, html: str, session: requests.Session) -> list[tuple[str, str]]:
        """
        Extracts rows from the HTML content of the ranking page.
        :param html:  HTML content of the ranking page.
        :param session: Requests session to use for the search.
        :return: list of tuples containing the name and URL of each school.
        """
        soup = BeautifulSoup(html, "lxml")
        rows = []
        for btn in soup.find_all(
            "a", href=True, string=lambda t: t and "fiche complète" in t.lower()
        ):
            url = urldefrag(urljoin(Config.BASE, btn["href"])).url
            name = btn.find_previous("h3").get_text(" ", strip=True)
            if "/etudes/annuaire-enseignement-superieur/etablissement/" not in url:
                mapped = self.annuaire_url_from_name(name, session)
                url = mapped or url
            rows.append((name, url))
        return rows

    def extract_ranking_page(self) -> list[tuple[str, str]]:
        """
        Extracts the ranking page from the website.
        """
        session = requests.Session()
        all_rows = []
        for page in range(1, 10):
            url = Config.RANKING if page == 1 else f"{Config.RANKING}?page={page}"
            html = requests.get(url, headers=Config.HEADERS, timeout=10).text
            page_rows = self.extract_rows(html, session)
            all_rows.extend(page_rows)
            print(f"Page {page} -> +{len(page_rows)} lignes (total {len(all_rows)})")
            time.sleep(1)

        print(f"Total final : {len(all_rows)} liens")
        with open(Config.CSV_SCHOOL_URLS, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows([("name", "url")] + all_rows)

        return all_rows

    def annuaire_url_from_name(self, name: str, session: requests.Session) -> str | None:
        """
        Extracts the URL of the school from the name using the annuaire search.
        We point search to - https://www.letudiant.fr/etudes/annuaire-enseignement-superieur/etablissement/critere-<school_name>.html
        Data is provided from ranking page, some schools name are formatted as "School Name - Campus location".

        :param name: Name of the school to search for.
        :param session: Requests session to use for the search.
        :return: URL of the school if found, otherwise None.
        """
        if name in self.false_positive:
            return self.false_positive[name]
        name_clean = name.lower().split("-")[0].strip()
        url = Config.SEARCH.format(query=quote_plus(name_clean))
        html = session.get(url, headers=Config.HEADERS, timeout=10).text
        soup = BeautifulSoup(html, "lxml")

        link = soup.find(
            "a",
            href=lambda h: h
            and "https://www.letudiant.fr/etudes/annuaire-enseignement-superieur/etablissement/"
            in h,
        )
        if link:
            return urldefrag(urljoin(Config.BASE, link["href"])).url
        return None


if __name__ == "__main__":
    scrapping = ScrappingLetudiant()
    scrapping.load_false_positive(Config.CSV_FALSE_POSITIVE)
    rows = scrapping.extract_ranking_page()

    schools = pd.DataFrame([row[1] for row in rows], columns=["url"])
    schools["duplicated"] = schools.duplicated()
    print(schools)
