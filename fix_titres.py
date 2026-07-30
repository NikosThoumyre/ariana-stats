import pandas as pd

print("🔧 Unification des titres (Retour aux noms originaux)...")

df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")

# Le dictionnaire des noms à ramener à la normale
renames = {
    "Right There (feat. Big Sean)": "Right There",
    "The Way (feat. Mac Miller)": "The Way",
    "Almost Is Never Enough (with Nathan Sykes)": "Almost Is Never Enough",
    "* Popular Song (MIKA & Ariana Grande)": "* Popular Song"
}

df['Song Title'] = df['Song Title'].replace(renames)

df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")
print("✅ Terminé ! L'historique est prêt.")