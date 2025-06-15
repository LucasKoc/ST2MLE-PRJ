import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
import matplotlib.pyplot as plt
import numpy as np

# Colonnes explicatives pertinentes
features = [
    'note_brute_insertion_à_deux_mois',
    'note_brute_salaire_à_la_sortie',
    "note_brute_diplômés_en_poste_à_l'international",
    'note_brute_forums_entreprises',
    'note_brute_label_dd&rs',
    'note_brute_masse_et_encadrement_des_doctorants',
    'note_brute_moyenne_au_bac_des_intégrés',
    'note_brute_ouverture_sociale',
    'note_brute_parité_au_sein_de_la_promotion_(hommes/femmes)',
    "note_brute_part_d'enseignants-chercheurs",
    'note_brute_politique_de_chaires',
    "note_brute_pourcentage_d'étudiants_internationaux",
    'note_brute_réputation_internationale',
    "note_brute_taux_d'alternants",
    'note_brute_étudiants_rémunérés_pendant_leurs_études',
]

# Préparation des données
X = df[features].apply(pd.to_numeric, errors='coerce')
X = X.fillna(X.mean())

ecoles = df["ecole"] if "ecole" in df.columns else [f"École {i}" for i in range(len(df))]

y_proxy = df['note_brute_insertion_à_deux_mois'].fillna(df['note_brute_insertion_à_deux_mois'].mean())

# Pas de split ici puisque tu entraînes sur toutes les données

# Initialisation des modèles
model_rf = RandomForestRegressor(n_estimators=100, random_state=42)
model_dt = DecisionTreeRegressor(random_state=42)
model_gb = GradientBoostingRegressor(n_estimators=100, random_state=42)

# Entraînement
model_rf.fit(X, y_proxy)
model_dt.fit(X, y_proxy)

model_gb = HistGradientBoostingRegressor(random_state=42)
model_gb.fit(X, y_proxy)


# Prédictions
y_pred_rf = model_rf.predict(X)
y_pred_dt = model_dt.predict(X)
y_pred_gb = model_gb.predict(X)

# Affichage des prédictions
print(f"{'École':30} | {'RF 6 mois':>10} | {'DT 6 mois':>10} | {'GB 6 mois':>10} | {'Insertion 2 mois (réel)':>20}")
print("-"*90)
for nom_ecole, pred_rf, pred_dt, pred_gb in zip(ecoles, y_pred_rf, y_pred_dt, y_pred_gb):
    vrai_2_mois = df.loc[df['ecole'] == nom_ecole, 'note_brute_insertion_à_deux_mois'].values
    vrai_2_mois = vrai_2_mois[0] if len(vrai_2_mois) > 0 else None
    print(f"{nom_ecole:30} | {pred_rf:10.2f} | {pred_dt:10.2f} | {pred_gb:10.2f} | {str(vrai_2_mois):>20}")

# Vraies valeurs pour correspondre aux écoles
vrais_2_mois = []
for nom_ecole in ecoles:
    val = df.loc[df['ecole'] == nom_ecole, 'note_brute_insertion_à_deux_mois'].values
    vrais_2_mois.append(val[0] if len(val) > 0 else np.nan)

x = np.arange(len(ecoles))
width = 0.25

# Calcul des différences pour chaque modèle
differences_rf = np.array(y_pred_rf) - np.array(vrais_2_mois)
differences_dt = np.array(y_pred_dt) - np.array(vrais_2_mois)
differences_gb = np.array(y_pred_gb) - np.array(vrais_2_mois)

plt.figure(figsize=(14, 6))

plt.bar(x - width, differences_rf, width, label='Différence RF', color='tab:blue', alpha=0.7)
plt.bar(x, differences_dt, width, label='Différence DT', color='tab:red', alpha=0.7)
plt.bar(x + width, differences_gb, width, label='Différence GB', color='tab:purple', alpha=0.7)

plt.axhline(0, color='black', linewidth=0.8)
plt.ylabel('Différence (Prédit - Réel)')
plt.xlabel('Écoles (non affichées)')
plt.legend()
plt.grid(True, axis='y', linestyle='--', alpha=0.7)

# Ne pas afficher les labels x pour plus de lisibilité
plt.xticks([])

plt.tight_layout()
plt.show()
