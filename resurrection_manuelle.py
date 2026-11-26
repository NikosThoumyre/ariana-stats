import pandas as pd
from datetime import timedelta
import os

print("🧟‍♂️ Lancement de la Résurrection Intelligente (Redressement Manuel)...")

def safe_float(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return 0.0
    return float(str(val).replace(',', '').replace(' ', '').replace('+', ''))

if not os.path.exists("chansons_fantomes.csv"):
    print("❌ Fichier chansons_fantomes.csv introuvable !")
    exit()

df_fantomes = pd.read_csv("chansons_fantomes.csv", encoding="utf-8-sig")
df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")
# 💡 ON OUVRE LE RESUME EN FORMAT TEXTE POUR NE PAS PLANTER SUR LES 72 MILLIARDS
df_res = pd.read_csv("historique_resume.csv", dtype=str, encoding="utf-8-sig")

df['Date_obj'] = pd.to_datetime(df['Date'])
df_res['Date_obj'] = pd.to_datetime(df_res['Date'])

nouvelles_lignes_chansons = []
valeurs_ajoutees_global = {}

for idx, row_f in df_fantomes.iterrows():
    titre = row_f['Song Title']
    date_cible = pd.to_datetime(row_f['Date'])
    streams_cible = safe_float(row_f['Streams'])
    
    print(f"\n🔍 Traitement de {titre} jusqu'au {date_cible.strftime('%Y-%m-%d')}...")
    
    df_chanson = df[df['Song Title'] == titre]
    if df_chanson.empty: continue
    
    date_last = df_chanson['Date_obj'].max()
    streams_last = safe_float(df_chanson[df_chanson['Date_obj'] == date_last]['Streams'].iloc[0])
    
    jours_ecart = (date_cible - date_last).days
    if jours_ecart <= 0:
        print("   -> Déjà à jour, on ignore.")
        continue
        
    print(f"   -> {jours_ecart} jours à combler. (Passage de {streams_last:,.0f} à {streams_cible:,.0f})")
    
    daily_moyen = (streams_cible - streams_last) / jours_ecart
    
    for i in range(1, jours_ecart + 1):
        date_fantome = date_last + timedelta(days=i)
        streams_fantome = streams_last + (daily_moyen * i)
        
        # 🛡️ LE BOUCLIER ANTI-RETOUR DE KWORB
        date_existe = date_fantome in df['Date_obj'].values
        titre_base = titre.replace('* ', '').strip()
        chansons_du_jour = df[df['Date_obj'] == date_fantome]['Song Title']
        kworb_la_deja_remise = chansons_du_jour.str.contains(titre_base, case=False, regex=False).any()
        
        if date_existe and not kworb_la_deja_remise:
            date_str = date_fantome.strftime('%Y-%m-%d')
            
            nouvelles_lignes_chansons.append({
                'Song Title': titre,
                'Streams': str(int(streams_fantome)),
                'Daily': str(int(daily_moyen)),
                'Date': date_str,
                'Date_obj': date_fantome
            })
            
            if date_str not in valeurs_ajoutees_global: valeurs_ajoutees_global[date_str] = 0
            valeurs_ajoutees_global[date_str] += daily_moyen
            
            # Réparation du cratère géant pour le 1er jour
            if i == 1: 
                valeurs_ajoutees_global[date_str] += streams_last


# ==========================================
# INJECTION ET SAUVEGARDE
# ==========================================
if nouvelles_lignes_chansons:
    for d, row in df_fantomes.iterrows():
        df = df[~((df['Song Title'] == row['Song Title']) & (df['Date_obj'] > df[df['Song Title'] == row['Song Title']]['Date_obj'].max() - timedelta(days=100)) & (df['Date_obj'] <= pd.to_datetime(row['Date'])))]

    df = pd.concat([df, pd.DataFrame(nouvelles_lignes_chansons)], ignore_index=True)
    df = df.sort_values(by=['Date_obj', 'Streams'], ascending=[True, False]).drop(columns=['Date_obj'])
    df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")
    print("\n✅ Historique des chansons réparé !")

    # 💡 L'INJECTION SECURISEE POUR LES CHIFFRES GÉANTS (72 MILLIARDS)
    for date_str, ajout in valeurs_ajoutees_global.items():
        mask_str = (df_res['Date'] == date_str) & (df_res['Catégorie'] == 'Streams')
        if not df_res[mask_str].empty:
            # On calcule librement, et on le transforme en string pur sans virgule
            nouveau_total = int(safe_float(df_res.loc[mask_str, 'Total'].iloc[0]) + ajout)
            nouveau_feat = int(safe_float(df_res.loc[mask_str, 'As feature (*)'].iloc[0]) + ajout)
            
            df_res.loc[mask_str, 'Total'] = str(nouveau_total)
            df_res.loc[mask_str, 'As feature (*)'] = str(nouveau_feat)

    # Lissage des Dailys Globaux (format Texte)
    df_str = df_res[df_res['Catégorie'] == 'Streams'].sort_values('Date_obj').copy()
    df_dai = df_res[df_res['Catégorie'] == 'Daily'].sort_values('Date_obj').copy()
    
    for col in ['Total', 'As lead', 'Solo', 'As feature (*)']:
        diffs = df_str[col].apply(safe_float).diff()
        val_jour1 = safe_float(df_dai.iloc[0][col]) if len(df_dai) > 0 else 0
        diffs.iloc[0] = val_jour1
        
        # Injection en texte strict pour ne pas faire planter Pandas !
        df_dai[col] = diffs.fillna(0).astype(int).astype(str).values
        
    df_res.update(df_str)
    df_res.update(df_dai)
    
    # +2 au compteur de Tracks
    for date_str in valeurs_ajoutees_global.keys():
        mask_trk = (df_res['Date'] == date_str) & (df_res['Catégorie'] == 'Tracks')
        if not df_res[mask_trk].empty:
            nouv_trk = int(safe_float(df_res.loc[mask_trk, 'Total'].iloc[0]) + 2)
            nouv_trk_feat = int(safe_float(df_res.loc[mask_trk, 'As feature (*)'].iloc[0]) + 2)
            
            df_res.loc[mask_trk, 'Total'] = str(nouv_trk)
            df_res.loc[mask_trk, 'As feature (*)'] = str(nouv_trk_feat)

    ordre_cat = {'Streams': 1, 'Daily': 2, 'Tracks': 3}
    df_res['Cat_Order'] = df_res['Catégorie'].map(ordre_cat)
    df_res = df_res.sort_values(by=['Date_obj', 'Cat_Order'], ascending=[True, True]).drop(columns=['Date_obj', 'Cat_Order'])
    df_res.to_csv("historique_resume.csv", index=False, encoding="utf-8-sig")
    print("🌍 Total Global lissé ! Le cratère a disparu.")

else:
    print("\n🤷‍♂️ Rien à mettre à jour.")