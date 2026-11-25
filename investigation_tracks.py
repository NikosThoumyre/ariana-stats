import pandas as pd

print("🔍 ENQUÊTE SUR LE NOMBRE DE CHANSONS (14 vs 15 Nov)...\n")

def safe_int(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return 0
    return int(float(str(val).replace(',', '').replace(' ', '').replace('+', '')))

df_res = pd.read_csv("historique_resume.csv", encoding="utf-8-sig")

# On extrait les données du 14 et du 15 Novembre pour la catégorie "Tracks"
try:
    tracks_14 = df_res[(df_res['Date'] == '2026-11-14') & (df_res['Catégorie'] == 'Tracks')].iloc[0]
    tracks_15 = df_res[(df_res['Date'] == '2026-11-15') & (df_res['Catégorie'] == 'Tracks')].iloc[0]
    
    t_14 = safe_int(tracks_14['Total'])
    t_15 = safe_int(tracks_15['Total'])
    
    f_14 = safe_int(tracks_14['As feature (*)'])
    f_15 = safe_int(tracks_15['As feature (*)'])
    
    print(f"📊 ÉVOLUTION DU CATALOGUE (TOTAL TRACKS) :")
    print(f"   - Le 14 Nov : {t_14} chansons")
    print(f"   - Le 15 Nov : {t_15} chansons")
    print(f"   => Différence : {t_15 - t_14} chansons\n")
    
    print(f"🤝 ÉVOLUTION DES COLLABORATIONS (AS FEATURE) :")
    print(f"   - Le 14 Nov : {f_14} featurings")
    print(f"   - Le 15 Nov : {f_15} featurings")
    print(f"   => Différence : {f_15 - f_14} featurings\n")
    
    if (t_15 - t_14) < 0:
        print("💡 CONCLUSION : Ton intuition était parfaite. Kworb a bel et bien supprimé des chansons de sa base de données !")

except Exception as e:
    print(f"Erreur lors de la lecture : {e}")