import pandas as pd
from datetime import datetime
import json
import html
import math

# --- FONCTIONS UTILITAIRES ---
def rendre_cliquable(row, colonne_titre, uid_col='Unique_ID'):
    titre = row[colonne_titre]
    uid_safe = row[uid_col].replace("'", "\\'").replace('"', '&quot;')
    titre_affiche = html.escape(str(titre))
    return f'<a href="javascript:void(0)" onclick="afficherDetailsChanson(\'{uid_safe}\')" class="song-link" title="Voir les graphiques de {titre_affiche}">{titre_affiche}</a>'

def format_en(x):
    if pd.isna(x) or str(x).strip() == '-': return '-'
    try:
        clean_x = str(x).replace(',', '').replace(' ', '').replace('+', '')
        return f"{int(float(clean_x)):,}"
    except:
        return str(x)

def format_evo(diff):
    if pd.isna(diff) or str(diff).strip() == '-': return '-'
    try:
        clean_val = str(diff).replace(',', '').replace(' ', '').replace('+', '')
        val = int(float(clean_val))
        if val > 0:
            return f"<span style='color: #28a745; font-weight: bold;'>+{val:,}</span>"
        elif val < 0:
            return f"<span style='color: #dc3545; font-weight: bold;'>{val:,}</span>"
        else:
            return "0"
    except:
        return str(diff)

def clean_compare(val1, val2):
    if pd.isna(val1) or pd.isna(val2): return False
    try:
        v1 = int(float(str(val1).replace(',', '').replace(' ', '').replace('+', '')))
        v2 = int(float(str(val2).replace(',', '').replace(' ', '').replace('+', '')))
        return v1 == v2
    except:
        return str(val1).strip() == str(val2).strip()

def resolve_track_id(t):
    # Si on a déjà forcé un Occurrence (ex: Intro___1), on le garde, sinon on met ___0 par défaut
    return t if "___" in t else f"{t}___0"

# ==========================================
# 0. LE DICTIONNAIRE DES ALBUMS (Masterlist)
# ==========================================
ALBUM_TRACKS = {
    "Yours Truly": [
        "Honeymoon Avenue", "Baby I___0", "Right There", "Tattooed Heart", "Lovin' It", "Piano",
        "Daydreamin'", "The Way", "You'll Never Know", "Almost Is Never Enough", "* Popular Song", "Better Left Unsaid"
    ],
    "Yours Truly (Tenth Anniversary Edition)": [
        "Honeymoon Avenue", "Baby I___0", "Right There", "Tattooed Heart", "Lovin' It", "Piano",
        "Daydreamin'", "The Way", "You'll Never Know", "Almost Is Never Enough", "* Popular Song", "Better Left Unsaid",
        "Honeymoon Avenue - Live from London", "Daydreamin' - Live from London", "Baby I - Live from London",
        "Tattooed Heart - Live from London", "Right There - Live from London (feat. Big Sean)", "The Way - Live from London (feat. Mac Miller)"
    ],
    "Christmas Kisses": [
        "Last Christmas", "Love Is Everything", "Snow In California", "Santa Baby", "Santa Tell Me"
    ],
    "My Everything": [
        "Intro___0", "Problem", "One Last Time___0", "Why Try", "Break Free", "Best Mistake", "Be My Baby",
        "Break Your Heart Right Back", "Love Me Harder", "Just A Little Bit Of Your Heart", "Hands On Me", "My Everything"
    ],
    "My Everything (Deluxe)": [
        "Intro___0", "Problem", "One Last Time___0", "Why Try", "Break Free", "Best Mistake", "Be My Baby",
        "Break Your Heart Right Back", "Love Me Harder", "Just A Little Bit Of Your Heart", "Hands On Me", "My Everything",
        "* Bang Bang", "Only 1", "You Don't Know Me"
    ],
    "My Everything (Tenth Anniversary Edition)": [
        "Intro___0", "Problem", "One Last Time___0", "Why Try", "Break Free", "Best Mistake", "Be My Baby",
        "Break Your Heart Right Back", "Love Me Harder", "Just A Little Bit Of Your Heart", "Hands On Me", "My Everything",
        "* Bang Bang", "Only 1", "You Don't Know Me", "Cadillac Song", "Too Close"
    ],
    "Christmas & Chill": [
        "Intro___1", "Wit It This Christmas", "December", "Not Just On Christmas", "True Love", "Winter Things"
    ],
    "Dangerous Woman": [
        "Moonlight", "Dangerous Woman", "Be Alright", "Into You", "Side To Side", "Let Me Love You", "Greedy",
        "Leave Me Lonely", "Everyday", "Bad Decisions", "Thinking Bout You" 
    ],
    "Dangerous Woman (Deluxe)": [
        "Moonlight", "Dangerous Woman", "Be Alright", "Into You", "Side To Side", "Let Me Love You", "Greedy",
        "Leave Me Lonely", "Everyday", "Sometimes", "I Don't Care", "Bad Decisions", "Touch It",
        "Knew Better / Forever Boy", "Thinking Bout You", "Step On Up", "Jason's Song (Gave It Away)", "Focus"
    ],
    "Dangerous Woman (Tenth Anniversary Edition)": [
        "Moonlight", "Dangerous Woman", "Be Alright", "Into You", "Side To Side", "Let Me Love You", "Greedy",
        "Leave Me Lonely", "Everyday", "Sometimes", "I Don't Care", "Bad Decisions", "Touch It",
        "Knew Better / Forever Boy", "Thinking Bout You", "Step On Up", "Jason's Song (Gave It Away)", "Focus",
        "Knew Better Part Two"
    ],
    "Sweetener": [
        "raindrops (an angel cried)", "blazed (feat. Pharrell Williams)", "the light is coming (feat. Nicki Minaj)",
        "R.E.M", "God is a woman", "sweetener", "successful", "everytime", "breathin", "no tears left to cry",
        "borderline (feat. Missy Elliott)", "better off", "goodnight n go", "pete davidson", "get well soon"
    ],
    "thank u, next": [
        "imagine", "needy", "NASA", "bloodline", "fake smile", "bad idea", "make up", "ghostin", "in my head",
        "7 rings", "thank u, next", "break up with your girlfriend, i'm bored"
    ],
    "k bye for now (swt live)": [
        "raindrops (an angel cried) - live", "god is a woman - live", "bad idea - live",
        "break up with your girlfriend, i'm bored - live", "r.e.m - live", "be alright - live", "sweetener - live",
        "successful - live", "side to side - live", "7 rings - live", "love me harder - live", "breathin - live",
        "needy - live", "fake smile - live", "make up - live", "right there - live", "you'll never know - live",
        "break your heart right back - live", "nasa - live", "tattooed heart - live", "only 1 - live",
        "goodnight n go - live", "get well soon - live", "in my head interlude - live", "everyday - live",
        "the light is coming - live", "into you - live", "my heart belongs to daddy - live", "dangerous woman - live",
        "break free - live", "no tears left to cry - live", "thank u, next - live"
    ],
    "Positions": [
        "shut up", "34+35", "motive (with Doja Cat)", "just like magic", "off the table (with The Weeknd)",
        "six thirty", "safety net (feat. Ty Dolla $ign)", "my hair", "nasty", "west side", "love language",
        "positions", "obvious", "pov"
    ],
    "Positions (Deluxe)": [
        "shut up", "34+35", "motive (with Doja Cat)", "just like magic", "off the table (with The Weeknd)",
        "six thirty", "safety net (feat. Ty Dolla $ign)", "my hair", "nasty", "west side", "love language",
        "positions", "obvious", "pov", "someone like u - interlude", "test drive",
        "34+35 Remix (feat. Doja Cat, Megan Thee Stallion) - Remix", "worst behavior", "main thing"
    ],
    "eternal sunshine": [
        "intro (end of the world)", "bye", "don't wanna break up again", "Saturn Returns Interlude",
        "eternal sunshine", "supernatural", "true story", "the boy is mine", "yes, and?",
        "we can't be friends (wait for your love)", "i wish i hated you", "imperfect for you", "ordinary things (feat. Nonna)"
    ],
    "eternal sunshine (deluxe: brighter days ahead)": [
        "intro (end of the world)", "bye", "don't wanna break up again", "Saturn Returns Interlude",
        "eternal sunshine", "supernatural", "true story", "the boy is mine", "yes, and?",
        "we can't be friends (wait for your love)", "i wish i hated you", "imperfect for you", "ordinary things (feat. Nonna)",
        "intro (end of the world) - extended", "yes, and? (with Mariah Carey) - Remix", "supernatural (with Troye Sivan) - remix",
        "the boy is mine (with Brandy, Monica) - Remix", "twilight zone", "warm", "dandelion", "past life", "Hampstead"
    ],
    "Petal": [
        "Hate That I Made You Love Me"
    ]
}


