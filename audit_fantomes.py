import pandas as pd

print("🔍 AUDIT : Vérification de la présence des chansons fantômes...\n")

def safe_float(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return 0.0
    return float(str(val).replace(',', '').replace(' ', '').replace('+', ''))

df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")
df_res = pd.read_csv("historique_resume.csv", encoding="utf-8-sig")

# 1. Vérification des chansons individuelles
dates_cibles = ["2026-11-14", "2026-11-15", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20"]
chansons_cibles = ["* Quit", "* Adore"]

print("🎵 PRÉSENCE DES CHANSONS (Historique) :")
for d in dates_cibles:
    df_d = df[df['Date'] == d]
    if df_d.empty:
        print(f"   [{d}] : ❌ Aucune donnée trouvée pour cette date.")
        continue
        
    trouvees = []
    for c in chansons_cibles:
        row = df_d[df_d['Song Title'] == c]
        if not row.empty:
            trouvees.append(f"{c} ({int(safe_float(row.iloc[0]['Streams'])):,} streams)")
            
    if len(trouvees) == 2:
        print(f"   [{d}] : ✅ Les 2 chansons sont bien là ! -> {trouvees}")
    elif len(trouvees) == 1:
        print(f"   [{d}] : ⚠️ Une seule chanson trouvée : {trouvees}")
    else:
        print(f"   [{d}] : ❌ AUCUNE des deux chansons n'est là !")

# 2. Vérification du Total Global
print("\n🌍 VÉRIFICATION DU TOTAL GLOBAL (Résumé) :")
for d in dates_cibles:
    row_res = df_res[(df_res['Date'] == d) & (df_res['Catégorie'] == 'Streams')]
    if not row_res.empty:
        total = safe_float(row_res.iloc[0]['Total'])
        print(f"   [{d}] : {total:,.0f} streams globaux.")
    else:
        print(f"   [{d}] : ❌ Pas de total trouvé.")
        
print("\n💡 Analyse terminée. Copie-moi le résultat pour qu'on comprenne le décalage !")