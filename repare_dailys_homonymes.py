import pandas as pd

print("🛠️ RECALCUL DES DAILYS (Avec séparation des homonymes)...\n")

df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")
df['Date_obj'] = pd.to_datetime(df['Date'])

# 1. On crée les vrais IDs uniques (en triant bien par streams décroissants d'abord)
df = df.sort_values(by=['Date_obj', 'Streams'], ascending=[True, False])
df['Occurence'] = df.groupby(['Date', 'Song Title']).cumcount()
df['Unique_ID'] = df['Song Title'] + "___" + df['Occurence'].astype(str)

# 2. On trie par ID unique pour ne jamais mélanger les deux versions !
df = df.sort_values(by=['Unique_ID', 'Date_obj'])
df['Streams_num'] = pd.to_numeric(df['Streams'], errors='coerce').fillna(0)

# 3. Le VRAI calcul du Daily
nouveau_daily = df.groupby('Unique_ID')['Streams_num'].diff()

# Pour le tout premier jour d'une chanson, on garde le Daily d'origine (s'il n'est pas buggé)
def fix_first_day(row):
    if pd.isna(row['Vrai_Daily']):
        try:
            old_daily = float(str(row['Daily']).replace(',', '').replace('+', ''))
            # Si le daily d'origine est absurde (> 1 Milliard), on met 0
            if old_daily > 1_000_000_000 or old_daily < -1_000_000_000:
                return 0
            return old_daily
        except:
            return 0
    return row['Vrai_Daily']

df['Vrai_Daily'] = nouveau_daily
df['Daily'] = df.apply(fix_first_day, axis=1).astype(int)

# 4. Nettoyage final et sauvegarde
df = df.sort_values(by=['Date_obj', 'Streams_num'], ascending=[True, False])
df = df[['Song Title', 'Streams', 'Daily', 'Date']]
df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")

print("✅ TOUT EST RÉPARÉ ! Les courbes des homonymes (comme One Last Time et Intro) sont sauvées.")