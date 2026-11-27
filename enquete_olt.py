import pandas as pd

print("🔍 ENQUÊTE SUR 'ONE LAST TIME'...\n")

df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")

# On isole uniquement les lignes qui s'appellent "One Last Time" sur les 3 derniers jours
dates_recentes = sorted(df['Date'].unique(), reverse=True)[:3]
df_olt = df[(df['Song Title'] == 'One Last Time') & (df['Date'].isin(dates_recentes))]

# On affiche ce qu'il y a dans le fichier
print(df_olt.to_string(index=False))

print("\n💡 CONCLUSION : Tu vas voir que les colonnes 'Daily' ont des chiffres absurdes de plusieurs milliards, car le robot a soustrait la petite version à la grande version !")