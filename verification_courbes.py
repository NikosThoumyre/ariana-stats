import pandas as pd

print("🔍 ANALYSE DE COMPORTEMENT : 'Quit' et 'Adore' avant leur suppression...\n")

df = pd.read_csv("historique_ariana.csv", encoding="utf-8-sig")

# On prend les 20 jours avant le 15 novembre
d_start = "2026-10-25"
d_end = "2026-11-14"
df_cible = df[(df['Date'] >= d_start) & (df['Date'] <= d_end)].copy()

chansons = ['* Quit', '* Adore']

for c in chansons:
    print(f"📊 Comportement de {c} sur ses 20 derniers jours :")
    df_c = df_cible[df_cible['Song Title'] == c].sort_values('Date')
    
    if df_c.empty:
        print("   (Aucune donnée trouvée)")
        continue
        
    jours_a_zero = 0
    for idx, row in df_c.iterrows():
        try:
            daily = int(str(row['Daily']).replace(',','').replace('+',''))
            # On affiche juste les jours où le Daily était de 0 (les fameux "plateaux")
            if daily == 0:
                jours_a_zero += 1
        except:
            pass
            
    total_jours = len(df_c)
    pourcentage_plat = (jours_a_zero / total_jours) * 100
    
    print(f"   - Jours tracés : {total_jours}")
    print(f"   - Jours avec un Daily à 0 (Courbe plate) : {jours_a_zero}")
    print(f"   => La courbe était 'plate' {pourcentage_plat:.1f}% du temps !\n")