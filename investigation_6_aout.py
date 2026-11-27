import pandas as pd

print("🔍 ENQUÊTE CIBLÉE : Que manque-t-il dans 'Yours Truly' le 6 août ?\n")

df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")

date_veille = "2026-08-05"
date_cratere = "2026-08-06"

# La tracklist de l'album Yours Truly (Tenth Anniversary Edition)
tracklist = [
    "Honeymoon Avenue", "Baby I", "Right There", "Tattooed Heart", "Lovin' It", 
    "Piano", "Daydreamin'", "The Way", "You'll Never Know", "Almost Is Never Enough", 
    "* Popular Song", "Better Left Unsaid", "Honeymoon Avenue - Live from London", 
    "Daydreamin' - Live from London", "Baby I - Live from London", 
    "Tattooed Heart - Live from London", "Right There - Live from London (feat. Big Sean)", 
    "The Way - Live from London (feat. Mac Miller)"
]

df_5 = df[df['Date'] == date_veille]
df_6 = df[df['Date'] == date_cratere]

chansons_5 = []
chansons_6 = []

# On récolte les noms exacts des chansons classées ces jours-là (en retirant les ___0, ___1...)
for t in df_5['Song Title']:
    chansons_5.append(t.split('___')[0])
for t in df_6['Song Title']:
    chansons_6.append(t.split('___')[0])

print(f"📊 Bilan des pistes de 'Yours Truly' :")
chansons_perdues = []

for track in tracklist:
    # On gère le cas des "___0" de notre dictionnaire
    clean_track = track.split('___')[0] 
    
    etait_la_le_5 = clean_track in chansons_5
    etait_la_le_6 = clean_track in chansons_6
    
    if etait_la_le_5 and not etait_la_le_6:
        chansons_perdues.append(clean_track)
        # On récupère le nombre de streams de la veille pour mesurer l'impact
        streams = int(df_5[df_5['Song Title'].str.startswith(clean_track)]['Streams'].iloc[0])
        print(f"   ❌ DISPARUE le 6 : {clean_track} (Poids : {streams:,} streams)")
    
    elif not etait_la_le_5 and not etait_la_le_6:
        print(f"   💤 Absente les deux jours : {clean_track}")

print("\n💡 CONCLUSION :")
if not chansons_perdues:
    print("   Bizarre, aucune chanson de l'album ne semble avoir disparu ce jour-là...")
else:
    perte_totale = sum([int(df_5[df_5['Song Title'].str.startswith(c)]['Streams'].iloc[0]) for c in chansons_perdues])
    print(f"   => Le 6 août, l'album a perdu {len(chansons_perdues)} chansons, créant un cratère de {perte_totale:,} streams !")