# ==========================================
# 1. DONNÉES CHANSONS & CALCULS
# ==========================================
df = pd.read_csv("historique_ariana.csv")
df['Occurence'] = df.groupby(['Date', 'Song Title']).cumcount()
df['Unique_ID'] = df['Song Title'] + "___" + df['Occurence'].astype(str)
df['Streams_num'] = pd.to_numeric(df['Streams'], errors='coerce').fillna(0)
df['Daily_num'] = pd.to_numeric(df['Daily'], errors='coerce').fillna(0)

dates = sorted(df['Date'].unique(), reverse=True)
date_jour = dates[0]
df_jour = df[df['Date'] == date_jour].copy()

# Base pour les évolutions (Hier vs Aujourd'hui)
if len(dates) >= 2:
    df_evolution = pd.merge(df_jour, df[df['Date'] == dates[1]], on=['Song Title', 'Occurence'], suffixes=('_Aujourdhui', '_Hier'))
    df_evolution['Différence'] = df_evolution['Daily_num_Aujourdhui'] - df_evolution['Daily_num_Hier']
    df_affichage_evo = df_evolution[['Song Title', 'Daily_num_Aujourdhui', 'Daily_num_Hier', 'Différence', 'Unique_ID_Aujourdhui']].copy()
    df_affichage_evo = df_affichage_evo.rename(columns={'Unique_ID_Aujourdhui': 'Unique_ID'})
else:
    df_affichage_evo = pd.DataFrame(columns=['Song Title', 'Daily_num_Aujourdhui', 'Daily_num_Hier', 'Différence', 'Unique_ID'])

# --- Global ---
df_global = df_jour.copy()
df_global['Chanson'] = df_global.apply(lambda r: rendre_cliquable(r, 'Song Title'), axis=1)
df_global['Streams '] = df_global['Streams_num'].apply(format_en)
df_global['Daily '] = df_global['Daily_num'].apply(format_en)
html_tableau_global = df_global[['Chanson', 'Streams ', 'Daily ']].fillna('-').to_html(index=False, classes="table-chansons sortable auto-index", escape=False)

# --- Évolution ---
if len(dates) >= 2:
    df_evo_visuel = df_affichage_evo.copy()
    df_evo_visuel['Chanson'] = df_evo_visuel.apply(lambda r: rendre_cliquable(r, 'Song Title'), axis=1)
    df_evo_visuel['Daily Actuel '] = df_evo_visuel['Daily_num_Aujourdhui'].apply(format_en)
    df_evo_visuel['Daily Veille '] = df_evo_visuel['Daily_num_Hier'].apply(format_en)
    df_evo_visuel['Évolution (Différence)'] = df_evo_visuel['Différence'].apply(format_evo)
    df_evo_visuel = df_evo_visuel[['Chanson', 'Daily Actuel ', 'Daily Veille ', 'Évolution (Différence)']]
    html_tableau_evo = df_evo_visuel.to_html(index=False, classes="table-chansons sortable auto-index", escape=False)
else:
    html_tableau_evo = "<p style='text-align:center;'><em>⏳ Reviens à la prochaine mise à jour pour voir les évolutions !</em></p>"

