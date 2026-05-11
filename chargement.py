import pandas as pd
from datetime import datetime, timedelta
import os
import requests
from bs4 import BeautifulSoup

url_songs = "https://kworb.net/spotify/artist/66CXWjxzNUsdJxJ2JdwvnR_songs.html"
url_listeners = "https://kworb.net/spotify/listeners.html"

# Nos 4 fichiers de base de données
nom_fichier_chansons = "historique_ariana.csv"
nom_fichier_resume = "historique_resume.csv"
nom_fichier_listeners = "historique_ariana_listeners.csv"
nom_fichier_classement = "classement_listeners_jour.csv"

print("Recherche de nouvelles données sur Kworb...")

# --- A. LECTURE DE LA PAGE CHANSONS ---
response_songs = requests.get(url_songs)
tableaux_songs = pd.read_html(response_songs.text)

df_resume_kworb = tableaux_songs[0].copy() # Le petit tableau (Total, Solo, etc.)
df_chansons = tableaux_songs[1].copy()     # Le grand tableau des chansons
df_filtre_chansons = df_chansons[['Song Title', 'Streams', 'Daily']].copy()

chanson_repere = df_filtre_chansons.iloc[0]['Song Title']
streams_actuels = str(df_filtre_chansons.iloc[0]['Streams'])

maj_chansons_necessaire = False
init_fichiers_annexes = False
nouvelle_date_str = ""

# --- B. LOGIQUE DES DATES (La machine à voyager dans le temps) ---
if os.path.exists(nom_fichier_chansons):
    df_existant = pd.read_csv(nom_fichier_chansons)
    derniere_date_str = df_existant['Date'].max()
    df_derniere_date = df_existant[df_existant['Date'] == derniere_date_str]
    
    try:
        streams_enregistres = str(df_derniere_date[df_derniere_date['Song Title'] == chanson_repere].iloc[0]['Streams'])
    except:
        streams_enregistres = "0"
        
    if streams_actuels == streams_enregistres:
        print("⏳ Les streams des chansons n'ont pas changé.")
        nouvelle_date_str = derniere_date_str
        # Si on a ajouté l'idée des Listeners aujourd'hui, on force la création des fichiers manquants
        if not os.path.exists(nom_fichier_resume) or not os.path.exists(nom_fichier_listeners):
            init_fichiers_annexes = True
    else:
        derniere_date_obj = datetime.strptime(derniere_date_str, "%Y-%m-%d")
        nouvelle_date_str = (derniere_date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
        maj_chansons_necessaire = True
else:
    soup = BeautifulSoup(response_songs.text, 'html.parser')
    element_date = soup.find(string=lambda x: x and 'Last updated:' in x)
    date_kworb_obj = datetime.strptime(element_date.replace('Last updated:', '').strip(), "%Y/%m/%d")
    nouvelle_date_str = (date_kworb_obj - timedelta(days=1)).strftime("%Y-%m-%d")
    maj_chansons_necessaire = True

# --- C. SAUVEGARDE DE TOUTES LES DONNÉES ---
if maj_chansons_necessaire or init_fichiers_annexes:
    print(f"🔄 Traitement des données pour la date : {nouvelle_date_str}")
    
    # 1. Sauvegarde des Chansons
    if maj_chansons_necessaire:
        df_filtre_chansons['Date'] = nouvelle_date_str
        df_filtre_chansons.to_csv(nom_fichier_chansons, mode='a' if os.path.exists(nom_fichier_chansons) else 'w', header=not os.path.exists(nom_fichier_chansons), index=False, encoding='utf-8-sig')
        print("✅ Chansons mises à jour.")
    
    # 2. Sauvegarde du Résumé (Streams Total, Lead, Solo...)
    df_resume_kworb.rename(columns={df_resume_kworb.columns[0]: 'Catégorie'}, inplace=True)
    df_resume_kworb['Date'] = nouvelle_date_str
    df_resume_kworb.to_csv(nom_fichier_resume, mode='a' if os.path.exists(nom_fichier_resume) else 'w', header=not os.path.exists(nom_fichier_resume), index=False, encoding='utf-8-sig')
    print("✅ Résumé Artiste (Total/Solo) mis à jour.")
    
    # 3. Récupération de la page Listeners
    print("🌍 Récupération du classement mondial des auditeurs...")
    response_listeners = requests.get(url_listeners)
    df_listeners = pd.read_html(response_listeners.text)[0]
    
    # Sauvegarde du grand classement (On écrase l'ancien, on n'a besoin que du classement du jour !)
    df_listeners.to_csv(nom_fichier_classement, index=False, encoding='utf-8-sig')
    
    # Extraction et sauvegarde de l'historique d'Ariana Grande
    df_ariana_list = df_listeners[df_listeners['Artist'] == 'Ariana Grande'].copy()
    if not df_ariana_list.empty:
        df_ariana_list['Date'] = nouvelle_date_str
        df_ariana_list.to_csv(nom_fichier_listeners, mode='a' if os.path.exists(nom_fichier_listeners) else 'w', header=not os.path.exists(nom_fichier_listeners), index=False, encoding='utf-8-sig')
        print("✅ Historique des Listeners mis à jour.")
    
    print("🎉 Toutes les bases de données sont prêtes !")
else:
    print("✅ Tout est déjà à jour. Aucune action requise.")