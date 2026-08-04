import pandas as pd

print("🔍 Analyse ciblée des disparitions et apparitions mystères...")

# 1. On charge le fichier
df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")

# 2. On fixe les dates exactes du "crime"
date_avant = "2026-08-01"  # Le dernier jour normal
date_apres = "2026-08-02"  # Le jour du bug

print(f"📅 Comparaison entre le {date_avant} et le {date_apres} :\n")

# 3. On compare
chansons_avant = set(df[df['Date'] == date_avant]['Song Title'].unique())
chansons_apres = set(df[df['Date'] == date_apres]['Song Title'].unique())

disparues = chansons_avant - chansons_apres
apparues = chansons_apres - chansons_avant

print(f"❌ CHANSONS QUI ONT DISPARU LE {date_apres} :")
if not disparues:
    print("   (Aucune chanson disparue)")
else:
    for c in disparues:
        try:
            streams = df[(df['Date'] == date_avant) & (df['Song Title'] == c)]['Streams'].iloc[0]
            print(f"   - {c} (avait {streams} streams)")
        except:
            print(f"   - {c} (streams inconnus)")

print(f"\n✨ NOUVELLES CHANSONS APPARUES LE {date_apres} :")
if not apparues:
    print("   (Aucune nouvelle chanson)")
else:
    for c in apparues:
        try:
            streams = df[(df['Date'] == date_apres) & (df['Song Title'] == c)]['Streams'].iloc[0]
            print(f"   - {c} (a {streams} streams)")
        except:
            print(f"   - {c} (streams inconnus)")
    
print("\n💡 Conclusion : Regarde les chiffres. Si une disparue et une apparue ont presque les mêmes streams, c'est un renommage !")