import pandas as pd

print("🩺 Opération Chirurgicale ciblée : Réparation de 'The Way' et 'Supernatural'...\n")

# 💡 CORRECTION : On ouvre TOUT en texte pur pour éviter les crashs (dtype=str)
df = pd.read_csv("historique_ariana.csv", dtype=str, encoding="utf-8-sig")

def safe_int(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return 0
    return int(float(str(val).replace(',', '').replace(' ', '').replace('+', '')))

df['Occurence'] = df.groupby(['Date', 'Song Title']).cumcount()
df['Unique_ID'] = df['Song Title'] + "___" + df['Occurence'].astype(str)
df['Date_obj'] = pd.to_datetime(df['Date'])

lignes_reparees = []

# ==========================================
# 1. CAS YOURS TRULY (The Way le 6 août)
# ==========================================
print("-> Traitement de 'The Way' (Trou du 6 août)...")
uid_way = "The Way___0"
d5_way = pd.to_datetime("2026-08-05")
d6_way = pd.to_datetime("2026-08-06")
d7_way = pd.to_datetime("2026-08-07")

try:
    s5 = safe_int(df.loc[(df['Unique_ID'] == uid_way) & (df['Date_obj'] == d5_way), 'Streams'].iloc[0])
    s7 = safe_int(df.loc[(df['Unique_ID'] == uid_way) & (df['Date_obj'] == d7_way), 'Streams'].iloc[0])
    
    # On calcule la moyenne parfaite pour le 6 août
    mid_s = (s5 + s7) // 2
    daily_6 = mid_s - s5
    daily_7 = s7 - mid_s
    
    # On prépare la ligne fantôme
    lignes_reparees.append({
        'Song Title': "The Way",
        'Streams': str(mid_s),
        'Daily': str(daily_6),
        'Date': "2026-08-06",
        'Date_obj': d6_way,
        'Unique_ID': uid_way
    })
    
    # On lisse le Daily du 7 août
    df.loc[(df['Unique_ID'] == uid_way) & (df['Date_obj'] == d7_way), 'Daily'] = str(daily_7)
except Exception as e:
    print(f"Erreur The Way : {e}")


# ==========================================
# 2. CAS ETERNAL SUNSHINE (Supernatural le 17 et 18 août)
# ==========================================
print("-> Traitement de 'Supernatural' (Pic du 17 et 18 août)...")
uid_sup = "supernatural___0"
d16_sup = pd.to_datetime("2026-08-16")
d17_sup = pd.to_datetime("2026-08-17")
d18_sup = pd.to_datetime("2026-08-18")
d19_sup = pd.to_datetime("2026-08-19")

try:
    s16 = safe_int(df.loc[(df['Unique_ID'] == uid_sup) & (df['Date_obj'] == d16_sup), 'Streams'].iloc[0])
    s19 = safe_int(df.loc[(df['Unique_ID'] == uid_sup) & (df['Date_obj'] == d19_sup), 'Streams'].iloc[0])
    
    # On divise la progression sur les 3 jours
    daily_moyen = (s19 - s16) // 3
    
    s17 = s16 + daily_moyen
    s18 = s17 + daily_moyen
    
    # On écrase les 2 hallucinations de Kworb par les vrais chiffres lissés (format texte)
    df.loc[(df['Unique_ID'] == uid_sup) & (df['Date_obj'] == d17_sup), 'Streams'] = str(s17)
    df.loc[(df['Unique_ID'] == uid_sup) & (df['Date_obj'] == d17_sup), 'Daily'] = str(daily_moyen)
    
    df.loc[(df['Unique_ID'] == uid_sup) & (df['Date_obj'] == d18_sup), 'Streams'] = str(s18)
    df.loc[(df['Unique_ID'] == uid_sup) & (df['Date_obj'] == d18_sup), 'Daily'] = str(daily_moyen)
    
    # On ajuste le Daily du 19 (la retombée)
    daily_19 = s19 - s18
    df.loc[(df['Unique_ID'] == uid_sup) & (df['Date_obj'] == d19_sup), 'Daily'] = str(daily_19)

except Exception as e:
    print(f"Erreur Supernatural : {e}")

# ==========================================
# 3. SAUVEGARDE
# ==========================================
if lignes_reparees:
    # On supprime la ligne du 6 aout si elle existait sous une forme corrompue
    df = df[~((df['Unique_ID'] == uid_way) & (df['Date_obj'] == d6_way))]
    df = pd.concat([df, pd.DataFrame(lignes_reparees)], ignore_index=True)

# On recalcule en nombres entiers juste pour le tri final !
df['Streams_num'] = df['Streams'].apply(safe_int)
df = df.sort_values(by=['Date_obj', 'Streams_num'], ascending=[True, False])

df = df[['Song Title', 'Streams', 'Daily', 'Date']]
df.to_csv("historique_ariana.csv", index=False, encoding="utf-8-sig")

print("✅ Opération terminée ! Les deux anomalies ont été effacées.")