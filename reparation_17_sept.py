import pandas as pd

print("🩺 Chirurgie de précision : Réparation UNIQUEMENT du 17 et 18 septembre...")

date_16 = "2026-09-16"
date_17 = "2026-09-17"
date_18 = "2026-09-18"

def clean_val(x):
    try:
        return float(str(x).replace(',', '').replace(' ', '').replace('+', ''))
    except:
        return 0.0

# ==========================================
# 1. RÉSUMÉ GLOBAL
# ==========================================
print("-> Lissage du résumé global...")
df_res = pd.read_csv("historique_resume.csv", encoding="utf-8-sig")
cols = ['Total', 'As lead', 'Solo', 'As feature (*)']

try:
    for col in cols:
        # On lit les valeurs du 16 et du 18
        val_16 = clean_val(df_res.loc[(df_res['Date'] == date_16) & (df_res['Catégorie'] == 'Streams'), col].values[0])
        val_18 = clean_val(df_res.loc[(df_res['Date'] == date_18) & (df_res['Catégorie'] == 'Streams'), col].values[0])
        
        # On calcule le point parfait au milieu
        mid_val = int((val_16 + val_18) / 2)
        d17 = int(mid_val - val_16)
        d18 = int(val_18 - mid_val)
        
        # On injecte uniquement sur le 17 et le 18
        df_res.loc[(df_res['Date'] == date_17) & (df_res['Catégorie'] == 'Streams'), col] = mid_val
        df_res.loc[(df_res['Date'] == date_17) & (df_res['Catégorie'] == 'Daily'), col] = d17
        df_res.loc[(df_res['Date'] == date_18) & (df_res['Catégorie'] == 'Daily'), col] = d18
        
    df_res.to_csv("historique_resume.csv", index=False, encoding="utf-8-sig")
except Exception as e:
    print(f"Erreur sur le résumé : {e}")

# ==========================================
# 2. CHANSONS INDIVIDUELLES
# ==========================================
print("-> Lissage des chansons...")
df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")
df['Occurence'] = df.groupby(['Date', 'Song Title']).cumcount()
df['Unique_ID'] = df['Song Title'] + "___" + df['Occurence'].astype(str)

df_16 = df[df['Date'] == date_16].set_index('Unique_ID')
df_18 = df[df['Date'] == date_18].set_index('Unique_ID')

# On ne touche qu'aux chansons présentes ces jours là
common_uids = df_16.index.intersection(df_18.index)

for uid in common_uids:
    try:
        s16 = clean_val(df_16.loc[uid, 'Streams'])
        s18 = clean_val(df_18.loc[uid, 'Streams'])
        
        if s16 > 0 and s18 > 0:
            mid_s = int((s16 + s18) / 2)
            d17 = int(mid_s - s16)
            d18 = int(s18 - mid_s)
            
            df.loc[(df['Date'] == date_17) & (df['Unique_ID'] == uid), 'Streams'] = mid_s
            df.loc[(df['Date'] == date_17) & (df['Unique_ID'] == uid), 'Daily'] = d17
            df.loc[(df['Date'] == date_18) & (df['Unique_ID'] == uid), 'Daily'] = d18
    except:
        continue

df = df.drop(columns=['Occurence', 'Unique_ID'])
df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")

print("✅ Opération terminée. Le 17 septembre est lissé, le reste du fichier n'a pas été touché du tout !")