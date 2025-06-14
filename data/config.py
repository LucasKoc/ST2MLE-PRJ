class Config:
    BASE = "https://www.letudiant.fr"
    RANKING = f"{BASE}/classements/classement-des-ecoles-d-ingenieurs.html"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    }
    SEARCH = (
        "https://www.letudiant.fr/etudes/"
        "annuaire-enseignement-superieur/etablissement/"
        "critere-{query}/page-1.html"
    )

    THEMATICS_IDS = [425, 426, 427, 429, 430, 431]

    # Paths
    CSV_FALSE_POSITIVE = "false_positive.csv"
    CSV_SCHOOL_URLS = "liens_fiches_ecoles.csv"
    CSV_SCORE_CLASSEMENT_LETUDIANT = "classements_letudiant.csv"
