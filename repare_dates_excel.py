import pandas as pd

print("🔧 Réparation des formats de dates abîmés par Excel...")

fichiers = [
    "historique_resume.csv",
    "historique_ariana.csv",
    "historique_ariana_listeners.csv"
]

for fichier in fichiers:
    try:
        # On lit le fichier
        df = pd.read_csv(fichier, encoding="utf-8-sig")
        
        # On dit à Python de transformer les textes en dates, en lui précisant que le jour peut être en premier (dayfirst=True)
        # format='mixed' permet de gérer les lignes où Excel a mis DD/MM/YYYY et celles où c'est resté YYYY-MM-DD
        df['Date_obj'] = pd.to_datetime(df['Date'], dayfirst=True, format='mixed')
        
        # On force la réécriture de la date en texte parfait : YYYY-MM-DD
        df['Date'] = df['Date_obj'].dt.strftime('%Y-%m-%d')
        
        df = df.drop(columns=['Date_obj'])
        df.to_csv(fichier, index=False, encoding="utf-8-sig")
        print(f"✅ Dates parfaitement restaurées dans {fichier} !")
    except Exception as e:
        print(f"⚠️ Impossible de réparer {fichier} (Peut-être qu'il n'en avait pas besoin). Erreur : {e}")

print("\n🎉 Terminé ! Ton ordinateur parle de nouveau le même langage que ton code.")