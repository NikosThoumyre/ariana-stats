import pandas as pd
from datetime import timedelta

print("🔄 Lancement du décalage temporel (+1 jour à partir du 16 août)...")

fichiers_a_corriger = [
    "historique_ariana.csv",
    "historique_resume.csv",
    "historique_ariana_listeners.csv"
]

for nom_fichier in fichiers_a_corriger:
    try:
        # 1. On charge le fichier
        df = pd.read_csv(nom_fichier, encoding="utf-8-sig")
        
        # 2. On convertit la colonne Date en "vrai" format date mathématique
        df['Date_obj'] = pd.to_datetime(df['Date'])
        
        # 3. On sélectionne TOUTES les dates à partir du 16 août 2026
        mask = df['Date_obj'] >= pd.to_datetime("2026-08-16")
        
        # 4. On ajoute +1 jour à toutes ces dates !
        df.loc[mask, 'Date_obj'] = df.loc[mask, 'Date_obj'] + timedelta(days=1)
        
        # 5. On écrase l'ancienne colonne Date avec le nouveau texte (YYYY-MM-DD)
        df['Date'] = df['Date_obj'].dt.strftime('%Y-%m-%d')
        
        # 6. On nettoie et on sauvegarde
        df = df.drop(columns=['Date_obj'])
        df.to_csv(nom_fichier, index=False, encoding="utf-8-sig")
        
        print(f"✅ {nom_fichier} a été décalé avec succès !")
    except Exception as e:
        print(f"❌ Erreur sur {nom_fichier} : {e}")

print("\n🎉 Opération terminée ! Le 16 août est maintenant vide, et les jours suivants ont repris leur vraie place.")