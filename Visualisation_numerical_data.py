import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# === Corrélation (heatmap) ===

# Sélection des colonnes numériques uniquement
numeric_df = df.select_dtypes(include='number')

# Heatmap des corrélations sans annotations
plt.figure(figsize=(12, 10))
sns.heatmap(numeric_df.corr(), annot=False, fmt=".2f", cmap='coolwarm', square=True,
            xticklabels=False, yticklabels=False)
plt.axis('off')
plt.tight_layout()
plt.show()

# === Boxplot de l'insertion à 2 mois ===

plt.figure(figsize=(10, 6))
sns.boxplot(data=df, y='note_brute_insertion_à_deux_mois')
plt.title('Répartition des taux d\'insertion à 2 mois')
plt.ylabel('Taux d\'insertion (%)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# === Radar Chart pour international ===

# Liste des critères sélectionnés
criteria = [
    "note_brute_pourcentage_d'étudiants_internationaux",
    "note_brute_diplômés_en_poste_à_l'international",
    "note_brute_diplômés_ayant_passé_plus_d'un_semestre_à_l'international_en_stage"
]

# Convertir en numérique et gérer les erreurs sur tout le df (pour être sûr)
for col in criteria:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Remplacer NaN par la moyenne de la colonne
df[criteria] = df[criteria].fillna(df[criteria].mean())

# Calcul du score international = moyenne des 3 critères
df['score_international'] = df[criteria].mean(axis=1)

# Sélectionner top 5 écoles selon score international
top5_schools = df.sort_values(by='score_international', ascending=False).head(5)

# Extraire données critères pour ces écoles
data = top5_schools.set_index('ecole')[criteria]

# Normalisation min-max par colonne (critères)
normalized_data = (data - data.min()) / (data.max() - data.min())

# Préparer labels (numéros) et angles pour le radar chart
num_vars = len(criteria)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]  # Fermer le polygone

labels_num = [str(i) for i in range(1, num_vars + 1)]

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

colors = sns.color_palette("RdBu_r", n_colors=len(normalized_data))

# Tracer chaque école avec numéro comme légende et couleurs rouge à bleu
for i, (school, color) in enumerate(zip(normalized_data.index, colors), start=1):
    values = normalized_data.loc[school].tolist()
    values += values[:1]
    ax.plot(angles, values, label=str(i), color=color)
    ax.fill(angles, values, alpha=0.25, color=color)

ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)
ax.set_thetagrids(np.degrees(angles[:-1]), labels_num, fontsize=12)
plt.xticks(rotation=45)
plt.yticks([0.2, 0.4, 0.6, 0.8], ["0.2", "0.4", "0.6", "0.8"], color="grey", size=8)
ax.set_rlabel_position(180 / num_vars)
plt.ylim(0, 1)

plt.title("Top 5 écoles selon score international", size=16, y=1.1)
plt.legend(title="Écoles (numéro)", loc='upper right', bbox_to_anchor=(1.3, 1.1))

# Tableau sous le radar chart (inchangé)

table_data = top5_schools.set_index('ecole')[criteria + ['score_international']].round(2)
table_data_num = table_data[criteria].copy()
table_data_num.columns = labels_num
table_data_num['Score International'] = table_data['score_international']
table_data_num.index.name = 'École'

plt.subplots_adjust(bottom=0.3)
table_ax = fig.add_axes([0.1, 0.05, 0.8, 0.2])
table_ax.axis('off')

table = table_ax.table(cellText=table_data_num.reset_index().values,
                       colLabels=table_data_num.reset_index().columns,
                       cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.5)

plt.show()

print("Correspondance numéro -> critère :")
for i, crit in enumerate(criteria, start=1):
    print(f"{i} : {crit}")

print("\nCorrespondance numéro -> école :")
for i, school in enumerate(normalized_data.index, start=1):
    print(f"{i} : {school}")

# === Radar Chart pour une école (ex : EFREI) ===

features = [
    # Stage & Expérience
    "note_brute_diplômés_ayant_passé_plus_d'un_semestre_à_l'international_en_stage",
    "note_brute_durée_minimale_de_stages_en_entreprise",
    "note_brute_taux_d'alternants",
    # Vie Étudiante & Accompagnement
    "note_brute_valorisation_de_l'engagement_étudiant",
    "note_brute_nombre_de_places_en_résidence_crous_et_privées",
    # International
    "note_brute_pourcentage_d'étudiants_internationaux",
    "note_brute_diplômés_en_poste_à_l'international",
    "note_brute_diplômés_ayant_passé_plus_d'un_semestre_à_l'international_en_échange_académique",
    "score_diplômés_en_poste_à_l'international",
    # Formation & Effectifs
    "note_brute_cycle_ingénieur_-_nombre_d'intégrés_en_1ère_année",
    "note_brute_cycle_prépa_intégrée_-_nombre_d'intégrés_à_bac",
    "note_brute_nombre_d'étudiants_par_enseignant",
    "note_brute_taille_des_promos_en_cycle_ingénieur",
    "note_brute_part_etudiant_hommes",
    "note_brute_part_etudiant_femmes",
    # Qualité & Recherche
    "note_brute_recherche_et_enseignement",
    "note_brute_masse_et_encadrement_des_doctorants",
    "score_label_dd&rs",
    "score_masse_et_encadrement_des_doctorants"
]

