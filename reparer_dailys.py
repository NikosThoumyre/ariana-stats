import pandas as pd
import numpy as np

print("🔧 Recalcul mathématique de toutes les colonnes Daily...")

def safe_float(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return np.nan
    return float(str(val).replace(',', '').replace(' ', '').replace('+', ''))

# ==========================================
# 1. RÉSUMÉ GLOBAL
# ==========================================
df_res = pd.read_csv("historique_resume.csv", encoding="utf-8-sig")
df_str = df_res[df_res['Catégorie'] == 'Streams'].sort_values('Date').copy()
df_dai = df_res[df_res['Catégorie'] == 'Daily'].sort_values('Date').copy()
df_trk = df_res[df_res['Catégorie'] == 'Tracks'].sort_values('Date').copy()

for col in ['Total', 'As lead', 'Solo', 'As feature (*)']:
    # Calcul de la différence exacte
    diffs = df_str[col].apply(safe_float).diff()
    
    # On sauvegarde la valeur du premier jour
    val_jour1 = safe_float(df_dai.iloc[0][col]) if len(df_dai) > 0 else 0
    diffs.iloc[0] = val_jour1
    
    # Injection avec .values pour éviter le bug des zéros !
    df_dai[col] = diffs.fillna(0).astype(int).values

df_res_clean = pd.concat([df_str, df_dai, df_trk]).sort_values(by=['Date', 'Catégorie'], ascending=[True, False])
df_res_clean.to_csv("historique_resume.csv", index=False, encoding="utf-8-sig")


# ==========================================
# 2. CHANSONS INDIVIDUELLES
# ==========================================
df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")
df = df.sort_values(by=['Song Title', 'Date'])

df['Streams_num'] = df['Streams'].apply(safe_float)
df['Nouveau_Daily'] = df.groupby('Song Title')['Streams_num'].diff()

# On restaure les dailys du tout premier jour pour chaque chanson
first_days = df.groupby('Song Title').head(1).index
df.loc[first_days, 'Nouveau_Daily'] = df.loc[first_days, 'Daily'].apply(safe_float)

df['Daily'] = df['Nouveau_Daily'].fillna(0).astype(int)

df = df.sort_values(by=['Date', 'Streams'], ascending=[True, False])
df = df[['Song Title', 'Streams', 'Daily', 'Date']]
df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")

print("✅ Terminé ! Tous tes Dailys ont été recalculés et sont parfaits !")