import pandas as pd

print("🔧 Nettoyage des titres (Suppression des featurings de Kworb)...")

df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")

# On force les noms longs à redevenir courts pour correspondre à ton Dashboard
renames = {
    "Right There (feat. Big Sean)": "Right There",
    "The Way (feat. Mac Miller)": "The Way",
    "Almost Is Never Enough (with Nathan Sykes)": "Almost Is Never Enough",
    "* Popular Song (MIKA & Ariana Grande)": "* Popular Song"
}

df['Song Title'] = df['Song Title'].replace(renames)

df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")
print("✅ Terminé ! Ton historique est réparé et unifié.")