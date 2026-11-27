import pandas as pd

print("🔧 Lancement de l'écrasement des faux pics (Copie des voisins)...")

# 1. On charge le fichier
df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig", dtype=str)

# 2. On définit nos cibles et la source saine à copier
cibles = [
    {"mauvais_jour": "2026-07-05", "bon_jour": "2026-07-06"},
    {"mauvais_jour": "2026-08-27", "bon_jour": "2026-08-26"},
    {"mauvais_jour": "2026-09-01", "bon_jour": "2026-09-02"}
]

# 3. L'astuce de l'Unique_ID pour ne pas mélanger One Last Time etc.
df['Occurence'] = df.groupby(['Date', 'Song Title']).cumcount()
df['Unique_ID'] = df['Song Title'] + "___" + df['Occurence'].astype(str)

total_modifications = 0

for cible in cibles:
    mauvais_jour = cible["mauvais_jour"]
    bon_jour = cible["bon_jour"]
    
    print(f"-> Traitement du pic du {mauvais_jour} (Copie des valeurs du {bon_jour})...")
    
    # On boucle sur toutes les chansons qui existent dans le fichier
    for uid in df['Unique_ID'].unique():
        try:
            # On vérifie si la chanson existe bien pour les deux jours
            mask_mauvais = (df['Date'] == mauvais_jour) & (df['Unique_ID'] == uid)
            mask_bon = (df['Date'] == bon_jour) & (df['Unique_ID'] == uid)
            
            if not df[mask_mauvais].empty and not df[mask_bon].empty:
                # On lit le bon Daily
                vrai_daily = df.loc[mask_bon, 'Daily'].iloc[0]
                
                # Et on écrase le faux !
                df.loc[mask_mauvais, 'Daily'] = str(vrai_daily)
                total_modifications += 1
        except:
            pass

# 4. On nettoie et on sauvegarde
df = df.drop(columns=['Occurence', 'Unique_ID'])

# On trie pour garder le fichier parfait
df['Date_obj'] = pd.to_datetime(df['Date'])
# On convertit les streams en nombre juste pour le tri, puis on s'en débarrasse
def safe_int(val):
    try: return int(float(str(val).replace(',', '').replace(' ', '').replace('+', '')))
    except: return 0
df['Streams_num'] = df['Streams'].apply(safe_int)

df = df.sort_values(by=['Date_obj', 'Streams_num'], ascending=[True, False])
df = df[['Song Title', 'Streams', 'Daily', 'Date']]

df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")

print(f"\n✅ OPÉRATION TERMINÉE ! {total_modifications} faux Dailys ont été écrasés et réparés.")