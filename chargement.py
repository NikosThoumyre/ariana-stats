import pandas as pd
from datetime import datetime, timedelta
import os
import requests
from bs4 import BeautifulSoup

url_songs = "https://kworb.net/spotify/artist/66CXWjxzNUsdJxJ2JdwvnR_songs.html"
url_listeners = "https://kworb.net/spotify/listeners.html"

nom_fichier_chansons = "historique_ariana.csv"
nom_fichier_resume = "historique_resume.csv"
nom_fichier_listeners = "historique_ariana_listeners.csv"
nom_fichier_classement = "classement_listeners_jour.csv"

print("Recherche de nouvelles données sur Kworb...")

# ==========================================
# PARTIE 1 : VÉRIFICATION DES STREAMS
# ==========================================
response_songs = requests.get(url_songs)
tableaux_songs = pd.read_html(response_songs.text)

df_resume_kworb = tableaux_songs[0].copy()
df_chansons = tableaux_songs[1].copy()
df_filtre_chansons = df_chansons[['Song Title', 'Streams', 'Daily']].copy()

chanson_repere = df_filtre_chansons.iloc[0]['Song Title']
streams_actuels = str(df_filtre_chansons.iloc[0]['Streams'])

maj_chansons = False
if os.path.exists(nom_fichier_chansons):
    df_existant = pd.read_csv(nom_fichier_chansons)
    date_derniers_streams_str = df_existant['Date'].max()
    df_derniere_date = df_existant[df_existant['Date'] == date_derniers_streams_str]
    try:
        streams_enregistres = str(df_derniere_date[df_derniere_date['Song Title'] == chanson_repere].iloc[0]['Streams'])
    except:
        streams_enregistres = "0"

    if streams_actuels != streams_enregistres:
        nouvelle_date_streams_obj = datetime.strptime(date_derniers_streams_str, "%Y-%m-%d") + timedelta(days=1)
        nouvelle_date_streams_str = nouvelle_date_streams_obj.strftime("%Y-%m-%d")
        maj_chansons = True
else:
    # 1ère création (au cas où)
    soup = BeautifulSoup(response_songs.text, 'html.parser')
    element_date = soup.find(string=lambda x: x and 'Last updated:' in x)
    date_kworb_obj = datetime.strptime(element_date.replace('Last updated:', '').strip(), "%Y/%m/%d")
    nouvelle_date_streams_str = (date_kworb_obj - timedelta(days=1)).strftime("%Y-%m-%d")
    maj_chansons = True

if maj_chansons:
    df_filtre_chansons['Date'] = nouvelle_date_streams_str
    df_filtre_chansons.to_csv(nom_fichier_chansons, mode='a' if os.path.exists(nom_fichier_chansons) else 'w', header=not os.path.exists(nom_fichier_chansons), index=False, encoding='utf-8-sig')
    
    df_resume_kworb.rename(columns={df_resume_kworb.columns[0]: 'Catégorie'}, inplace=True)
    df_resume_kworb['Date'] = nouvelle_date_streams_str
    df_resume_kworb.to_csv(nom_fichier_resume, mode='a' if os.path.exists(nom_fichier_resume) else 'w', header=not os.path.exists(nom_fichier_resume), index=False, encoding='utf-8-sig')
    print(f"✅ STREAMS : Nouvelles données du {nouvelle_date_streams_str} enregistrées.")
else:
    print("⏳ STREAMS : Pas de changement. On attend.")


# ==========================================
# PARTIE 2 : VÉRIFICATION DES LISTENERS
# ==========================================
response_listeners = requests.get(url_listeners)
df_listeners = pd.read_html(response_listeners.text)[0]
df_ariana_list_actuel = df_listeners[df_listeners['Artist'] == 'Ariana Grande'].copy()

if not df_ariana_list_actuel.empty:
    listeners_actuels = str(df_ariana_list_actuel.iloc[0]['Listeners'])
    maj_listeners = False
    
    if os.path.exists(nom_fichier_listeners):
        df_list_existant = pd.read_csv(nom_fichier_listeners)
        date_derniers_listeners_str = df_list_existant['Date'].max()
        df_dernier_list = df_list_existant[df_list_existant['Date'] == date_derniers_listeners_str]
        listeners_enregistres = str(df_dernier_list.iloc[0]['Listeners'])
        
        # Le déclencheur : Les chiffres des Listeners sont différents du fichier !
        if listeners_actuels != listeners_enregistres:
            nouvelle_date_list_obj = datetime.strptime(date_derniers_listeners_str, "%Y-%m-%d") + timedelta(days=1)
            nouvelle_date_list_str = nouvelle_date_list_obj.strftime("%Y-%m-%d")
            maj_listeners = True
    else:
        nouvelle_date_list_str = nouvelle_date_streams_str if 'nouvelle_date_streams_str' in locals() else datetime.now().strftime("%Y-%m-%d")
        maj_listeners = True
        
    if maj_listeners:
        df_ariana_list_actuel['Date'] = nouvelle_date_list_str
        df_ariana_list_actuel.to_csv(nom_fichier_listeners, mode='a' if os.path.exists(nom_fichier_listeners) else 'w', header=not os.path.exists(nom_fichier_listeners), index=False, encoding='utf-8-sig')
        df_listeners.to_csv(nom_fichier_classement, index=False, encoding='utf-8-sig')
        print(f"✅ LISTENERS : Nouvelles données du {nouvelle_date_list_str} enregistrées.")
    else:
        print("⏳ LISTENERS : Pas de changement. On attend.")
else:
    print("⚠️ Ariana Grande introuvable dans le classement Listeners.")