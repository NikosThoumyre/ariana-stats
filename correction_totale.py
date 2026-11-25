import pandas as pd
import numpy as np

print("🔧 Début de la correction historique (Titres + Séparation All My Love)...")

# 1. Charger l'historique
df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")

# 2. Corriger les noms de Yours Truly et Rule The World
renames = {
    "Right There (feat. Big Sean)": "Right There",
    "The Way (feat. Mac Miller)": "The Way",
    "Almost Is Never Enough (with Nathan Sykes)": "Almost Is Never Enough",
    "* Popular Song (MIKA & Ariana Grande)": "* Popular Song",
    "* Rule The World (feat. Ariana Grande)": "* Rule The World"
}
df['Song Title'] = df['Song Title'].replace(renames)

# 3. Séparer All My Love (Remix vs Original) grâce aux mathématiques !
mask_aml = df['Song Title'].str.contains('All My Love', case=False, na=False)
streams_num = pd.to_numeric(df['Streams'], errors='coerce').fillna(0)

# Celles à plus de 70M sont le Remix, les autres sont l'Originale
mask_remix = mask_aml & (streams_num >= 70_000_000)
mask_original = mask_aml & (streams_num < 70_000_000)

df.loc[mask_remix, 'Song Title'] = "* All My Love - Remix"
df.loc[mask_original, 'Song Title'] = "* All My Love"

# 4. Recalculer les Dailys parfaits pour effacer les Zig-Zags
df['Date_obj'] = pd.to_datetime(df['Date'])
df = df.sort_values(by=['Song Title', 'Date_obj'])
df['Streams_num'] = pd.to_numeric(df['Streams'], errors='coerce').fillna(0)

nouveau_daily = df.groupby('Song Title')['Streams_num'].diff()

# Garder le daily d'origine pour le 1er jour d'apparition d'une chanson
premiers_jours = df.groupby('Song Title').head(1).index
nouveau_daily.loc[premiers_jours] = pd.to_numeric(df.loc[premiers_jours, 'Daily'], errors='coerce')

df['Daily'] = nouveau_daily.fillna(0).astype(int)

# 5. Trier chronologiquement, nettoyer et sauvegarder
df = df.sort_values(by=['Date_obj', 'Streams_num'], ascending=[True, False])
df = df[['Song Title', 'Streams', 'Daily', 'Date']]
df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")

print("✅ L'historique est parfait : Yours Truly est corrigé, et All My Love a maintenant 2 belles courbes distinctes !")