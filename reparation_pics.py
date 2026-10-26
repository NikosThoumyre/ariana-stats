import pandas as pd
from datetime import timedelta

print("🚀 Début de l'opération chirurgicale sur les historiques...")

def safe_int(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return 0
    return int(float(str(val).replace(',', '').replace(' ', '').replace('+', '')))

# 1. Chargement et préparation
df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")
df['Date_obj'] = pd.to_datetime(df['Date'])

# ==========================================
# ÉTAPE 1 & 2 : LES DÉCALAGES
# ==========================================
print("📅 Création des deux trous temporels...")

# Décalage 1 : à partir du 17 Septembre (l'ancien 17 devient 18)
mask1 = df['Date_obj'] >= pd.to_datetime("2026-09-17")
df.loc[mask1, 'Date_obj'] += timedelta(days=1)

# Décalage 2 : à partir du 1er Octobre (l'ancien 30 Sept avait été poussé au 1er Oct, il devient donc 2 Oct)
mask2 = df['Date_obj'] >= pd.to_datetime("2026-10-01")
df.loc[mask2, 'Date_obj'] += timedelta(days=1)


# ==========================================
# ÉTAPE 3 & 4 : REBOUCHAGE ET LISSAGE
# ==========================================
print("🛠️ Fractionnement des pics en deux et calcul des Streams...")

# On crée un ID unique pour éviter de mélanger des chansons homonymes
df['Occurence'] = df.groupby(['Date_obj', 'Song Title']).cumcount()
df['Unique_ID'] = df['Song Title'] + "___" + df['Occurence'].astype(str)

# Nos deux chantiers
trous = [
    {"trou": "2026-09-17", "pic": "2026-09-18"},
    {"trou": "2026-10-01", "pic": "2026-10-02"}
]

nouvelles_lignes = []

for t in trous:
    date_trou = pd.to_datetime(t["trou"])
    date_pic = pd.to_datetime(t["pic"])
    
    # On cible toutes les chansons présentes le jour du pic
    df_pic = df[df['Date_obj'] == date_pic]
    
    for idx, row in df_pic.iterrows():
        uid = row['Unique_ID']
        titre = row['Song Title']
        streams_pic = safe_int(row['Streams'])
        daily_pic_old = safe_int(row['Daily'])
        
        # Le calcul mathématique : On coupe en deux !
        daily_1 = daily_pic_old // 2          # Pour le jour du pic (ex: le 18)
        daily_0 = daily_pic_old - daily_1     # Pour le jour manquant (ex: le 17)
        
        # Le total du jour manquant = Total du pic - Daily du pic
        streams_trou = streams_pic - daily_1
        
        # On prépare la ligne du jour manquant
        nouvelles_lignes.append({
            'Song Title': titre,
            'Streams': streams_trou,
            'Daily': daily_0,
            'Date_obj': date_trou,
            'Unique_ID': uid
        })
        
        # On corrige le Daily du jour de pic dans la base de données
        df.loc[(df['Date_obj'] == date_pic) & (df['Unique_ID'] == uid), 'Daily'] = daily_1


# ==========================================
# ÉTAPE 5 : NETTOYAGE ET SAUVEGARDE
# ==========================================
print("🧹 Sauvegarde des données propres...")

# On rajoute les nouvelles lignes fabriquées
if nouvelles_lignes:
    df = pd.concat([df, pd.DataFrame(nouvelles_lignes)], ignore_index=True)

df['Date'] = df['Date_obj'].dt.strftime('%Y-%m-%d')
df = df.drop(columns=['Date_obj', 'Occurence', 'Unique_ID'], errors='ignore')

# On trie du plus ancien au plus récent, puis par streams décroissants
df['Date_temp'] = pd.to_datetime(df['Date'])
df = df.sort_values(by=['Date_temp', 'Streams'], ascending=[True, False]).drop(columns=['Date_temp'])

df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")

print("✅ MISSION ACCOMPLIE ! Les deux anomalies d'automne ont été désamorcées.")