import pandas as pd
from datetime import timedelta
import os

print("🔍 Recherche des trous d'un seul jour et reconstitution exacte...")

def safe_int(val):
    if pd.isna(val): return 0
    return int(str(val).replace(',', '').replace(' ', '').replace('+', ''))

# ==========================================
# 1. HISTORIQUE ARIANA (Chansons)
# ==========================================
df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")
df['Date_obj'] = pd.to_datetime(df['Date'])
dates = sorted(df['Date_obj'].unique())

nouvelles_lignes = []
for i in range(len(dates) - 1):
    d1 = dates[i]
    d2 = dates[i+1]
    
    # Si la différence entre deux dates est EXACTEMENT de 2 jours (ex: 15 août et 17 août)
    if (d2 - d1).days == 2:
        d_manquant = d1 + timedelta(days=1)
        print(f"🛠️ Trou détecté le {d_manquant.strftime('%Y-%m-%d')} (Chansons). Application de ta formule...")
        
        # On utilise l'astuce de l'Unique_ID au cas où il y ait des homonymes
        df['Occurence'] = df.groupby(['Date', 'Song Title']).cumcount()
        df['Unique_ID'] = df['Song Title'] + "___" + df['Occurence'].astype(str)
        
        df1 = df[df['Date_obj'] == d1].set_index('Unique_ID')
        df2 = df[df['Date_obj'] == d2].set_index('Unique_ID')
        
        chansons_communes = df1.index.intersection(df2.index)
        for uid in chansons_communes:
            chanson_nom = df1.loc[uid, 'Song Title']
            
            s1 = float(df1.loc[uid, 'Streams'])
            s2 = float(df2.loc[uid, 'Streams'])
            d2_daily = float(df2.loc[uid, 'Daily'])
            
            # TA FORMULE EXACTE :
            s_manquant = s2 - d2_daily
            d_manquant_daily = s_manquant - s1
            
            nouvelles_lignes.append({
                'Song Title': chanson_nom,
                'Streams': int(s_manquant),
                'Daily': int(d_manquant_daily),
                'Date': d_manquant.strftime('%Y-%m-%d'),
                'Date_obj': d_manquant
            })
            
        df = df.drop(columns=['Occurence', 'Unique_ID'], errors='ignore')

if nouvelles_lignes:
    df = pd.concat([df, pd.DataFrame(nouvelles_lignes)], ignore_index=True)
    # On trie bien par date du plus vieux au plus récent (ascending=True)
    df = df.sort_values(by=['Date_obj', 'Streams'], ascending=[True, False]).drop(columns=['Date_obj'])
    df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")
else:
    df = df.drop(columns=['Date_obj'], errors='ignore')


# ==========================================
# 2. HISTORIQUE RESUME (Overview)
# ==========================================
df_res = pd.read_csv("historique_resume.csv", encoding="utf-8-sig")
df_res['Date_obj'] = pd.to_datetime(df_res['Date'])
dates_res = sorted(df_res['Date_obj'].unique())
nouvelles_lignes_res = []

cols_calc = ['Total', 'As lead', 'Solo', 'As feature (*)']

