import pandas as pd

print("🧹 Rangement des fichiers dans l'ordre chronologique...")

# 1. Rangement de l'historique des chansons
df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")
df['Date_obj'] = pd.to_datetime(df['Date'])
# ascending=[True, False] -> Dates du plus vieux au plus récent, et Streams du plus grand au plus petit
df = df.sort_values(by=['Date_obj', 'Streams'], ascending=[True, False]).drop(columns=['Date_obj'])
df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")

# 2. Rangement du résumé
df_res = pd.read_csv("historique_resume.csv", encoding="utf-8-sig")
df_res['Date_obj'] = pd.to_datetime(df_res['Date'])
ordre_cat = {'Streams': 1, 'Daily': 2, 'Tracks': 3}
df_res['Cat_Order'] = df_res['Catégorie'].map(ordre_cat)
# ascending=[True, True] -> Dates chronologiques, puis Streams -> Daily -> Tracks
df_res = df_res.sort_values(by=['Date_obj', 'Cat_Order'], ascending=[True, True]).drop(columns=['Date_obj', 'Cat_Order'])
df_res.to_csv("historique_resume.csv", index=False, encoding="utf-8-sig")

print("✅ Fichiers remis dans le bon sens (du plus ancien en haut au plus récent en bas) !")