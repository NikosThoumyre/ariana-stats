import pandas as pd
from datetime import timedelta
import os
import numpy as np

print("🚀 Lancement de la réparation totale (Décalage + Lissage)...")

date_16 = "2026-09-16"
date_17 = "2026-09-17"
date_18 = "2026-09-18"

def safe_int(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return 0
    return int(float(str(val).replace(',', '').replace(' ', '').replace('+', '')))

# ==========================================
# 1. RÉSUMÉ GLOBAL
# ==========================================
df_res = pd.read_csv("historique_resume.csv", encoding="utf-8-sig")
df_res['Date_obj'] = pd.to_datetime(df_res['Date'])

# 1. DÉCALAGE : Tout ce qui est >= au 17 septembre prend +1 jour
mask_res = df_res['Date_obj'] >= pd.to_datetime(date_17)
df_res.loc[mask_res, 'Date_obj'] = df_res.loc[mask_res, 'Date_obj'] + timedelta(days=1)
df_res['Date'] = df_res['Date_obj'].dt.strftime('%Y-%m-%d')

# 2. LISSAGE DU TROU (Le 17)
cols = ['Total', 'As lead', 'Solo', 'As feature (*)']
try:
    for col in cols:
        val_16 = safe_int(df_res.loc[(df_res['Date'] == date_16) & (df_res['Catégorie'] == 'Streams'), col].values[0])
        val_18 = safe_int(df_res.loc[(df_res['Date'] == date_18) & (df_res['Catégorie'] == 'Streams'), col].values[0])
        
        mid_val = int((val_16 + val_18) / 2)
        d17 = int(mid_val - val_16)
        d18 = int(val_18 - mid_val)
        
        nouvelle_ligne_str = {'Catégorie': 'Streams', 'Total': 0, 'As lead': 0, 'Solo': 0, 'As feature (*)': 0, 'Date': date_17, 'Date_obj': pd.to_datetime(date_17)}
        nouvelle_ligne_dai = {'Catégorie': 'Daily', 'Total': 0, 'As lead': 0, 'Solo': 0, 'As feature (*)': 0, 'Date': date_17, 'Date_obj': pd.to_datetime(date_17)}
        nouvelle_ligne_trk = df_res[(df_res['Date'] == date_18) & (df_res['Catégorie'] == 'Tracks')].iloc[0].to_dict()
        nouvelle_ligne_trk['Date'] = date_17
        nouvelle_ligne_trk['Date_obj'] = pd.to_datetime(date_17)
        
        if not (df_res['Date'] == date_17).any():
            df_res = pd.concat([df_res, pd.DataFrame([nouvelle_ligne_str, nouvelle_ligne_dai, nouvelle_ligne_trk])], ignore_index=True)
        
        df_res.loc[(df_res['Date'] == date_17) & (df_res['Catégorie'] == 'Streams'), col] = mid_val
        df_res.loc[(df_res['Date'] == date_17) & (df_res['Catégorie'] == 'Daily'), col] = d17
        df_res.loc[(df_res['Date'] == date_18) & (df_res['Catégorie'] == 'Daily'), col] = d18

    ordre_cat = {'Streams': 1, 'Daily': 2, 'Tracks': 3}
    df_res['Cat_Order'] = df_res['Catégorie'].map(ordre_cat)
    df_res = df_res.sort_values(by=['Date_obj', 'Cat_Order'], ascending=[True, True]).drop(columns=['Date_obj', 'Cat_Order'])
    df_res.to_csv("historique_resume.csv", index=False, encoding="utf-8-sig")
except Exception as e:
    print(f"Erreur résumé: {e}")


# ==========================================
# 2. CHANSONS INDIVIDUELLES
# ==========================================
df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")
df['Date_obj'] = pd.to_datetime(df['Date'])

# 1. DÉCALAGE
mask_df = df['Date_obj'] >= pd.to_datetime(date_17)
df.loc[mask_df, 'Date_obj'] = df.loc[mask_df, 'Date_obj'] + timedelta(days=1)
df['Date'] = df['Date_obj'].dt.strftime('%Y-%m-%d')

# 2. LISSAGE DU TROU
df['Occurence'] = df.groupby(['Date', 'Song Title']).cumcount()
df['Unique_ID'] = df['Song Title'] + "___" + df['Occurence'].astype(str)

df_16 = df[df['Date'] == date_16].set_index('Unique_ID')
df_18 = df[df['Date'] == date_18].set_index('Unique_ID')

common_uids = df_16.index.intersection(df_18.index)
lignes_17 = []

for uid in common_uids:
    s16 = safe_int(df_16.loc[uid, 'Streams'])
    s18 = safe_int(df_18.loc[uid, 'Streams'])
    nom = df_16.loc[uid, 'Song Title']
    
    if s16 > 0 and s18 > 0:
        mid_s = int((s16 + s18) / 2)
        d17 = int(mid_s - s16)
        d18 = int(s18 - mid_s)
        
        lignes_17.append({
            'Song Title': nom,
            'Streams': mid_s,
            'Daily': d17,
            'Date': date_17,
            'Date_obj': pd.to_datetime(date_17)
        })
        df.loc[(df['Date'] == date_18) & (df['Unique_ID'] == uid), 'Daily'] = d18

df = df.drop(columns=['Occurence', 'Unique_ID'])
if lignes_17 and not (df['Date'] == date_17).any():
    df = pd.concat([df, pd.DataFrame(lignes_17)], ignore_index=True)
    df = df.sort_values(by=['Date_obj', 'Streams'], ascending=[True, False])

df = df.drop(columns=['Date_obj'])
df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")


# ==========================================
# 3. LISTENERS
# ==========================================
if os.path.exists("historique_ariana_listeners.csv"):
    df_list = pd.read_csv("historique_ariana_listeners.csv", encoding="utf-8-sig")
    df_list['Date_obj'] = pd.to_datetime(df_list['Date'])
    
    # Décalage
    mask_list = df_list['Date_obj'] >= pd.to_datetime(date_17)
    df_list.loc[mask_list, 'Date_obj'] = df_list.loc[mask_list, 'Date_obj'] + timedelta(days=1)
    df_list['Date'] = df_list['Date_obj'].dt.strftime('%Y-%m-%d')
    
    # Lissage
    try:
        l16 = safe_int(df_list[df_list['Date'] == date_16].iloc[0]['Listeners'])
        l18 = safe_int(df_list[df_list['Date'] == date_18].iloc[0]['Listeners'])
        
        mid_l = int((l16 + l18) / 2)
        d17 = mid_l - l16
        d18 = l18 - mid_l
        
        row_17 = df_list[df_list['Date'] == date_18].iloc[0].to_dict()
        row_17['Date'] = date_17
        row_17['Date_obj'] = pd.to_datetime(date_17)
        row_17['Listeners'] = mid_l
        row_17['Daily +/-'] = f"+{d17}" if d17 > 0 else str(d17)
        
        if not (df_list['Date'] == date_17).any():
            df_list = pd.concat([df_list, pd.DataFrame([row_17])], ignore_index=True)
            
        df_list.loc[df_list['Date'] == date_18, 'Daily +/-'] = f"+{d18}" if d18 > 0 else str(d18)
        
        df_list = df_list.sort_values(by='Date_obj', ascending=True).drop(columns=['Date_obj'])
        df_list.to_csv("historique_ariana_listeners.csv", index=False, encoding="utf-8-sig")
    except Exception as e:
        print(f"Erreur Listeners: {e}")

print("✅ TOUT EST RÉPARÉ ! Les dates sont décalées et le 17 septembre a été calculé sans aucun pic !")