ecole_cible = "EFREI"
row = df[df["ecole"].str.contains(ecole_cible, case=False, na=False)]

if row.empty:
    print(f"L'école {ecole_cible} n'a pas été trouvée.")
else:
    values = row[features].iloc[0].fillna(0).values
    max_vals = df[features].max().values
    values = values / max_vals

    labels = [f.replace("note_brute_", "").replace("_", " ")[:25] for f in features]
    num_vars = len(labels)

    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values = values.tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, values, color='tab:blue', linewidth=2)
    ax.fill(angles, values, color='tab:blue', alpha=0.25)

    ax.set_title(f"Radar Chart - {ecole_cible}", size=16, y=1.08)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=10)
    ax.set_ylim(0, 1)
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

# === Dictionnaire des catégories pour les heatmap ===
criteria_dict = {
    "Stage & Expérience": {
        '1': "note_brute_diplômés_ayant_passé_plus_d'un_semestre_à_l'international_en_stage",
        '2': "note_brute_durée_minimale_de_stages_en_entreprise",
        '3': "note_brute_pourcentage_d'étudiants_en_stage_en_fin_d'études",
        '4': "note_brute_taux_d'alternants",
    },
    "Vie Étudiante & Accompagnement": {
        '1': "note_brute_valorisation_de_l'engagement_étudiant",
        '2': "note_brute_vie_associative",
        '3': "note_brute_nombre_de_places_en_résidence_crous_et_privées"
    },
    "International": {
        '1': "note_brute_pourcentage_d'étudiants_internationaux",
        '2': "note_brute_diplômés_en_poste_à_l'international",
        '3': "note_brute_diplômés_ayant_passé_plus_d'un_semestre_à_l'international_en_stage",
        '4': "note_brute_diplômés_ayant_passé_plus_d'un_semestre_à_l'international_en_échange_académique",
        '5': "score_diplômés_en_poste_à_l'international"
    },
    "Formation & Effectifs": {
        '1': "note_brute_cycle_ingénieur_-_nombre_d'intégrés_en_1ère_année",
        '2': "note_brute_cycle_prépa_intégrée_-_nombre_d'intégrés_à_bac",
        '3': "note_brute_nombre_d'étudiants_par_enseignant",
        '4': "note_brute_taille_des_promos_en_cycle_ingénieur",
        '5': "note_brute_part_etudiant_hommes",
        '6': "note_brute_part_etudiant_femmes"
    },
    "Qualité & Recherche": {
        '1': "note_brute_recherche_et_enseignement",
        '2': "note_brute_masse_et_encadrement_des_doctorants",
        '3': "score_label_dd&rs",
        '4': "score_masse_et_encadrement_des_doctorants"
    }
}

# === Affichage heatmaps + statistiques ===
for theme, criteres in criteria_dict.items():
    colonnes = list(criteres.values())
    colonnes_existantes = [c for c in colonnes if c in df.columns]

    if not colonnes_existantes:
        print(f"[{theme}] Aucune donnée disponible.\n")
        continue

    data = df[colonnes_existantes]

    # Statistiques générales
    flat_values = data.values.flatten()
    flat_values = flat_values[~pd.isnull(flat_values)]

    print(f"\n📊 {theme}")
    print(f"  Moyenne   : {flat_values.mean():.3f}")
    print(f"  Médiane   : {pd.Series(flat_values).median():.3f}")
    print(f"  Écart-type: {flat_values.std():.3f}")
    print(f"  Min       : {flat_values.min():.3f}")
    print(f"  Max       : {flat_values.max():.3f}")

    # Normalisation des données pour comparabilité
    data_normalized = data.copy()
    for col in data.columns:
        max_val = df[col].max()
        if max_val != 0:
            data_normalized[col] = df[col] / max_val
        else:
            data_normalized[col] = 0

    # Heatmap
    plt.figure(figsize=(12, 6))
    sns.heatmap(data_normalized, cmap='RdBu_r', linewidths=0.5, linecolor='gray',
                cbar_kws={'label': 'Score normalisé (0-1)'})
    plt.title(f"🔍 Heatmap - {theme}")
    plt.xlabel("Critères")
    plt.ylabel("Écoles")
    plt.xticks(ticks=[i + 0.5 for i in range(len(data.columns))],
               labels=[col.replace("note_brute_", "").replace("score_", "").replace("_", " ")[:25] for col in data.columns],
               rotation=30, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()
