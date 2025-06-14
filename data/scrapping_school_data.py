import time

import pandas as pd
from bs4 import BeautifulSoup
from config import Config
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm


class ScrappingSchoolData:
    """
    Class to scrape school data from a specific website and save it to a CSV file.
    """

    def __init__(self, url: dict[str, str] | None = None, thematics_ids: list[int] | None = None):
        assert (
            thematics_ids is not None
        ), "Thematics ids must be provided. Check Config.THEMATICS_IDS."

        if url is None:
            url = {}

        self.urls = url
        self.thematics_ids = thematics_ids
        self.data = []

        # Chrome driver setup
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        # chrome_options.binary_location = "/usr/bin/chromium-browser"
        self.driver = webdriver.Chrome(options=chrome_options)

    def load_urls(self, path: str) -> None:
        """
        Load URLs from a CSV file.
        Format: {'name': 'url', 'alt_url'}
        :param path: Path to the CSV file containing URLs.
        """
        assert path is not None, "Path must be provided."
        assert path.endswith(".csv"), "Path must be a CSV file."

        df = pd.read_csv(path)
        self.urls = {
            row["name"]: {"url": row["url"], "alt_url": row.get("alt_url", "")}
            for _, row in df.iterrows()
        }
        print(self.urls)

    def scrape_data(self):
        """
        Scrape data from the loaded URLs and save it into the class attribute `data`.
        """
        try:
            for school_key, sources in tqdm(
                self.urls.items(), desc="Scraping schools", total=len(self.urls)
            ):
                primary_url = sources["url"]
                fallback_url = sources.get("alt_url", "")
                success = self.scrape_school_data(school_key, primary_url)

                if not success and fallback_url:
                    tqdm.write(f"Fallback tentative - {school_key}")
                    self.scrape_school_data(school_key, fallback_url)
        finally:
            self.driver.quit()

    def scrape_school_data(self, school_key: str, url: str) -> bool:
        self.driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        success = False

        for thematic_id in self.thematics_ids:
            header_div = soup.find("div", id=lambda x: x and x.endswith(f"{thematic_id}-header"))
            titre = (
                header_div.find("h2").text.strip() if header_div else f"Thématique {thematic_id}"
            )

            thematic_div = soup.find(
                "div", id=lambda x: x and x.endswith(f"{thematic_id}-criteria")
            )
            if not thematic_div:
                tqdm.write(f"[!] Section {thematic_id} introuvable pour {school_key} | {url}")
                continue

            success = True  # At least one thematic section found

            rows = thematic_div.find_all("div", class_="criterion-row")
            for row in rows:
                try:
                    label = row.find("span", class_="tw-font-medium").get_text(strip=True)
                    score_div = row.find("div", class_="tw-bg-ranking-green")
                    score = score_div.get_text(strip=True) if score_div else "N/A"
                    note_div = row.find("div", class_="tw-text-right")
                    note = note_div.get_text(strip=True) if note_div else "N/A"

                    self.data.append(
                        {
                            "École": school_key,
                            "Thématique": titre,
                            "ID Thématique": thematic_id,
                            "Critère": label,
                            "Score /10": score,
                            "Note brute": note,
                        }
                    )
                except Exception as e:
                    tqdm.write(f"⚠️ Problème ligne ({school_key}, thématique {thematic_id}): {e}")
        return success

    def convert_data_into_df(self) -> pd.DataFrame:
        """
        Convert the scraped data into a pandas DataFrame.
        :return: DataFrame containing the scraped data.
        """
        self.data = (
            pd.DataFrame(self.data)
            if self.data
            else pd.DataFrame(
                columns=[
                    "École",
                    "Thématique",
                    "ID Thématique",
                    "Critère",
                    "Score /10",
                    "Note brute",
                ]
            )
        )
        return self.data

    def export_data_to_csv(self, filename: str = Config.CSV_SCORE_CLASSEMENT_LETUDIANT) -> None:
        """
        Export the scraped data to a CSV file.
        :param filename: Name of the CSV file to save the data.
        """
        df = self.convert_data_into_df()
        df.to_csv(filename, index=False, encoding="utf-8")


if __name__ == "__main__":
    scrapping_school_data = ScrappingSchoolData(thematics_ids=Config.THEMATICS_IDS)
    scrapping_school_data.load_urls(Config.CSV_SCHOOL_URLS)
    scrapping_school_data.scrape_data()
    scrapping_school_data.export_data_to_csv()