# --- Prédiction ---
date_obj = datetime.strptime(date_jour, "%Y-%m-%d")
jours_restants = (datetime(date_obj.year, 12, 31) - date_obj).days
df_pred = df_jour.copy()
df_pred['Prédiction'] = df_pred['Streams_num'] + (df_pred['Daily_num'] * jours_restants)
df_pred = df_pred.sort_values(by='Prédiction', ascending=False)
df_pred['Chanson'] = df_pred.apply(lambda r: rendre_cliquable(r, 'Song Title'), axis=1)
df_pred['Streams Actuels '] = df_pred['Streams_num'].apply(format_en)
df_pred['Daily Actuel '] = df_pred['Daily_num'].apply(format_en)
df_pred[f'Prédiction (au 31 Déc {date_obj.year})'] = df_pred['Prédiction'].apply(format_en)
df_pred_final = df_pred[['Chanson', 'Streams Actuels ', 'Daily Actuel ', f'Prédiction (au 31 Déc {date_obj.year})']]
html_tableau_pred = df_pred_final.to_html(index=False, classes="table-chansons sortable auto-index", escape=False)

# --- Milestones & Overtakes ---
df_ms = df_jour[df_jour['Daily_num'] > 0].copy()
df_ms['Next Milestone'] = df_ms['Streams_num'].apply(lambda s: math.ceil((s + 1) / 100_000_000) * 100_000_000)
df_ms['Remaining'] = df_ms['Next Milestone'] - df_ms['Streams_num']
df_ms['Days Away'] = (df_ms['Remaining'] / df_ms['Daily_num']).apply(math.ceil)
df_ms = df_ms.sort_values('Days Away').head(20)
df_ms['Chanson'] = df_ms.apply(lambda r: rendre_cliquable(r, 'Song Title'), axis=1)
df_ms['Target '] = df_ms['Next Milestone'].apply(format_en)
df_ms['Remaining Streams '] = df_ms['Remaining'].apply(format_en)
df_ms['Estimated Days '] = df_ms['Days Away'].apply(format_en)
html_tableau_ms = df_ms[['Chanson', 'Target ', 'Remaining Streams ', 'Estimated Days ']].to_html(index=False, classes="table-chansons sortable auto-index", escape=False)

overtakes =[]
records_actifs = df_jour[df_jour['Daily_num'] > 0].sort_values('Streams_num', ascending=False).to_dict('records')
for i in range(len(records_actifs)):
    chanson_cible = records_actifs[i]
    for j in range(i+1, len(records_actifs)):
        chanson_poursuivant = records_actifs[j]
        if chanson_poursuivant['Daily_num'] > chanson_cible['Daily_num']:
            vitesse_rattrapage = chanson_poursuivant['Daily_num'] - chanson_cible['Daily_num']
            ecart_streams = chanson_cible['Streams_num'] - chanson_poursuivant['Streams_num']
            overtakes.append({
                'Overtaker_UID': chanson_poursuivant['Unique_ID'], 'Overtaker': chanson_poursuivant['Song Title'],
                'Target_UID': chanson_cible['Unique_ID'], 'Target': chanson_cible['Song Title'],
                'Diff': ecart_streams, 'Speed': vitesse_rattrapage, 'Days': math.ceil(ecart_streams / vitesse_rattrapage)
            })

df_over = pd.DataFrame(overtakes)
if not df_over.empty:
    df_over = df_over.sort_values('Days').head(25)
    df_over['Chanson Rapide 🚀'] = df_over.apply(lambda r: rendre_cliquable(r, 'Overtaker', 'Overtaker_UID'), axis=1)
    df_over['Chanson Rattrapée 🎯'] = df_over.apply(lambda r: rendre_cliquable(r, 'Target', 'Target_UID'), axis=1)
    df_over['Écart Actuel '] = df_over['Diff'].apply(format_en)
    df_over['Vitesse de rattrapage '] = df_over['Speed'].apply(lambda x: f"+{format_en(x)}/jour")
    df_over['Jours Estimés '] = df_over['Days'].apply(format_en)
    html_tableau_overtake = df_over[['Chanson Rapide 🚀', 'Chanson Rattrapée 🎯', 'Écart Actuel ', 'Vitesse de rattrapage ', 'Jours Estimés ']].to_html(index=False, classes="table-chansons sortable auto-index", escape=False)
else:
    html_tableau_overtake = "<p style='text-align:center; padding:20px;'>Aucun dépassement en cours détecté.</p>"


# ==========================================
# 2. LOGIQUE DES ALBUMS (NOUVEAU)
# ==========================================
album_list_stats = []
albums_js_data = {}
html_album_tracklists = ""

for i, (nom_album, tracklist_brute) in enumerate(ALBUM_TRACKS.items()):
    # Convertit les noms du dico en Unique_ID (ex: ajoute ___0 si besoin)
    uids_album = [resolve_track_id(t) for t in tracklist_brute]
    
    # 1. Stats pour la page "Liste des Albums"
    alb_jour = df_jour[df_jour['Unique_ID'].isin(uids_album)]
    tot_jour = alb_jour['Streams_num'].sum()
    daily_jour = alb_jour['Daily_num'].sum()
    
    daily_veille = 0
    if len(dates) >= 2:
        alb_veille = df[df['Date'] == dates[1]]
        alb_veille = alb_veille[alb_veille['Unique_ID'].isin(uids_album)]
        daily_veille = alb_veille['Daily_num'].sum()
        
    lien_cliquable = f'<a href="javascript:void(0)" onclick="afficherDetailsAlbum({i})" class="song-link">💿 {html.escape(nom_album)}</a>'
    album_list_stats.append({
        'Album': lien_cliquable, 'Total_Num': tot_jour, 'Daily_Num': daily_jour, 'Diff': daily_jour - daily_veille
    })

    # 2. Données JSON pour les 2 graphiques de cet album
    df_alb_hist = df[df['Unique_ID'].isin(uids_album)]
    df_alb_agg = df_alb_hist.groupby('Date').agg({'Streams_num':'sum', 'Daily_num':'sum'}).reset_index().sort_values('Date')
    albums_js_data[i] = {
        'titre': nom_album,
        'dates': df_alb_agg['Date'].tolist(),
        'streams': df_alb_agg['Streams_num'].tolist(),
        'daily': df_alb_agg['Daily_num'].tolist()
    }

    # 3. Création du code HTML de la Tracklist de l'album
    df_tracklist = df_jour[df_jour['Unique_ID'].isin(uids_album)].copy()
    
    if not df_tracklist.empty:
        # On fusionne avec les évolutions si elles existent
        if not df_affichage_evo.empty:
            df_tracklist = pd.merge(df_tracklist, df_affichage_evo[['Unique_ID', 'Différence']], on='Unique_ID', how='left')
        else:
            df_tracklist['Différence'] = '-'
            
        # On remet l'ordre exact du dictionnaire
        order_dict = {uid: idx for idx, uid in enumerate(uids_album)}
        df_tracklist['Ordre_Album'] = df_tracklist['Unique_ID'].map(order_dict)
        df_tracklist = df_tracklist.sort_values('Ordre_Album')
        
        # Formatage des nouvelles colonnes
        df_tracklist['Chanson'] = df_tracklist.apply(lambda r: rendre_cliquable(r, 'Song Title'), axis=1)
        df_tracklist['Total Streams '] = df_tracklist['Streams_num'].apply(format_en)
        df_tracklist['Daily Streams '] = df_tracklist['Daily_num'].apply(format_en)
        df_tracklist['Évolution'] = df_tracklist['Différence'].apply(format_evo)
        
        # On sélectionne les colonnes finales
        df_tracklist = df_tracklist[['Chanson', 'Total Streams ', 'Daily Streams ', 'Évolution']]
        tbl_html = df_tracklist.to_html(index=False, classes="table-chansons auto-index", escape=False)
    else:
        # S'il n'y a aucune chanson de l'album dans le Top Kworb aujourd'hui :
        tbl_html = "<p style='text-align:center; padding: 20px; color: #666;'><em>Aucune chanson de cet album n'est classée dans le Top Kworb aujourd'hui.</em></p>"
    
    html_album_tracklists += f'<div id="tracklist-album-{i}" class="album-tracklist-content" style="display:none;">{tbl_html}</div>\n'

