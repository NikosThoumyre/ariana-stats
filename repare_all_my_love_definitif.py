import pandas as pd
import numpy as np

print("🛠️ Réparation DÉFINITIVE de All My Love et des Homonymes...\n")

df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")

def safe_float(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return 0.0
    return float(str(val).replace(',', '').replace(' ', '').replace('+', ''))

df['Streams_num'] = df['Streams'].apply(safe_float)

# ==========================================
# 1. LE CAS SPÉCIAL : ALL MY LOVE
# ==========================================
# On force TOUTES les lignes qui contiennent 'All My Love' à être renommées proprement 
# SELON LEUR NOMBRE DE STREAMS (La seule vérité absolue !)
mask_aml = df['Song Title'].str.contains('All My Love', case=False, na=False)

# Si la ligne a plus de 70M, c'est FORCÉMENT le Remix
mask_remix = mask_aml & (df['Streams_num'] >= 70_000_000)
# Si elle a moins de 70M, c'est FORCÉMENT l'Originale
mask_original = mask_aml & (df['Streams_num'] < 70_000_000)

df.loc[mask_remix, 'Song Title'] = "* All My Love - Remix"
df.loc[mask_original, 'Song Title'] = "* All My Love"


# ==========================================
# 2. LA SÉCURITÉ POUR LES AUTRES HOMONYMES (One Last Time, Intro)
# ==========================================
df['Date_obj'] = pd.to_datetime(df['Date'])
df = df.sort_values(by=['Date_obj', 'Streams_num'], ascending=[True, False])

df['Occurence'] = df.groupby(['Date', 'Song Title']).cumcount()
df['Unique_ID'] = df['Song Title'] + "___" + df['Occurence'].astype(str)

df = df.sort_values(by=['Unique_ID', 'Date_obj'])

# ==========================================
# 3. RECALCUL PARFAIT DES DAILYS
# ==========================================
nouveau_daily = df.groupby('Unique_ID')['Streams_num'].diff()

def fix_first_day(row):
    if pd.isna(row['Vrai_Daily']):
        try:
            old_daily = float(str(row['Daily']).replace(',', '').replace('+', ''))
            if old_daily > 1_000_000_000 or old_daily < -1_000_000_000:
                return 0
            return old_daily
        except:
            return 0
    return row['Vrai_Daily']

df['Vrai_Daily'] = nouveau_daily
df['Daily'] = df.apply(fix_first_day, axis=1).astype(int)

# 4. Nettoyage et sauvegarde
df = df.sort_values(by=['Date_obj', 'Streams_num'], ascending=[True, False])
df['Streams'] = df['Streams_num'].astype(int)
df = df[['Song Title', 'Streams', 'Daily', 'Date']]
df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")

print("✅ TOUT EST RÉPARÉ ! All My Love est séparée pour toujours, et les homonymes sont sécurisés.")