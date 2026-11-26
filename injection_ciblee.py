import pandas as pd
from datetime import timedelta
import os

print("🧟‍♂️ Injection chirurgicale de 'Quit' et 'Adore' (15 au 24 Nov)...")

def safe_float(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return 0.0
    return float(str(val).replace(',', '').replace(' ', '').replace('+', ''))

df_songs = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig", dtype=str)
df_res = pd.read_csv("historique_resume.csv", encoding="utf-8-sig", dtype=str)

# 1. PARAMÈTRES DES CHANSONS
quit_streams_start = 287173354
adore_streams_start = 81176283

quit_daily_avg = 5396
adore_daily_avg = 4004

# 2. GÉNÉRATION DES DONNÉES DU 15 AU 24
dates_a_reparer = ["2026-11-15", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", 
                   "2026-11-20", "2026-11-21", "2026-11-22", "2026-11-23", "2026-11-24"]

nouvelles_lignes_chansons = []
valeurs_ajoutees = {}

quit_current = quit_streams_start
adore_current = adore_streams_start

for d in dates_a_reparer:
    quit_current += quit_daily_avg
    adore_current += adore_daily_avg
    
    nouvelles_lignes_chansons.append({'Song Title': '* Quit', 'Streams': str(int(quit_current)), 'Daily': str(int(quit_daily_avg)), 'Date': d})
    nouvelles_lignes_chansons.append({'Song Title': '* Adore', 'Streams': str(int(adore_current)), 'Daily': str(int(adore_daily_avg)), 'Date': d})
    
    valeurs_ajoutees[d] = int((quit_current - quit_streams_start) + (adore_current - adore_streams_start)) + quit_streams_start + adore_streams_start

# ==========================================
# INJECTION DANS historique_ariana.csv
# ==========================================
# Nettoyage si le script a déjà été lancé à moitié
df_songs = df_songs[~((df_songs['Song Title'].isin(['* Quit', '* Adore'])) & (df_songs['Date'].isin(dates_a_reparer)))]

df_songs = pd.concat([df_songs, pd.DataFrame(nouvelles_lignes_chansons)], ignore_index=True)
df_songs['Date_obj'] = pd.to_datetime(df_songs['Date'])
df_songs['Streams_num'] = df_songs['Streams'].apply(safe_float)
df_songs = df_songs.sort_values(by=['Date_obj', 'Streams_num'], ascending=[True, False])
df_songs = df_songs.drop(columns=['Date_obj', 'Streams_num'])
df_songs.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")

print("🎵 1/2 : Chansons réinjectées avec succès !")

# ==========================================
# INJECTION DANS historique_resume.csv
# ==========================================
for d in dates_a_reparer:
    ajout = valeurs_ajoutees[d]
    
    # 1. On modifie les Streams globaux
    mask_str = (df_res['Date'] == d) & (df_res['Catégorie'] == 'Streams')
    if not df_res[mask_str].empty:
        total_actuel = safe_float(df_res.loc[mask_str, 'Total'].iloc[0])
        feat_actuel = safe_float(df_res.loc[mask_str, 'As feature (*)'].iloc[0])
        
        df_res.loc[mask_str, 'Total'] = str(int(total_actuel + ajout))
        df_res.loc[mask_str, 'As feature (*)'] = str(int(feat_actuel + ajout))
        
    # 2. On modifie le compteur de Tracks (+2)
    mask_trk = (df_res['Date'] == d) & (df_res['Catégorie'] == 'Tracks')
    if not df_res[mask_trk].empty:
        total_trk = safe_float(df_res.loc[mask_trk, 'Total'].iloc[0])
        feat_trk = safe_float(df_res.loc[mask_trk, 'As feature (*)'].iloc[0])
        
        df_res.loc[mask_trk, 'Total'] = str(int(total_trk + 2))
        df_res.loc[mask_trk, 'As feature (*)'] = str(int(feat_trk + 2))

df_res['Date_obj'] = pd.to_datetime(df_res['Date'])
ordre_cat = {'Streams': 1, 'Daily': 2, 'Tracks': 3}
df_res['Cat_Order'] = df_res['Catégorie'].map(ordre_cat)
df_res = df_res.sort_values(by=['Date_obj', 'Cat_Order'], ascending=[True, True]).drop(columns=['Date_obj', 'Cat_Order'])
df_res.to_csv("historique_resume.csv", index=False, encoding="utf-8-sig")

print("🌍 2/2 : Total Global corrigé sans toucher aux Dailys !")
print("✅ Opération terminée. Le cratère a disparu de ton graphique Total Streams.")