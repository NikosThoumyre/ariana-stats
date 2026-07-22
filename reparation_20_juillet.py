import pandas as pd

print("🛠️ Début de la réparation temporelle du 20 juillet...")

# ==========================================
# 1. RÉPARATION DE L'HISTORIQUE DES CHANSONS
# ==========================================
df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")

# 💡 LE BOUCLIER ANTI-ERREURS POUR LES CASES VIDES :
def safe_float(val):
    if pd.isna(val) or str(val).strip() in ['-', '']:
        return 0.0
    return float(str(val).replace(',', '').replace(' ', '').replace('+', ''))

# On corrige la date au cas où
df.loc[df['Date'] == '2026-07-20', 'Date'] = '2026-07-21'

# On crée l'Unique_ID pour différencier les homonymes !
df['Occurence'] = df.groupby(['Date', 'Song Title']).cumcount()
df['Unique_ID'] = df['Song Title'] + "___" + df['Occurence'].astype(str)

df_19 = df[df['Date'] == '2026-07-19'].set_index('Unique_ID')
df_21 = df[df['Date'] == '2026-07-21'].set_index('Unique_ID')

chansons_communes = df_19.index.intersection(df_21.index)
lignes_20 = []

for uid in chansons_communes:
    chanson_nom = df_19.loc[uid, 'Song Title']
    
    # On utilise notre bouclier safe_float !
    t_19 = safe_float(df_19.loc[uid, 'Streams'])
    t_21 = safe_float(df_21.loc[uid, 'Streams'])
    d_21 = safe_float(df_21.loc[uid, 'Daily'])
    
    # Les formules magiques
    t_20 = t_21 - d_21
    d_20 = t_20 - t_19
    
    lignes_20.append({
        'Song Title': chanson_nom,
        'Streams': int(t_20),
        'Daily': int(d_20),
        'Date': '2026-07-20'
    })

df_20 = pd.DataFrame(lignes_20)

# On nettoie le fichier d'origine de ses colonnes temporaires
df = df.drop(columns=['Occurence', 'Unique_ID'])

df_final = pd.concat([df, df_20], ignore_index=True)
df_final['Date_obj'] = pd.to_datetime(df_final['Date'])
df_final = df_final.sort_values(by=['Date_obj', 'Streams'], ascending=[False, False]).drop(columns=['Date_obj'])
df_final.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")


# ==========================================
# 2. RÉPARATION DU RÉSUMÉ (Overview)
# ==========================================
df_res = pd.read_csv("historique_resume.csv", encoding="utf-8-sig")
df_res.loc[df_res['Date'] == '2026-07-20', 'Date'] = '2026-07-21'

res_str_19 = df_res[(df_res['Date'] == '2026-07-19') & (df_res['Catégorie'] == 'Streams')].iloc[0]
res_str_21 = df_res[(df_res['Date'] == '2026-07-21') & (df_res['Catégorie'] == 'Streams')].iloc[0]
res_dai_21 = df_res[(df_res['Date'] == '2026-07-21') & (df_res['Catégorie'] == 'Daily')].iloc[0]
res_trk_21 = df_res[(df_res['Date'] == '2026-07-21') & (df_res['Catégorie'] == 'Tracks')].iloc[0]

colonnes = ['Total', 'As lead', 'Solo', 'As feature (*)']
lignes_res_20 = []

# Calcul pour Streams
row_str_20 = {'Catégorie': 'Streams', 'Date': '2026-07-20'}
for col in colonnes:
    t_19 = safe_float(res_str_19[col])
    t_21 = safe_float(res_str_21[col])
    d_21 = safe_float(res_dai_21[col])
    row_str_20[col] = int(t_21 - d_21)
lignes_res_20.append(row_str_20)

# Calcul pour Daily
row_dai_20 = {'Catégorie': 'Daily', 'Date': '2026-07-20'}
for col in colonnes:
    t_19 = safe_float(res_str_19[col])
    t_20 = row_str_20[col]
    row_dai_20[col] = int(t_20 - t_19)
lignes_res_20.append(row_dai_20)

# Pour les Tracks, on copie le 21
row_trk_20 = {'Catégorie': 'Tracks', 'Date': '2026-07-20'}
for col in colonnes:
    row_trk_20[col] = res_trk_21[col]
lignes_res_20.append(row_trk_20)

df_res_20 = pd.DataFrame(lignes_res_20)
df_res_final = pd.concat([df_res, df_res_20], ignore_index=True)

df_res_final['Date_obj'] = pd.to_datetime(df_res_final['Date'])
ordre_cat = {'Streams': 1, 'Daily': 2, 'Tracks': 3}
df_res_final['Cat_Order'] = df_res_final['Catégorie'].map(ordre_cat)
df_res_final = df_res_final.sort_values(by=['Date_obj', 'Cat_Order'], ascending=[False, True]).drop(columns=['Date_obj', 'Cat_Order'])

df_res_final.to_csv("historique_resume.csv", index=False, encoding="utf-8-sig")

print("✅ Félicitations, la faille temporelle du 20 juillet est refermée !")