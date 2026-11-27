import pandas as pd

print("🔍 ENQUÊTE APPROFONDIE : Le mystère d'Eternal Sunshine...\n")

def safe_float(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return 0.0
    return float(str(val).replace(',', '').replace(' ', '').replace('+', ''))

df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")

# La tracklist complète d'Eternal Sunshine (Deluxe)
uids_es = [
    "intro (end of the world)___0", "bye___0", "don't wanna break up again___0", "Saturn Returns Interlude___0", 
    "eternal sunshine___0", "supernatural___0", "true story___0", "the boy is mine___0", "yes, and?___0", 
    "we can't be friends (wait for your love)___0", "i wish i hated you___0", "imperfect for you___0", 
    "ordinary things (feat. Nonna)___0", "intro (end of the world) - extended___0", "yes, and? (with Mariah Carey) - Remix___0", 
    "supernatural (with Troye Sivan) - remix___0", "the boy is mine (with Brandy, Monica) - Remix___0", 
    "twilight zone___0", "warm___0", "dandelion___0", "past life___0", "Hampstead___0"
]

# Les dates suspectes autour de l'anomalie
jours_suspects = ["2026-08-17", "2026-08-18", "2026-08-19", "2026-08-20", "2026-08-21", "2026-08-22"]

# On crée l'ID unique temporaire pour l'enquête
df['Occurence'] = df.groupby(['Date', 'Song Title']).cumcount()
df['Unique_ID'] = df['Song Title'] + "___" + df['Occurence'].astype(str)

print("📈 ÉVOLUTION DES DAILYS GLOBAUX DE L'ALBUM :")
for d in jours_suspects:
    df_d = df[df['Date'] == d]
    if df_d.empty:
        print(f"   [{d}] : ❌ JOUR TOTALEMENT MANQUANT DANS LA BASE DE DONNÉES !")
        continue
        
    df_es = df_d[df_d['Unique_ID'].isin(uids_es)]
    daily_album = df_es['Daily'].apply(safe_float).sum()
    print(f"   [{d}] : +{daily_album:,.0f} streams gagnés")

print("\n🎵 RECHERCHE DES VARIATIONS BIZARRES SUR LES CHANSONS :")
# On cherche si une chanson a gagné > 10M ou perdu des streams sur cette période
df_periode = df[df['Date'].isin(jours_suspects) & df['Unique_ID'].isin(uids_es)].sort_values(by=['Unique_ID', 'Date'])

for uid, grp in df_periode.groupby('Unique_ID'):
    grp = grp.reset_index(drop=True)
    for i in range(1, len(grp)):
        d_avant = grp.loc[i-1, 'Date']
        d_apres = grp.loc[i, 'Date']
        daily = safe_float(grp.loc[i, 'Daily'])
        
        if daily < 0 or daily > 5_000_000: # Si la chanson perd des streams ou gagne plus de 5M en un jour
            nom = grp.loc[i, 'Song Title']
            print(f"   🚨 ANOMALIE sur '{nom}' le {d_apres} (Daily : {daily:,.0f})")