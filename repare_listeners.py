import pandas as pd
from datetime import timedelta
import os

print("🚀 Décalage et lissage UNIQUEMENT des Listeners...")

def safe_int(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return 0
    return int(float(str(val).replace(',', '').replace(' ', '').replace('+', '')))

def format_daily(val):
    return f"+{val}" if val > 0 else str(val)

# Nos deux anomalies à traiter
trous = [
    {"trou": "2026-09-17", "pic": "2026-09-18"},
    {"trou": "2026-10-01", "pic": "2026-10-02"}
]

fichier = "historique_ariana_listeners.csv"

if os.path.exists(fichier):
    # 💡 CORRECTION : dtype=str force Python à tout lire comme du texte !
    df_list = pd.read_csv(fichier, dtype=str, encoding="utf-8-sig")
    df_list['Date_obj'] = pd.to_datetime(df_list['Date'])

    # Étape 1 : Les deux décalages
    df_list.loc[df_list['Date_obj'] >= pd.to_datetime("2026-09-17"), 'Date_obj'] += timedelta(days=1)
    df_list.loc[df_list['Date_obj'] >= pd.to_datetime("2026-10-01"), 'Date_obj'] += timedelta(days=1)

    nouvelles_lignes_list = []
    
    # Étape 2 : Le lissage (division du Daily par 2)
    for t in trous:
        date_trou = pd.to_datetime(t["trou"])
        date_pic = pd.to_datetime(t["pic"])
        
        row_pic = df_list[df_list['Date_obj'] == date_pic]
        if not row_pic.empty:
            row_pic = row_pic.iloc[0].copy()
            list_pic = safe_int(row_pic['Listeners'])
            daily_pic = safe_int(row_pic['Daily +/-'])
            
            # La Formule (on coupe en deux)
            daily_1 = daily_pic // 2
            daily_2 = daily_pic - daily_1
            list_trou = list_pic - daily_2
            
            # Création du jour manquant
            row_trou = row_pic.copy()
            row_trou['Date_obj'] = date_trou
            row_trou['Listeners'] = str(list_trou)
            row_trou['Daily +/-'] = format_daily(daily_1)
            
            # Correction du jour de pic
            df_list.loc[df_list['Date_obj'] == date_pic, 'Daily +/-'] = format_daily(daily_2)
            nouvelles_lignes_list.append(row_trou.to_dict())

    if nouvelles_lignes_list:
        df_list = pd.concat([df_list, pd.DataFrame(nouvelles_lignes_list)], ignore_index=True)
    
    # Nettoyage et sauvegarde
    df_list['Date'] = df_list['Date_obj'].dt.strftime('%Y-%m-%d')
    df_list = df_list.sort_values(by='Date_obj', ascending=True).drop(columns=['Date_obj'])
    df_list.to_csv(fichier, index=False, encoding="utf-8-sig")
    
    print("✅ Opération 100% terminée sur les Listeners !")
else:
    print(f"❌ Le fichier {fichier} est introuvable.")