for i in range(len(dates_res) - 1):
    d1 = dates_res[i]
    d2 = dates_res[i+1]
    if (d2 - d1).days == 2:
        d_manquant = d1 + timedelta(days=1)
        print(f"🛠️ Trou détecté le {d_manquant.strftime('%Y-%m-%d')} (Résumé). Application de ta formule...")
        
        str1 = df_res[(df_res['Date_obj'] == d1) & (df_res['Catégorie'] == 'Streams')].iloc[0]
        str2 = df_res[(df_res['Date_obj'] == d2) & (df_res['Catégorie'] == 'Streams')].iloc[0]
        dai2 = df_res[(df_res['Date_obj'] == d2) & (df_res['Catégorie'] == 'Daily')].iloc[0]
        
        row_str_mid = {'Catégorie': 'Streams', 'Date': d_manquant.strftime('%Y-%m-%d'), 'Date_obj': d_manquant}
        row_dai_mid = {'Catégorie': 'Daily', 'Date': d_manquant.strftime('%Y-%m-%d'), 'Date_obj': d_manquant}
        
        for col in cols_calc:
            s1_val = safe_int(str1[col])
            s2_val = safe_int(str2[col])
            d2_val = safe_int(dai2[col])
            
            # TA FORMULE :
            s_manquant = s2_val - d2_val
            d_manquant_daily = s_manquant - s1_val
            
            row_str_mid[col] = int(s_manquant)
            row_dai_mid[col] = int(d_manquant_daily)
            
        nouvelles_lignes_res.append(row_str_mid)
        nouvelles_lignes_res.append(row_dai_mid)
        
        # Pour les Tracks, on copie simplement le jour d'après
        trk2 = df_res[(df_res['Date_obj'] == d2) & (df_res['Catégorie'] == 'Tracks')].iloc[0]
        row_trk_mid = {'Catégorie': 'Tracks', 'Date': d_manquant.strftime('%Y-%m-%d'), 'Date_obj': d_manquant}
        for col in cols_calc:
            row_trk_mid[col] = trk2[col]
        nouvelles_lignes_res.append(row_trk_mid)

if nouvelles_lignes_res:
    df_res = pd.concat([df_res, pd.DataFrame(nouvelles_lignes_res)], ignore_index=True)
    ordre_cat = {'Streams': 1, 'Daily': 2, 'Tracks': 3}
    df_res['Cat_Order'] = df_res['Catégorie'].map(ordre_cat)
    # Tri chronologique (True)
    df_res = df_res.sort_values(by=['Date_obj', 'Cat_Order'], ascending=[True, True]).drop(columns=['Date_obj', 'Cat_Order'])
    df_res.to_csv("historique_resume.csv", index=False, encoding="utf-8-sig")
else:
    df_res = df_res.drop(columns=['Date_obj'], errors='ignore')


# ==========================================
# 3. HISTORIQUE LISTENERS
# ==========================================
if os.path.exists("historique_ariana_listeners.csv"):
    df_list = pd.read_csv("historique_ariana_listeners.csv", encoding="utf-8-sig")
    df_list['Date_obj'] = pd.to_datetime(df_list['Date'])
    dates_list = sorted(df_list['Date_obj'].unique())
    nouvelles_lignes_list = []
    
    for i in range(len(dates_list) - 1):
        d1 = dates_list[i]
        d2 = dates_list[i+1]
        if (d2 - d1).days == 2:
            d_manquant = d1 + timedelta(days=1)
            print(f"🛠️ Trou détecté le {d_manquant.strftime('%Y-%m-%d')} (Listeners). Application de ta formule...")
            
            l1 = df_list[df_list['Date_obj'] == d1].iloc[0]
            l2 = df_list[df_list['Date_obj'] == d2].iloc[0]
            
            l1_val = safe_int(l1['Listeners'])
            l2_val = safe_int(l2['Listeners'])
            d2_val = safe_int(l2['Daily +/-'])
            
            # TA FORMULE :
            l_manquant = l2_val - d2_val
            d_manquant_daily = l_manquant - l1_val
            
            row_mid = l1.copy()
            row_mid['Date'] = d_manquant.strftime('%Y-%m-%d')
            row_mid['Date_obj'] = d_manquant
            row_mid['Listeners'] = l_manquant
            row_mid['Daily +/-'] = f"+{d_manquant_daily}" if d_manquant_daily > 0 else str(d_manquant_daily)
            
            nouvelles_lignes_list.append(row_mid.to_dict())
            
    if nouvelles_lignes_list:
        df_list = pd.concat([df_list, pd.DataFrame(nouvelles_lignes_list)], ignore_index=True)
        # Tri chronologique (True)
        df_list = df_list.sort_values(by='Date_obj', ascending=True).drop(columns=['Date_obj'])
        df_list.to_csv("historique_ariana_listeners.csv", index=False, encoding="utf-8-sig")
    else:
        df_list = df_list.drop(columns=['Date_obj'], errors='ignore')

print("\n✅ Opération terminée ! Tous les trous de 1 jour ont été rebouchés avec tes calculs exacts !")