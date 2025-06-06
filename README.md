# ST2MLE - Project
Subject: French engineering school ranking vs reviews

## Description
This project aims to analyze the relationship between the ranking of French engineering schools and the reviews they receive. The goal is to determine if there is a correlation between a school's ranking and the sentiment expressed in its reviews (reality of ranking?).

##  Data
Data sources:
- [LEtudiant.fr](https://www.letudiant.fr/)
- [LEtudiant.fr - Classement des écoles d'ingénieurs 2025](https://www.letudiant.fr/classements/classement-des-ecoles-d-ingenieurs.html)

# Source code
## Requirements
Modules required are included in the `requirements.txt` file. Bash command:
```bash
pip install -r requirements.txt
```

## Code Linting

Code linting is done using `black` and `isort`.
```bash
# Checking code linting
black --check .
isort --check .

# Executing code linting
black .
isort .
```