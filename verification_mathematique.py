import pandas as pd

print("🔍 VÉRIFICATION MATHÉMATIQUE DE LA CHUTE DU 15 NOVEMBRE...\n")

def safe_float(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return 0.0
    return float(str(val).replace(',', '').replace(' ', '').replace('+', ''))

date_14 = "2026-11-14"
date_15 = "2026-11-15"

# ==========================================
# 1. Analyse du GLOBAL
# ==========================================
df_res = pd.read_csv("historique_resume.csv", encoding="utf-8-sig")
str_14 = df_res[(df_res['Date'] == date_14) & (df_res['Catégorie'] == 'Streams')]['Total'].iloc[0]
str_15 = df_res[(df_res['Date'] == date_15) & (df_res['Catégorie'] == 'Streams')]['Total'].iloc[0]

tot_14 = safe_float(str_14)
tot_15 = safe_float(str_15)
chute_globale = tot_15 - tot_14

print("🌍 1. Côté GLOBAL (historique_resume.csv) :")
print(f"   - Total le 14 Nov : {tot_14:,.0f}")
print(f"   - Total le 15 Nov : {tot_15:,.0f}")
print(f"   => Kworb a affiché une évolution de : {chute_globale:,.0f} streams\n")

# ==========================================
# 2. Analyse des CHANSONS
# ==========================================
df_songs = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")
df_14 = df_songs[df_songs['Date'] == date_14]

try:
    quit_streams = safe_float(df_14[df_14['Song Title'] == '* Quit']['Streams'].iloc[0])
except:
    quit_streams = 0

try:
    adore_streams = safe_float(df_14[df_14['Song Title'] == '* Adore']['Streams'].iloc[0])
except:
    adore_streams = 0

perte_chansons = quit_streams + adore_streams

print("🎵 2. Côté CHANSONS (historique_ariana.csv) :")
print(f"   - Streams de '* Quit' le 14 Nov  : {quit_streams:,.0f}")
print(f"   - Streams de '* Adore' le 14 Nov : {adore_streams:,.0f}")
print(f"   => Poids total des 2 chansons    : {perte_chansons:,.0f} streams\n")

# ==========================================
# 3. La Preuve
# ==========================================
difference_reelle = chute_globale + perte_chansons
print("⚖️ 3. LE BILAN (La Preuve Mathématique) :")
print(f"   Si on n'avait pas perdu ces deux chansons, le VRAI Daily de ce jour-là aurait été de : +{difference_reelle:,.0f} streams.")

if 25_000_000 <= difference_reelle <= 45_000_000:
    print("   ✅ Preuve établie : Cela correspond parfaitement à une journée normale d'écoutes pour Ariana ! Les deux suspectes sont confirmées.")
else:
    print("   ⚠️ Attention : Le chiffre final semble bizarre, il y a peut-être d'autres chansons impliquées.")