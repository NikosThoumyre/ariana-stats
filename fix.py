import pandas as pd

print("🔧 Nettoyage des titres (Round 2)...")

df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")

# On inclut Rule The World dans la liste des corrections !
renames = {
    "Right There (feat. Big Sean)": "Right There",
    "The Way (feat. Mac Miller)": "The Way",
    "Almost Is Never Enough (with Nathan Sykes)": "Almost Is Never Enough",
    "* Popular Song (MIKA & Ariana Grande)": "* Popular Song",
    "* Rule The World (feat. Ariana Grande)": "* Rule The World"
}

df['Song Title'] = df['Song Title'].replace(renames)

df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")
print("✅ Terminé ! Ton historique est réparé et unifié pour le 2 août.")