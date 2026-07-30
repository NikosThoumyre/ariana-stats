import pandas as pd

print("🔍 Analyse des disparitions et apparitions mystères...")

df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")

# On définit les dates avant et après le nouveau "bug" de Kworb
date_avant = "2026-07-27"
date_apres = "2026-07-28"

# On récupère la liste des chansons pour ces deux jours
chansons_avant = set(df[df['Date'] == date_avant]['Song Title'].unique())
chansons_apres = set(df[df['Date'] == date_apres]['Song Title'].unique())

# On fait les soustractions magiques
disparues = chansons_avant - chansons_apres
apparues = chansons_apres - chansons_avant

print(f"\n❌ CHANSONS QUI ONT DISPARU LE {date_apres} :")
for c in disparues:
    try:
        streams = df[(df['Date'] == date_avant) & (df['Song Title'] == c)]['Streams'].iloc[0]
        print(f"   - {c} (avait {streams} streams)")
    except:
        print(f"   - {c} (streams inconnus)")

print(f"\n✨ NOUVELLES CHANSONS APPARUES LE {date_apres} :")
for c in apparues:
    try:
        streams = df[(df['Date'] == date_apres) & (df['Song Title'] == c)]['Streams'].iloc[0]
        print(f"   - {c} (a {streams} streams)")
    except:
        print(f"   - {c} (streams inconnus)")
    
print("\n💡 Conclusion : Si une chanson disparue et une chanson apparue ont presque le même nombre de streams... C'est qu'elle a été renommée !")