# Formatage de la table globale des Albums
df_album_list = pd.DataFrame(album_list_stats).sort_values('Total_Num', ascending=False)
df_album_list['Total Streams '] = df_album_list['Total_Num'].apply(format_en)
df_album_list['Daily Streams '] = df_album_list['Daily_Num'].apply(format_en)
df_album_list['Évolution'] = df_album_list['Diff'].apply(format_evo)
html_tableau_albums_list = df_album_list[['Album', 'Total Streams ', 'Daily Streams ', 'Évolution']].to_html(index=False, classes="table-chansons sortable auto-index", escape=False)


# ==========================================
# 3. GRAPHIQUES JSON (Chansons) & MARKET SHARE
# ==========================================
df_graph_global = df.groupby('Date').agg({'Streams_num': 'sum', 'Daily_num': 'sum'}).reset_index().sort_values('Date')
dates_js = json.dumps(df_graph_global['Date'].tolist())
streams_total_js = json.dumps(df_graph_global['Streams_num'].tolist())
streams_daily_js = json.dumps(df_graph_global['Daily_num'].tolist())

top_10 = df_jour.sort_values('Daily_num', ascending=False).head(10)
others_daily = int(df_jour.sort_values('Daily_num', ascending=False).iloc[10:]['Daily_num'].sum())
market_labels = top_10['Song Title'].tolist() + ["Others"]
market_data = [int(x) for x in top_10['Daily_num'].tolist()] + [others_daily]
market_labels_js = json.dumps(market_labels)
market_data_js = json.dumps(market_data)

historique_chansons = {}
for uid in df['Unique_ID'].unique():
    df_chanson = df[df['Unique_ID'] == uid].sort_values('Date')
    df_chanson['Daily_7d'] = df_chanson['Daily_num'].rolling(window=7, min_periods=1).mean().round(0).astype(int)
    historique_chansons[uid] = {
        'titre': df_chanson.iloc[0]['Song Title'],
        'dates': df_chanson['Date'].tolist(),
        'streams': df_chanson['Streams_num'].tolist(),
        'daily': df_chanson['Daily_num'].tolist(),
        'daily_7d': df_chanson['Daily_7d'].tolist()
    }
historique_chansons_js = json.dumps(historique_chansons)
albums_js_data_json = json.dumps(albums_js_data)

# ==========================================
# 4. DONNÉES ARTISTE & LISTENERS
# ==========================================
df_resume = pd.read_csv("historique_resume.csv")
df_resume_jour = df_resume[df_resume['Date'] == df_resume['Date'].max()].drop(columns=['Date'])
for col in df_resume_jour.columns:
    if col != 'Catégorie': df_resume_jour[col] = df_resume_jour[col].apply(format_en)
html_tableau_resume = df_resume_jour.to_html(index=False, classes="table-chansons")

df_list_full = pd.read_csv("historique_ariana_listeners.csv")
df_list_jour = df_list_full[df_list_full['Date'] == df_list_full['Date'].max()].iloc[0]

listeners_actuel = format_en(df_list_jour['Listeners'])
listeners_peak_rank = str(df_list_jour['Peak'])
listeners_peak_val = format_en(df_list_jour['PkListeners'])
listeners_current_rank = str(df_list_jour['#']) if '#' in df_list_jour else "?"
try:
    daily_int = int(float(str(df_list_jour['Daily +/-']).replace(',', '').replace(' ', '').replace('+', '')))
    listeners_daily_str = f"+{format_en(daily_int)}" if daily_int > 0 else format_en(daily_int)
except:
    listeners_daily_str = str(df_list_jour['Daily +/-'])

df_classement = pd.read_csv("classement_listeners_jour.csv")
if all(col in df_classement.columns for col in ['Listeners', 'PkListeners']):
    df_classement['PkListeners'] = df_classement.apply(lambda r: f"<b>{format_en(r['PkListeners'])}</b>" if clean_compare(r['Listeners'], r['PkListeners']) else format_en(r['PkListeners']), axis=1)
if all(col in df_classement.columns for col in ['#', 'Peak']):
    df_classement['Peak'] = df_classement.apply(lambda r: f"<b>{format_en(r['Peak'])}</b>" if clean_compare(r['#'], r['Peak']) else format_en(r['Peak']), axis=1)

if 'Listeners' in df_classement.columns: df_classement['Listeners'] = df_classement['Listeners'].apply(format_en)
if 'Daily +/-' in df_classement.columns: df_classement['Daily +/-'] = df_classement['Daily +/-'].apply(format_evo)
html_tableau_classement = df_classement.to_html(index=False, classes="table-chansons table-listeners sortable", escape=False)

