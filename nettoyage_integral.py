import pandas as pd
import numpy as np
import os

print("🧹 Lancement du Grand Nettoyage Intégral de la Base de Données...")

def safe_float(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return np.nan
    return float(str(val).replace(',', '').replace(' ', '').replace('+', ''))

# ==========================================
# 1. NETTOYAGE DES CHANSONS (historique_ariana.csv)
# ==========================================
print("🎵 1/3 - Recalcul de toutes les chansons...")
df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")
df['Date_obj'] = pd.to_datetime(df['Date'])
df['Occurence'] = df.groupby(['Date', 'Song Title']).cumcount()
df['Unique_ID'] = df['Song Title'] + "___" + df['Occurence'].astype(str)

df = df.sort_values(by=['Unique_ID', 'Date_obj'])
df['Streams_num'] = df['Streams'].apply(safe_float)

lignes_propres = []
for uid, grp in df.groupby('Unique_ID'):
    grp = grp.copy()
    
    # 1. On détecte les aberrations (si une chanson PERD plus de 50 000 streams d'un coup, c'est un bug Kworb)
    diffs = grp['Streams_num'].diff()
    aberrations = diffs < -50000
    grp.loc[aberrations, 'Streams_num'] = np.nan
    
    # 2. Lissage mathématique des trous (Interpolation)
    grp['Streams_num'] = grp['Streams_num'].interpolate(method='linear').ffill().bfill()
    
    # 3. RECALCUL ABSOLU DU DAILY
    grp['Daily_Calc'] = grp['Streams_num'].diff()
    # Pour le tout premier jour, on garde le Daily d'origine (car on n'a pas le jour d'avant pour calculer)
    grp['Daily_Calc'] = grp['Daily_Calc'].fillna(pd.to_numeric(grp['Daily'], errors='coerce'))
    
    grp['Streams'] = grp['Streams_num'].fillna(0).astype(int)
    grp['Daily'] = grp['Daily_Calc'].fillna(0).astype(int)
    lignes_propres.append(grp)

df_clean = pd.concat(lignes_propres)
df_clean = df_clean.sort_values(by=['Date_obj', 'Streams'], ascending=[True, False])
df_clean = df_clean[['Song Title', 'Streams', 'Daily', 'Date']]
df_clean.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")


# ==========================================
# 2. NETTOYAGE DU RÉSUMÉ (historique_resume.csv)
# ==========================================
print("🌍 2/3 - Recalcul du Global et des Albums...")
df_res = pd.read_csv("historique_resume.csv", encoding="utf-8-sig")
df_res['Date_obj'] = pd.to_datetime(df_res['Date'])

df_str = df_res[df_res['Catégorie'] == 'Streams'].sort_values('Date_obj').copy()
df_dai = df_res[df_res['Catégorie'] == 'Daily'].sort_values('Date_obj').copy()
df_trk = df_res[df_res['Catégorie'] == 'Tracks'].sort_values('Date_obj').copy()

cols_calc = ['Total', 'As lead', 'Solo', 'As feature (*)']

for col in cols_calc:
    df_str[col] = df_str[col].apply(safe_float)
    
    # 1. Détection des aberrations globales (si le catalogue perd plus de 500k streams)
    diffs = df_str[col].diff()
    aberrations = diffs < -500000
    df_str.loc[aberrations, col] = np.nan
    
    # 2. Lissage
    df_str[col] = df_str[col].interpolate(method='linear').ffill().bfill().astype(int)
    
    # 3. RECALCUL DU DAILY POUR LE GLOBAL
    nouvelles_diffs = df_str[col].diff()
    
    # On met à jour le DataFrame Daily !
    # Pour le 1er jour, on garde la valeur Daily d'origine
    premier_jour = df_str['Date_obj'].iloc[0]
    valeur_origine_jour1 = safe_float(df_dai[df_dai['Date_obj'] == premier_jour][col].iloc[0]) if not df_dai[df_dai['Date_obj'] == premier_jour].empty else 0
    nouvelles_diffs.iloc[0] = valeur_origine_jour1
    
    df_dai[col] = nouvelles_diffs.fillna(0).astype(int)

df_res_clean = pd.concat([df_str, df_dai, df_trk])
ordre_cat = {'Streams': 1, 'Daily': 2, 'Tracks': 3}
df_res_clean['Cat_Order'] = df_res_clean['Catégorie'].map(ordre_cat)
df_res_clean = df_res_clean.sort_values(by=['Date_obj', 'Cat_Order'], ascending=[True, True])
df_res_clean = df_res_clean[['Catégorie', 'Total', 'As lead', 'Solo', 'As feature (*)', 'Date']]
df_res_clean.to_csv("historique_resume.csv", index=False, encoding="utf-8-sig")


# ==========================================
# 3. NETTOYAGE DES LISTENERS
# ==========================================
if os.path.exists("historique_ariana_listeners.csv"):
    print("👥 3/3 - Recalcul des Monthly Listeners...")
    df_list = pd.read_csv("historique_ariana_listeners.csv", encoding="utf-8-sig")
    df_list['Date_obj'] = pd.to_datetime(df_list['Date'])
    df_list = df_list.sort_values('Date_obj')
    
    df_list['Listeners_num'] = df_list['Listeners'].apply(safe_float)
    
    # Lissage si perte aberrante (ex: - 5 millions d'un coup)
    aberrations = df_list['Listeners_num'].diff() < -5000000
    df_list.loc[aberrations, 'Listeners_num'] = np.nan
    df_list['Listeners_num'] = df_list['Listeners_num'].interpolate(method='linear').ffill().bfill()
    df_list['Listeners'] = df_list['Listeners_num'].astype(int)
    
    # RECALCUL DU DAILY +/-
    diffs_list = df_list['Listeners_num'].diff()
    
    # On garde le daily d'origine pour le tout premier jour
    valeur_origine_list_jour1 = str(df_list['Daily +/-'].iloc[0])
    
    def format_list_daily(val):
        if pd.isna(val): return "0"
        v = int(val)
        return f"+{v}" if v > 0 else str(v)

    nouveaux_dailys = diffs_list.apply(format_list_daily)
    nouveaux_dailys.iloc[0] = valeur_origine_list_jour1
    df_list['Daily +/-'] = nouveaux_dailys
    
    df_list = df_list.drop(columns=['Date_obj', 'Listeners_num'])
    df_list.to_csv("historique_ariana_listeners.csv", index=False, encoding="utf-8-sig")

print("\n✅ INCROYABLE ! Toute ta base de données a été purifiée et recalculée depuis le 1er jour !")