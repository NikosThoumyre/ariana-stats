import pandas as pd
import numpy as np

print("🩺 Lancement du Lissage Magique (Gomme Anti-Aberrations)...")

def safe_float(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return np.nan
    return float(str(val).replace(',', '').replace(' ', '').replace('+', ''))

# ==========================================
# 1. RÉSUMÉ GLOBAL (Les gros cratères)
# ==========================================
print("🌍 1/2 - Lissage du catalogue global...")
df_res = pd.read_csv("historique_resume.csv", encoding="utf-8-sig")
df_str = df_res[df_res['Catégorie'] == 'Streams'].sort_values('Date').reset_index(drop=True)
df_dai = df_res[df_res['Catégorie'] == 'Daily'].sort_values('Date').reset_index(drop=True)
df_trk = df_res[df_res['Catégorie'] == 'Tracks'].sort_values('Date').reset_index(drop=True)

cols_calc = ['Total', 'As lead', 'Solo', 'As feature (*)']

for col in cols_calc:
    df_str[col] = df_str[col].apply(safe_float)
    
    # 💡 L'ALGORITHME DE DÉTECTION :
    last_valid = df_str.loc[0, col]
    for i in range(1, len(df_str)):
        curr = df_str.loc[i, col]
        diff = curr - last_valid
        
        # Si le catalogue gagne plus de 150M en 1 jour ou PERD des streams = C'est un bug Kworb !
        if diff > 150_000_000 or diff < -2_000_000:
            df_str.loc[i, col] = np.nan # On efface l'erreur
        else:
            last_valid = curr # La donnée est saine, on avance
            
    # On tire un trait droit mathématique sur tous les trous qu'on vient de créer
    df_str[col] = df_str[col].interpolate(method='linear').ffill().bfill().astype(int)
    
    # On recalcule les vrais Dailys
    nouvelles_diffs = df_str[col].diff()
    nouvelles_diffs.iloc[0] = safe_float(df_dai.iloc[0][col]) if len(df_dai) > 0 else 0
    df_dai[col] = nouvelles_diffs.fillna(0).astype(int)

df_res_clean = pd.concat([df_str, df_dai, df_trk]).sort_values(by=['Date', 'Catégorie'], ascending=[True, False])
df_res_clean.to_csv("historique_resume.csv", index=False, encoding="utf-8-sig")


# ==========================================
# 2. CHANSONS INDIVIDUELLES
# ==========================================
print("🎵 2/2 - Lissage des chansons individuelles...")
df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")
df['Occurence'] = df.groupby(['Date', 'Song Title']).cumcount()
df['Unique_ID'] = df['Song Title'] + "___" + df['Occurence'].astype(str)
df = df.sort_values(by=['Unique_ID', 'Date'])
df['Streams_num'] = df['Streams'].apply(safe_float)

lignes_propres = []
for uid, grp in df.groupby('Unique_ID'):
    grp = grp.sort_values('Date').reset_index(drop=True)
    
    if len(grp) > 1:
        last_valid = grp.loc[0, 'Streams_num']
        for i in range(1, len(grp)):
            curr = grp.loc[i, 'Streams_num']
            diff = curr - last_valid
            
            # Bug si une chanson gagne > 30M en un jour ou perd > 500k
            if diff > 30_000_000 or diff < -500_000:
                grp.loc[i, 'Streams_num'] = np.nan
            else:
                last_valid = curr
                
        grp['Streams_num'] = grp['Streams_num'].interpolate(method='linear').ffill().bfill()
        
        dailys = grp['Streams_num'].diff()
        dailys.iloc[0] = safe_float(grp.loc[0, 'Daily'])
        grp['Daily'] = dailys.fillna(0).astype(int)
        grp['Streams'] = grp['Streams_num'].astype(int)
        
    lignes_propres.append(grp)

df_clean = pd.concat(lignes_propres)
df_clean = df_clean.sort_values(by=['Date', 'Streams'], ascending=[True, False])
df_clean = df_clean[['Song Title', 'Streams', 'Daily', 'Date']]
df_clean.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")

print("✅ Terminé ! Ton historique est repassé au fer à repasser. Adieu les bugs de Kworb !")