import pandas as pd
from datetime import timedelta

print("🔄 Lancement du décalage temporel (+1 jour à partir du 17 septembre 2026)...")

fichiers_a_corriger = [
    "historique_ariana.csv",
    "historique_resume.csv",
    "historique_ariana_listeners.csv"
]

for nom_fichier in fichiers_a_corriger:
    try:
        # On charge le fichier
        df = pd.read_csv(nom_fichier, encoding="utf-8-sig")
        
        # On convertit la colonne Date en vrai format de temps
        df['Date_obj'] = pd.to_datetime(df['Date'])
        
        # On cible TOUTES les dates à partir du 17 septembre 2026
        mask = df['Date_obj'] >= pd.to_datetime("2026-09-17")
        
        # On ajoute +1 jour !
        df.loc[mask, 'Date_obj'] = df.loc[mask, 'Date_obj'] + timedelta(days=1)
        
        # On réécrit le texte de la date et on sauvegarde
        df['Date'] = df['Date_obj'].dt.strftime('%Y-%m-%d')
        df = df.drop(columns=['Date_obj'])
        df.to_csv(nom_fichier, index=False, encoding="utf-8-sig")
        
        print(f"✅ {nom_fichier} a été décalé avec succès !")
    except Exception as e:
        print(f"❌ Erreur sur {nom_fichier} : {e}")

print("\n🎉 Opération terminée ! Le 17 septembre est maintenant vide, les données sont passées au 18.")