df_list_full_sorted = df_list_full.sort_values('Date')
df_list_full_sorted['Listeners_clean'] = df_list_full_sorted['Listeners'].astype(str).str.replace(',', '').str.replace(' ', '')
list_dates_js = json.dumps(df_list_full_sorted['Date'].tolist())
list_vals_js = json.dumps(pd.to_numeric(df_list_full_sorted['Listeners_clean'], errors='coerce').fillna(0).tolist())

html_listeners_grid = f"""
<div style="display: flex; flex-direction: column; gap: 20px; width: 100%;">
    <div style="display: flex; gap: 20px; flex-wrap: wrap;">
        <div class="stat-card"><h4>Current Listeners</h4><p>{listeners_actuel}</p></div>
        <div class="stat-card"><h4>Daily Trend</h4><p>{listeners_daily_str}</p></div>
        <div class="stat-card"><h4>Current Rank</h4><p>#{listeners_current_rank}</p></div>
    </div>
    <div style="display: flex; gap: 20px; flex-wrap: wrap;">
        <div class="stat-card"><h4>Peak Listeners</h4><p>{listeners_peak_val}</p></div>
        <div class="stat-card"><h4>Peak Rank</h4><p>#{listeners_peak_rank}</p></div>
    </div>
</div>
"""

# ==========================================
# 5. CRÉATION DU FICHIER HTML
# ==========================================
html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Ariana Grande</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f4f7f6; color: #333; }}
        .header {{ background-color: #257059; color: white; text-align: center; padding: 50px 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin-top: 10px; font-size: 1.1em; opacity: 0.9; }}
        .container {{ max-width: 1200px; margin: -30px auto 40px auto; padding: 0 20px; }}
        .card {{ background-color: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); width: 100%; box-sizing: border-box; }}
        
        .song-link {{ color: #257059; font-weight: bold; text-decoration: none; transition: color 0.2s; }}
        .song-link:hover {{ text-decoration: underline; color: #174738; cursor: pointer; }}
        
        .tab {{ overflow: hidden; border-bottom: 2px solid #eaeaea; margin-bottom: 20px; display: flex; justify-content: center; flex-wrap: wrap; }}
        .tab button {{ background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 24px; transition: 0.3s; font-size: 17px; color: #555; font-weight: bold; border-radius: 10px 10px 0 0; }}
        .tab button:hover {{ background-color: #f1f1f1; }}
        .tab button.active {{ background-color: #257059; color: white; }}
        .tabcontent {{ display: none; animation: fadeEffect 0.5s; }}
        
        .subtab {{ display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
        .subtab button {{ background-color: #e2e8e5; border: none; border-radius: 20px; padding: 8px 20px; font-weight: bold; color: #333; cursor: pointer; transition: 0.3s; }}
        .subtab button:hover {{ background-color: #cdd9d4; }}
        .subtab button.active {{ background-color: #257059; color: white; }}
        
        .table-chansons {{ width: 100%; border-collapse: collapse; }}
        .table-chansons th {{ background-color: #f8f9fa; color: #555; padding: 15px; text-align: right; border-bottom: 2px solid #eaeaea; }}
        .table-chansons td {{ padding: 12px 15px; text-align: right; border-bottom: 1px solid #eaeaea; }}
        .table-chansons th:first-child, .table-chansons td:first-child {{ text-align: left; }}
        .table-listeners th:nth-child(2), .table-listeners td:nth-child(2) {{ text-align: left; }}
        .table-chansons tr:hover {{ background-color: #f1f1f1; }}
        
        .auto-index tbody {{ counter-reset: row-num; }}
        .auto-index tbody tr {{ counter-increment: row-num; }}
        .auto-index tbody tr td:first-child::before {{ content: counter(row-num) "."; color: #999; font-weight: bold; display: inline-block; width: 25px; margin-right: 8px; text-align: right; }}
        .auto-index th:first-child {{ padding-left: 48px; }}
        
        .sortable th {{ cursor: pointer; position: relative; padding-right: 20px; }}
        .sortable th:hover {{ background-color: #e2e8e5; }}
        .sortable th::after {{ content: '↕'; position: absolute; right: 5px; color: #bbb; }}
        .sortable th.asc::after {{ content: '↑'; color: #257059; font-weight: bold; }}
        .sortable th.desc::after {{ content: '↓'; color: #257059; font-weight: bold; }}
        
        .info-prediction {{ background-color: #e8f4f0; color: #257059; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px; font-weight: bold; }}
        .chart-container {{ position: relative; height: 400px; width: 100%; margin-bottom: 50px; padding: 20px; box-sizing: border-box; }}
        .donut-container {{ position: relative; height: 450px; width: 100%; margin: 20px auto; }}
        
        .btn-retour {{ background-color: #333; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; margin-bottom: 20px; transition: 0.3s; }}
        .btn-retour:hover {{ background-color: #555; }}

        .big-listener-btn {{ background-color: #ffffff; border: 2px solid #eaeaea; border-radius: 15px; padding: 20px; margin-top: 15px; }}
        .listeners-clickable {{ transition: all 0.3s ease; cursor: pointer; }}
        .listeners-clickable:hover {{ transform: translateY(-3px); box-shadow: 0 8px 15px rgba(37,112,89,0.15); border-color: #257059; }}
        .listeners-static {{ cursor: default; }}
        
        .stat-card {{ background-color: #f8f9fa; border: 2px solid #eaeaea; border-radius: 12px; padding: 20px; text-align: center; flex: 1; min-width: 150px; }}
        .stat-card h4 {{ margin: 0; color: #555; font-size: 1.1em; }}
        .stat-card p {{ margin: 10px 0 0 0; color: #257059; font-size: 1.8em; font-weight: bold; }}
    </style>
</head>
<body>

    <div class="header">
        <h1>🎵 Spotify Stats</h1>
        <p>Ariana Grande - Data from {date_jour}</p>
    </div>

    <div class="container">
        
        <div class="card" id="DashboardPrincipal">
            <div class="tab">
              <button class="tablinks" onclick="openTab(event, 'Artiste')" id="defaultOpen">👩‍🎤 Artist</button>
              <button class="tablinks" onclick="openTab(event, 'Listeners')">🌍 Listeners</button>
              <button class="tablinks" onclick="openTab(event, 'Albums')">💿 Albums</button>
              <button class="tablinks" onclick="openTab(event, 'Global')">📊 Songs</button>
              <button class="tablinks" onclick="openTab(event, 'Evolution')">📈 Evolution</button>
              <button class="tablinks" onclick="openTab(event, 'Prediction')">🔮 Prediction</button>
              <button class="tablinks" onclick="openTab(event, 'Milestones')">🏆 Milestones</button>
              <button class="tablinks" onclick="openTab(event, 'Graphiques')">📉 Charts</button>
            </div>

            <!-- ONGLET ARTISTE -->
            <div id="Artiste" class="tabcontent">
                <h2 style="color: #257059; margin-top: 0;">Streams Overview</h2>
                <div style="overflow-x: auto;">{html_tableau_resume}</div>
                <h2 style="color: #257059; margin-top: 40px;">Monthly Listeners</h2>
                <p style="color: #666; font-style: italic; margin-top: -10px;">Click to see global ranking and evolution.</p>
                <div class="big-listener-btn listeners-clickable" onclick="allerVersListeners()">
                    {html_listeners_grid}
                </div>
                <hr style="border: 1px solid #eaeaea; margin: 40px 0;">
                <h2 style="color: #257059;">Daily Market Share</h2>
                <p style="color: #666; margin-top: -10px;">Top 10 songs generating the most streams today</p>
                <div class="donut-container"><canvas id="chartMarketShare"></canvas></div>
            </div>

            <!-- ONGLET LISTENERS -->
            <div id="Listeners" class="tabcontent">
                <div class="subtab">
                    <button class="subtab-list active" onclick="openSubTab(event, 'List-Overview', 'subtab-list')" id="defaultList">Overview</button>
                    <button class="subtab-list" onclick="openSubTab(event, 'List-Evo', 'subtab-list')">Evolution Chart</button>
                    <button class="subtab-list" onclick="openSubTab(event, 'List-Rank', 'subtab-list')">Global Ranking</button>
                </div>
                <div id="List-Overview" class="subtab-list-content" style="display:block;">
                    <h2 style="color: #257059;">Monthly Listeners Overview</h2>
                    <div class="big-listener-btn listeners-static">{html_listeners_grid}</div>
                </div>
                <div id="List-Evo" class="subtab-list-content" style="display:none;">
                    <div class="chart-container"><canvas id="chartListenersGlobal"></canvas></div>
                </div>
                <div id="List-Rank" class="subtab-list-content" style="display:none;">
                    <div style="overflow-x: auto;">{html_tableau_classement}</div>
                </div>
            </div>

            <!-- NOUVEL ONGLET ALBUMS -->
            <div id="Albums" class="tabcontent">
                <h2 style="color: #257059; margin-top: 0;">Discography</h2>
                <p style="color: #666; font-style: italic; margin-top: -10px;">Click on an album to see its tracklist and evolution.</p>
                {html_tableau_albums_list}
            </div>

            <!-- AUTRES ONGLETS -->
            <div id="Global" class="tabcontent">{html_tableau_global}</div>
            <div id="Evolution" class="tabcontent">{html_tableau_evo}</div>
            <div id="Prediction" class="tabcontent">
              <div class="info-prediction">Projection based on {jours_restants} remaining days in the year.</div>
              {html_tableau_pred}
            </div>
            
            <div id="Milestones" class="tabcontent">
                <div class="subtab">
                    <button class="subtab-ms active" onclick="openSubTab(event, 'MS-Targets', 'subtab-ms')" id="defaultMS">Next 100M Targets</button>
                    <button class="subtab-ms" onclick="openSubTab(event, 'MS-Overtakes', 'subtab-ms')">Time to Overtake</button>
                </div>
                <div id="MS-Targets" class="subtab-ms-content" style="display:block;">
                    <div class="info-prediction">Estimated days to reach the next 100M threshold based on current Daily Streams.</div>
                    {html_tableau_ms}
                </div>
                <div id="MS-Overtakes" class="subtab-ms-content" style="display:none;">
                    <div class="info-prediction">Songs catching up to others in Total Streams!</div>
                    {html_tableau_overtake}
                </div>
            </div>

            <div id="Graphiques" class="tabcontent">
                <h2 style="text-align:center; color:#257059;">Global Cumulated Streams</h2>
                <div class="chart-container"><canvas id="chartTotalGlobal"></canvas></div>
                <div class="chart-container"><canvas id="chartDailyGlobal"></canvas></div>
                <hr style="border: 1px solid #eaeaea; margin: 40px 0;">
                <h2 style="text-align:center; color:#257059;">⚔️ Song Comparator</h2>
                <div style="display:flex; justify-content:center; gap: 20px; margin-bottom: 20px;">
                    <select id="songSelect1" onchange="updateComparator()" style="padding: 10px; border-radius: 8px; font-size: 16px; border: 2px solid #257059; max-width: 300px;"></select>
                    <span style="font-size: 20px; align-self: center; font-weight: bold; color: #555;">VS</span>
                    <select id="songSelect2" onchange="updateComparator()" style="padding: 10px; border-radius: 8px; font-size: 16px; border: 2px solid #257059; max-width: 300px;"></select>
                </div>
                <div class="chart-container"><canvas id="chartComparator"></canvas></div>
            </div>
        </div>

        <!-- ZONE DÉTAIL CHANSON -->
        <div class="card" id="PageDetailChanson" style="display: none;">
            <button class="btn-retour" onclick="fermerPopups()">⬅ Back to Dashboard</button>
            <h2 id="TitreChansonDetail" style="text-align: center; color: #257059; font-size: 2em; margin-top: 0;">Titre</h2>
            <div class="chart-container" style="height: 350px;"><canvas id="chartChansonTotal"></canvas></div>
            <div class="subtab" style="margin-top: 30px;">
                <button class="subtab-song active" onclick="openSubTab(event, 'Song-Daily-Brut', 'subtab-song')" id="defaultSong">Daily Streams</button>
                <button class="subtab-song" onclick="openSubTab(event, 'Song-Daily-Lisse', 'subtab-song')">🌊 7-Day Rolling Average</button>
            </div>
            <div id="Song-Daily-Brut" class="subtab-song-content" style="display:block;">
                <div class="chart-container" style="height: 350px;"><canvas id="chartChansonDaily"></canvas></div>
            </div>
            <div id="Song-Daily-Lisse" class="subtab-song-content" style="display:none;">
                <div class="chart-container" style="height: 350px;"><canvas id="chartChansonDaily7d"></canvas></div>
            </div>
        </div>

        <!-- ZONE DÉTAIL ALBUM (NOUVEAU) -->
        <div class="card" id="PageDetailAlbum" style="display: none;">
            <button class="btn-retour" onclick="fermerPopups()">⬅ Back to Dashboard</button>
            <h2 id="TitreAlbumDetail" style="text-align: center; color: #257059; font-size: 2em; margin-top: 0;">Album</h2>
            <div class="chart-container" style="height: 350px;"><canvas id="chartAlbumTotal"></canvas></div>
            <div class="chart-container" style="height: 350px;"><canvas id="chartAlbumDaily"></canvas></div>
            <h3 style="color: #257059; margin-top: 40px; text-align: center;">💿 Tracklist Performance</h3>
            <div id="album-tracklists-container">
                {html_album_tracklists}
            </div>
        </div>

    </div>

    <script>
    function openTab(evt, tabName) {{
      var i, tabcontent, tablinks;
      tabcontent = document.getElementsByClassName("tabcontent");
      for (i = 0; i < tabcontent.length; i++) {{ tabcontent[i].style.display = "none"; }}
      tablinks = document.getElementsByClassName("tablinks");
      for (i = 0; i < tablinks.length; i++) {{ tablinks[i].className = tablinks[i].className.replace(" active", ""); }}
      document.getElementById(tabName).style.display = "block";
      if(evt) evt.currentTarget.className += " active";
      
      if(tabName === 'Listeners' && document.getElementById('defaultList')) document.getElementById('defaultList').click();
      if(tabName === 'Milestones' && document.getElementById('defaultMS')) document.getElementById('defaultMS').click();
      window.dispatchEvent(new Event('resize')); 
    }}
    document.getElementById("defaultOpen").click();

    function allerVersListeners() {{
        let tabs = document.getElementsByClassName("tablinks");
        for (let i = 0; i < tabs.length; i++) {{
            if (tabs[i].innerText.includes("Listeners")) {{ tabs[i].click(); break; }}
        }}
        window.scrollTo(0, 0);
    }}

    function openSubTab(evt, tabName, groupClass) {{
      var i, tabcontent, tablinks;
      tabcontent = document.getElementsByClassName(groupClass + "-content");
      for (i = 0; i < tabcontent.length; i++) {{ tabcontent[i].style.display = "none"; }}
      tablinks = document.getElementsByClassName(groupClass);
      for (i = 0; i < tablinks.length; i++) {{ tablinks[i].className = tablinks[i].className.replace(" active", ""); }}
      document.getElementById(tabName).style.display = "block";
      if(evt) evt.currentTarget.className += " active";
    }}

    function fermerPopups() {{
        document.getElementById('PageDetailChanson').style.display = 'none';
        document.getElementById('PageDetailAlbum').style.display = 'none';
        document.getElementById('DashboardPrincipal').style.display = 'block';
    }}

    document.addEventListener("DOMContentLoaded", () => {{
        document.querySelectorAll('.table-listeners tbody tr').forEach(row => {{
            if (row.cells[1] && row.cells[1].innerText.includes('Ariana Grande')) {{
                row.style.backgroundColor = '#d1ede3';
                row.style.fontWeight = 'bold';
                row.style.borderLeft = '5px solid #257059';
                row.cells[1].innerText = '⭐ Ariana Grande';
            }}
        }});
    }});

    document.querySelectorAll('.sortable th').forEach(th => {{
        th.addEventListener('click', () => {{
            const table = th.closest('table');
            const tbody = table.querySelector('tbody');
            const index = Array.from(th.parentNode.children).indexOf(th);
            const isAscending = th.classList.contains('asc');
            
            table.querySelectorAll('th').forEach(t => t.classList.remove('asc', 'desc'));
            th.classList.toggle('asc', !isAscending);
            th.classList.toggle('desc', isAscending);
            
            const rows = Array.from(tbody.querySelectorAll('tr'));
            rows.sort((a, b) => {{
                let valA = a.children[index].textContent.trim(); 
                let valB = b.children[index].textContent.trim();
                let numA = parseFloat(valA.replace(/,/g, '').replace('+', '').replace(' days', ''));
                let numB = parseFloat(valB.replace(/,/g, '').replace('+', '').replace(' days', ''));
                if (!isNaN(numA) && !isNaN(numB)) return isAscending ? numA - numB : numB - numA;
                return isAscending ? valA.localeCompare(valB) : valB.localeCompare(valA);
            }});
            tbody.append(...rows);
        }});
    }});

    const datesGlobal = {dates_js};
    new Chart(document.getElementById('chartTotalGlobal').getContext('2d'), {{
        type: 'line', data: {{ labels: datesGlobal, datasets:[{{ label: 'Total Streams', data: {streams_total_js}, borderColor: '#257059', backgroundColor: 'rgba(37, 112, 89, 0.2)', borderWidth: 3, fill: true, tension: 0.3 }}] }},
        options: {{ responsive: true, maintainAspectRatio: false }}
    }});
    new Chart(document.getElementById('chartDailyGlobal').getContext('2d'), {{
        type: 'line', data: {{ labels: datesGlobal, datasets:[{{ label: 'Daily Streams', data: {streams_daily_js}, borderColor: '#d9534f', backgroundColor: 'rgba(217, 83, 79, 0.2)', borderWidth: 3, fill: true, tension: 0.3 }}] }},
        options: {{ responsive: true, maintainAspectRatio: false }}
    }});

    new Chart(document.getElementById('chartMarketShare').getContext('2d'), {{
        type: 'doughnut',
        data: {{
            labels: {market_labels_js},
            datasets: [{{ data: {market_data_js}, backgroundColor: ['#164a39','#1e5d4a','#257059','#2d866a','#359c7b','#3eb28d','#50c29f','#67cdad','#7fdbbd','#97e9ce','#cccccc'], borderWidth: 2 }}]
        }},
        options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right' }} }} }}
    }});

    const historique_chansons = {historique_chansons_js};
    let graphTotal = null, graphDaily = null, graphDaily7d = null, graphCompare = null;

    const songKeys = Object.keys(historique_chansons).sort((a,b) => historique_chansons[a].titre.localeCompare(historique_chansons[b].titre));
    const sel1 = document.getElementById('songSelect1');
    const sel2 = document.getElementById('songSelect2');
    songKeys.forEach(k => {{ sel1.add(new Option(historique_chansons[k].titre, k)); sel2.add(new Option(historique_chansons[k].titre, k)); }});
    if(songKeys.length > 1) sel2.selectedIndex = 1;

    function getAlignedData(songDates, songVals, globalDates) {{ return globalDates.map(gDate => {{ let idx = songDates.indexOf(gDate); return idx !== -1 ? songVals[idx] : null; }}); }}

    function updateComparator() {{
        let d1 = historique_chansons[sel1.value];
        let d2 = historique_chansons[sel2.value];
        if (graphCompare) graphCompare.destroy();
        graphCompare = new Chart(document.getElementById('chartComparator').getContext('2d'), {{
            type: 'line',
            data: {{
                labels: datesGlobal,
                datasets:[
                    {{ label: d1.titre, data: getAlignedData(d1.dates, d1.daily, datesGlobal), borderColor: '#257059', backgroundColor: '#257059', borderWidth: 3, spanGaps: true, tension: 0.3 }},
                    {{ label: d2.titre, data: getAlignedData(d2.dates, d2.daily, datesGlobal), borderColor: '#d9534f', backgroundColor: '#d9534f', borderWidth: 3, spanGaps: true, tension: 0.3 }}
                ]
            }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});
    }}
    updateComparator();

    function afficherDetailsChanson(uid) {{
        document.getElementById('DashboardPrincipal').style.display = 'none';
        document.getElementById('PageDetailAlbum').style.display = 'none';
        document.getElementById('PageDetailChanson').style.display = 'block';
        document.getElementById('defaultSong').click();
        
        const donnees = historique_chansons[uid];
        document.getElementById('TitreChansonDetail').innerText = "📈 " + donnees.titre;

        if (graphTotal) graphTotal.destroy();
        if (graphDaily) graphDaily.destroy();
        if (graphDaily7d) graphDaily7d.destroy();

        graphTotal = new Chart(document.getElementById('chartChansonTotal').getContext('2d'), {{
            type: 'line', data: {{ labels: donnees.dates, datasets:[{{ label: 'Total Streams', data: donnees.streams, borderColor: '#257059', backgroundColor: 'rgba(37,112,89,0.2)', borderWidth: 3, fill: true, tension: 0.3 }}] }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});
        graphDaily = new Chart(document.getElementById('chartChansonDaily').getContext('2d'), {{
            type: 'line', data: {{ labels: donnees.dates, datasets:[{{ label: 'Daily Streams', data: donnees.daily, borderColor: '#d9534f', backgroundColor: 'rgba(217,83,79,0.2)', borderWidth: 3, fill: true, tension: 0.3 }}] }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});
        graphDaily7d = new Chart(document.getElementById('chartChansonDaily7d').getContext('2d'), {{
            type: 'line', data: {{ labels: donnees.dates, datasets:[{{ label: 'Moyenne 7 Jours (Lissé)', data: donnees.daily_7d, borderColor: '#2980b9', backgroundColor: 'rgba(41,128,185,0.2)', borderWidth: 3, fill: true, tension: 0.4 }}] }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});
        window.scrollTo(0, 0);
    }}

    // --- LOGIQUE ALBUMS (NOUVEAU) ---
    const albums_js_data = {albums_js_data_json};
    let graphAlbumTotal = null, graphAlbumDaily = null;

    function afficherDetailsAlbum(albumIndex) {{
        document.getElementById('DashboardPrincipal').style.display = 'none';
        document.getElementById('PageDetailChanson').style.display = 'none';
        document.getElementById('PageDetailAlbum').style.display = 'block';
        
        // Cache toutes les tracklists, et affiche la bonne
        document.querySelectorAll('.album-tracklist-content').forEach(el => el.style.display = 'none');
        document.getElementById('tracklist-album-' + albumIndex).style.display = 'block';
        
        const donnees = albums_js_data[albumIndex];
        document.getElementById('TitreAlbumDetail').innerText = "💿 " + donnees.titre;

        if (graphAlbumTotal) graphAlbumTotal.destroy();
        if (graphAlbumDaily) graphAlbumDaily.destroy();

        graphAlbumTotal = new Chart(document.getElementById('chartAlbumTotal').getContext('2d'), {{
            type: 'line', data: {{ labels: donnees.dates, datasets:[{{ label: 'Total Streams (Album)', data: donnees.streams, borderColor: '#8e44ad', backgroundColor: 'rgba(142,68,173,0.2)', borderWidth: 3, fill: true, tension: 0.3 }}] }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});
        graphAlbumDaily = new Chart(document.getElementById('chartAlbumDaily').getContext('2d'), {{
            type: 'line', data: {{ labels: donnees.dates, datasets:[{{ label: 'Daily Streams (Album)', data: donnees.daily, borderColor: '#e67e22', backgroundColor: 'rgba(230,126,34,0.2)', borderWidth: 3, fill: true, tension: 0.3 }}] }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});
        window.scrollTo(0, 0);
    }}

    new Chart(document.getElementById('chartListenersGlobal').getContext('2d'), {{
        type: 'line', data: {{ labels: {list_dates_js}, datasets:[{{ label: "Monthly Listeners", data: {list_vals_js}, borderColor: '#8e44ad', backgroundColor: 'rgba(142, 68, 173, 0.2)', borderWidth: 3, fill: true, tension: 0.3 }}] }},
        options: {{ responsive: true, maintainAspectRatio: false }}
    }});
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Dashboard mis à jour : L'onglet Albums complet a été intégré !")
