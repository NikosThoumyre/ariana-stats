import pandas as pd
from datetime import timedelta

print("🩺 Opération Chirurgicale ciblée : Réparation du 6 août pour Yours Truly...\n")

def safe_int(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return 0
    return int(float(str(val).replace(',', '').replace(' ', '').replace('+', '')))

df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig", dtype=str)

# On prépare les données (occurences pour ne pas mélanger les homonymes)
df['Date_obj'] = pd.to_datetime(df['Date'])
df['Occurence'] = df.groupby(['Date', 'Song Title']).cumcount()
df['Unique_ID'] = df['Song Title'] + "___" + df['Occurence'].astype(str)

d5 = pd.to_datetime("2026-08-05")
d6 = pd.to_datetime("2026-08-06")
d7 = pd.to_datetime("2026-08-07")

# Les 3 coupables démasquées par notre enquête
chansons_a_reparer = [
    "Right There___0",
    "Almost Is Never Enough___0",
    "* Popular Song___0"
]

lignes_reparees = []

for uid in chansons_a_reparer:
    try:
        # On va chercher le score de la veille (le 5) et du lendemain (le 7)
        s5 = safe_int(df.loc[(df['Unique_ID'] == uid) & (df['Date_obj'] == d5), 'Streams'].iloc[0])
        s7 = safe_int(df.loc[(df['Unique_ID'] == uid) & (df['Date_obj'] == d7), 'Streams'].iloc[0])
        nom = df.loc[(df['Unique_ID'] == uid) & (df['Date_obj'] == d5), 'Song Title'].iloc[0]
        
        # Le calcul du milieu parfait
        mid_s = (s5 + s7) // 2
        daily_6 = mid_s - s5
        daily_7 = s7 - mid_s
        
        # On prépare la ligne fantôme pour le 6
        lignes_reparees.append({
            'Song Title': nom,
            'Streams': str(mid_s),
            'Daily': str(daily_6),
            'Date': "2026-08-06",
            'Date_obj': d6,
            'Unique_ID': uid
        })
        
        # On ajuste le Daily du 7 pour éviter un pic artificiel
        df.loc[(df['Unique_ID'] == uid) & (df['Date_obj'] == d7), 'Daily'] = str(daily_7)
        
        print(f"✨ Trou rebouché pour '{nom}' !")
    except Exception as e:
        print(f"⚠️ Impossible de réparer {uid} : {e}")

# ==========================================
# INJECTION ET SAUVEGARDE
# ==========================================
if lignes_reparees:
    # Par sécurité, si la ligne existait de façon corrompue, on l'efface avant d'injecter la propre
    for uid in chansons_a_reparer:
        df = df[~((df['Unique_ID'] == uid) & (df['Date_obj'] == d6))]
        
    df = pd.concat([df, pd.DataFrame(lignes_reparees)], ignore_index=True)
    
    # On trie pour que le fichier soit propre (du plus vieux au plus récent)
    df['Streams_num'] = df['Streams'].apply(safe_int)
    df = df.sort_values(by=['Date_obj', 'Streams_num'], ascending=[True, False])
    
    df = df.drop(columns=['Date_obj', 'Occurence', 'Unique_ID', 'Streams_num'])
    df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")
    print("\n✅ Historique sauvegardé. La courbe de Yours Truly est sauvée !")
else:
    print("\n🤷‍♂️ Rien à réparer.")