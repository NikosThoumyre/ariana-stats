import pandas as pd

print("🔍 INVENTAIRE COMPLET : Que s'est-il passé entre le 14 et le 15 novembre ?\n")

# 1. Chargement des données
df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")

date_14 = "2026-11-14"
date_15 = "2026-11-15"

df_14 = df[df['Date'] == date_14]
df_15 = df[df['Date'] == date_15]

# On récupère les listes exactes de noms de chansons
chansons_14 = set(df_14['Song Title'].unique())
chansons_15 = set(df_15['Song Title'].unique())

# On fait le croisement
disparues = chansons_14 - chansons_15
apparues = chansons_15 - chansons_14

# --- AFFICHAGE DES DISPARITIONS ---
print(f"❌ CHANSONS TOTALEMENT DISPARUES LE {date_15} (Il y en a {len(disparues)}) :")
if not disparues:
    print("   (Aucune)")
else:
    # On les trie par ordre alphabétique pour plus de lisibilité
    for c in sorted(disparues):
        try:
            streams = df_14[df_14['Song Title'] == c]['Streams'].iloc[0]
            print(f"   - {c} (Faisait {streams:,} streams au total le 14)")
        except:
            print(f"   - {c}")

# --- AFFICHAGE DES APPARITIONS ---
print(f"\n✨ NOUVELLES CHANSONS APPARUES LE {date_15} (Il y en a {len(apparues)}) :")
if not apparues:
    print("   (Aucune)")
else:
    for c in sorted(apparues):
        try:
            streams = df_15[df_15['Song Title'] == c]['Streams'].iloc[0]
            print(f"   - {c} (A {streams:,} streams au total le 15)")
        except:
            print(f"   - {c}")

print("\n💡 BILAN DES COURSES :")
print(f"   - Kworb a enlevé {len(disparues)} chansons.")
print(f"   - Kworb a ajouté {len(apparues)} chansons.")
print(f"   - Solde net sur ton compteur de 'Tracks' : {len(apparues) - len(disparues)} chansons.")