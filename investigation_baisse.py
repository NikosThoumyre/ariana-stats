import pandas as pd

print("🔍 DÉBUT DE L'ENQUÊTE : Analyse de la chute des streams...\n")

def safe_float(val):
    if pd.isna(val) or str(val).strip() in ['-', '']: return 0.0
    return float(str(val).replace(',', '').replace(' ', '').replace('+', ''))

# ==========================================
# 1. ANALYSE DU TOTAL GLOBAL
# ==========================================
print("🌍 1. VÉRIFICATION DE LA COURBE GLOBALE...")
df_res = pd.read_csv("historique_resume.csv", encoding="utf-8-sig")
df_str = df_res[df_res['Catégorie'] == 'Streams'].sort_values('Date').reset_index(drop=True)

date_chute = None
date_veille = None
perte_totale = 0

last_date = df_str.iloc[0]['Date']
last_total = safe_float(df_str.iloc[0]['Total'])

for i in range(1, len(df_str)):
    curr_date = df_str.iloc[i]['Date']
    curr_total = safe_float(df_str.iloc[i]['Total'])
    diff = curr_total - last_total
    
    if diff < -500_000: # Si la baisse est d'au moins 500k
        print(f"🚨 CHUTE DÉTECTÉE entre le {last_date} et le {curr_date} !")
        print(f"   - Total le {last_date} : {last_total:,.0f}")
        print(f"   - Total le {curr_date} : {curr_total:,.0f}")
        print(f"   => Perte globale de : {diff:,.0f} streams\n")
        date_chute = curr_date
        date_veille = last_date
        perte_totale = diff
        
    last_date = curr_date
    last_total = curr_total

# ==========================================
# 2 & 3. VÉRIFICATION DES CHANSONS (Si une chute a été trouvée)
# ==========================================
if date_chute:
    print(f"🧮 2. VÉRIFICATION DE L'ADDITION POUR LE {date_chute}...")
    df_songs = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")
    
    # Vérification de l'addition
    df_chute = df_songs[df_songs['Date'] == date_chute]
    somme_calculee = df_chute['Streams'].apply(safe_float).sum()
    kworb_total = safe_float(df_str[df_str['Date'] == date_chute].iloc[0]['Total'])
    
    print(f"   - Addition de toutes les chansons : {somme_calculee:,.0f}")
    print(f"   - Total affiché par Kworb         : {kworb_total:,.0f}")
    ecart = somme_calculee - kworb_total
    if ecart == 0:
        print("   => VRAI : L'addition correspond parfaitement au chiffre de Kworb.")
    else:
        print(f"   => FAUX : Il y a un écart de {ecart:,.0f} streams entre le total Kworb et l'addition des chansons !\n")

    # Recherche des coupables
    print(f"\n🎵 3. RECHERCHE DES COUPABLES (entre le {date_veille} et le {date_chute})...")
    df_veille = df_songs[df_songs['Date'] == date_veille].copy()
    
    # Création d'IDs uniques
    df_veille['Unique_ID'] = df_veille['Song Title'] + "___" + df_veille.groupby('Song Title').cumcount().astype(str)
    df_chute_uid = df_chute.copy()
    df_chute_uid['Unique_ID'] = df_chute_uid['Song Title'] + "___" + df_chute_uid.groupby('Song Title').cumcount().astype(str)
    
    dict_veille = dict(zip(df_veille['Unique_ID'], df_veille['Streams'].apply(safe_float)))
    dict_chute = dict(zip(df_chute_uid['Unique_ID'], df_chute_uid['Streams'].apply(safe_float)))
    
    chansons_baisse = []
    for uid, stream_actuel in dict_chute.items():
        if uid in dict_veille:
            stream_veille = dict_veille[uid]
            if stream_actuel < stream_veille:
                chansons_baisse.append({
                    'Titre': uid.split('___')[0],
                    'Perte': stream_actuel - stream_veille,
                    'Veille': stream_veille, 'Actuel': stream_actuel
                })
                
    if chansons_baisse:
        print("   📉 Chansons dont les streams ont diminué :")
        for c in chansons_baisse:
            print(f"      - {c['Titre']} : {c['Perte']:,.0f} (passé de {c['Veille']:,.0f} à {c['Actuel']:,.0f})")
    else:
        print("   ✅ Aucune chanson n'a vu ses streams baisser.")
        
    disparues = set(dict_veille.keys()) - set(dict_chute.keys())
    if disparues:
        print("\n   👻 Chansons qui ont totalement DISPARU ce jour-là :")
        for d in disparues:
            print(f"      - {d.split('___')[0]} (faisait {dict_veille[d]:,.0f} streams la veille)")
else:
    print("✅ Aucune baisse globale majeure détectée dans l'historique !")