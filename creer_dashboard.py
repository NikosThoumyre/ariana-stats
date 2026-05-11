import pandas as pd
from datetime import datetime
import json
import html

# --- FONCTION UTILITAIRE ---
def rendre_cliquable(row, colonne_titre):
    titre = row[colonne_titre]
    uid_safe = row['Unique_ID'].replace("'", "\\'").replace('"', '&quot;')
    titre_affiche = html.escape(str(titre))
    return f'<a href="javascript:void(0)" onclick="afficherDetailsChanson(\'{uid_safe}\')" class="song-link" title="Voir les graphiques de {titre_affiche}">{titre_affiche}</a>'

def format_num(x):
    try:
        clean_x = str(x).replace(',', '').replace(' ', '')
        return f"{int(float(clean_x)):,}".replace(",", " ")
    except:
        return str(x)

# ==========================================
# 1. DONNÉES CHANSONS (Dashboard Principal)
# ==========================================
df = pd.read_csv("historique_ariana.csv")
df['Occurence'] = df.groupby(['Date', 'Song Title']).cumcount()
df['Unique_ID'] = df['Song Title'] + "___" + df['Occurence'].astype(str)
df['Streams_num'] = pd.to_numeric(df['Streams'], errors='coerce').fillna(0)
df['Daily_num'] = pd.to_numeric(df['Daily'], errors='coerce').fillna(0)

dates = sorted(df['Date'].unique(), reverse=True)
date_jour = dates[0]

# Tableaux
df_jour = df[df['Date'] == date_jour].copy()
df_global = df_jour[['Song Title', 'Streams', 'Daily', 'Unique_ID']].copy()
df_global['Song Title'] = df_global.apply(lambda r: rendre_cliquable(r, 'Song Title'), axis=1)
html_tableau_global = df_global.drop(columns=['Unique_ID']).fillna('-').to_html(index=False, classes="table-chansons", escape=False)

if len(dates) >= 2:
    df_evolution = pd.merge(df_jour, df[df['Date'] == dates[1]], on=['Song Title', 'Occurence'], suffixes=('_Aujourdhui', '_Hier'))
    df_evolution['Différence'] = df_evolution['Daily_num_Aujourdhui'] - df_evolution['Daily_num_Hier']
    df_affichage_evo = df_evolution[['Song Title', 'Daily_Aujourdhui', 'Daily_Hier', 'Différence', 'Unique_ID_Aujourdhui']].copy()
    df_affichage_evo = df_affichage_evo.rename(columns={'Unique_ID_Aujourdhui': 'Unique_ID'})
    df_affichage_evo['Chanson'] = df_affichage_evo.apply(lambda r: rendre_cliquable(r, 'Song Title'), axis=1)
    df_affichage_evo = df_affichage_evo[['Chanson', 'Daily_Aujourdhui', 'Daily_Hier', 'Différence']].fillna('-')
    df_affichage_evo.columns =['Chanson', 'Daily Actuel', 'Daily Veille', 'Évolution']
    html_tableau_evo = df_affichage_evo.to_html(index=False, classes="table-chansons", escape=False)
else:
    html_tableau_evo = "<p style='text-align:center;'><em>⏳ Reviens à la prochaine mise à jour pour voir les évolutions !</em></p>"

date_obj = datetime.strptime(date_jour, "%Y-%m-%d")
jours_restants = (datetime(date_obj.year, 12, 31) - date_obj).days
df_pred = df_jour[['Song Title', 'Streams_num', 'Daily_num', 'Unique_ID']].copy()
df_pred['Prédiction'] = df_pred['Streams_num'] + (df_pred['Daily_num'] * jours_restants)
df_pred = df_pred.sort_values(by='Prédiction', ascending=False)
df_pred['Chanson'] = df_pred.apply(lambda r: rendre_cliquable(r, 'Song Title'), axis=1)
df_pred_final = df_pred[['Chanson', 'Streams_num', 'Daily_num', 'Prédiction']].copy()
df_pred_final.columns =['Chanson', 'Streams Actuels', f'Daily Actuel', f'Prédiction (au 31 Déc {date_obj.year})']
html_tableau_pred = df_pred_final.astype(str).to_html(index=False, classes="table-chansons", escape=False)

# Graphiques Chansons JSON
df_graph_global = df.groupby('Date').agg({'Streams_num': 'sum', 'Daily_num': 'sum'}).reset_index().sort_values('Date')
dates_js = json.dumps(df_graph_global['Date'].tolist())
streams_total_js = json.dumps(df_graph_global['Streams_num'].tolist())
streams_daily_js = json.dumps(df_graph_global['Daily_num'].tolist())

historique_chansons = {}
for uid in df['Unique_ID'].unique():
    df_chanson = df[df['Unique_ID'] == uid].sort_values('Date')
    historique_chansons[uid] = {
        'titre': df_chanson.iloc[0]['Song Title'],
        'dates': df_chanson['Date'].tolist(),
        'streams': df_chanson['Streams_num'].tolist(),
        'daily': df_chanson['Daily_num'].tolist()
    }
historique_chansons_js = json.dumps(historique_chansons)


# ==========================================
# 2. NOUVEAU : DONNÉES ARTISTE & LISTENERS
# ==========================================
# Tableau Résumé (Solo/Lead)
df_resume = pd.read_csv("historique_resume.csv")
df_resume_jour = df_resume[df_resume['Date'] == date_jour].drop(columns=['Date'])
html_tableau_resume = df_resume_jour.to_html(index=False, classes="table-chansons")

# Cartes Listeners
df_list_full = pd.read_csv("historique_ariana_listeners.csv")
df_list_jour = df_list_full[df_list_full['Date'] == df_list_full['Date'].max()].iloc[0]

listeners_actuel = format_num(df_list_jour['Listeners'])
listeners_peak_rank = str(df_list_jour['Peak'])
listeners_peak_val = format_num(df_list_jour['PkListeners'])

daily_raw = str(df_list_jour['Daily +/-']).replace(',', '').replace(' ', '')
try:
    daily_int = int(float(daily_raw))
    listeners_daily_str = f"+{format_num(daily_int)}" if daily_int > 0 else format_num(daily_int)
except:
    listeners_daily_str = str(df_list_jour['Daily +/-'])

# Classement Global (Pop-up)
df_classement = pd.read_csv("classement_listeners_jour.csv")
html_tableau_classement = df_classement.to_html(index=False, classes="table-chansons")

# Graphique Listeners JSON
df_list_full_sorted = df_list_full.sort_values('Date')
df_list_full_sorted['Listeners_clean'] = df_list_full_sorted['Listeners'].astype(str).str.replace(',', '').str.replace(' ', '')
list_dates_js = json.dumps(df_list_full_sorted['Date'].tolist())
list_vals_js = json.dumps(pd.to_numeric(df_list_full_sorted['Listeners_clean'], errors='coerce').fillna(0).tolist())


# ==========================================
# 3. CRÉATION DU FICHIER HTML
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
        @keyframes fadeEffect {{ from {{opacity: 0;}} to {{opacity: 1;}} }}
        
        .table-chansons {{ width: 100%; border-collapse: collapse; }}
        .table-chansons th {{ background-color: #f8f9fa; color: #555; padding: 15px; text-align: left; border-bottom: 2px solid #eaeaea; }}
        .table-chansons td {{ padding: 12px 15px; border-bottom: 1px solid #eaeaea; }}
        .table-chansons tr:hover {{ background-color: #f1f1f1; }}
        
        .info-prediction {{ background-color: #e8f4f0; color: #257059; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px; font-weight: bold; }}
        .chart-container {{ position: relative; height: 400px; width: 100%; margin-bottom: 50px; padding: 20px; box-sizing: border-box; }}
        
        .btn-retour {{ background-color: #333; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; margin-bottom: 20px; transition: 0.3s; }}
        .btn-retour:hover {{ background-color: #555; }}

        /* NOUVEAU : Le style des cartes Listeners */
        .listeners-grid {{ display: flex; flex-wrap: wrap; gap: 20px; cursor: pointer; margin-top: 20px; }}
        .stat-card {{ flex: 1 1 calc(25% - 20px); min-width: 200px; background-color: #f8f9fa; border: 2px solid #eaeaea; border-radius: 12px; padding: 20px; text-align: center; transition: all 0.3s ease; }}
        .stat-card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 15px rgba(37,112,89,0.15); border-color: #257059; }}
        .stat-card h4 {{ margin: 0; color: #555; font-size: 1.1em; }}
        .stat-card p {{ margin: 10px 0 0 0; color: #257059; font-size: 1.8em; font-weight: bold; }}
    </style>
</head>
<body>

    <div class="header">
        <h1>🎵 Statistiques Spotify</h1>
        <p>Ariana Grande - Données du {date_jour}</p>
    </div>

    <div class="container">
        
        <!-- ============================================== -->
        <!-- ZONE 1 : LE DASHBOARD PRINCIPAL                -->
        <!-- ============================================== -->
        <div class="card" id="DashboardPrincipal">
            <div class="tab">
              <button class="tablinks" onclick="openTab(event, 'Artiste')" id="defaultOpen">👩‍🎤 Artiste</button>
              <button class="tablinks" onclick="openTab(event, 'Global')">📊 Chansons</button>
              <button class="tablinks" onclick="openTab(event, 'Evolution')">📈 Évolution</button>
              <button class="tablinks" onclick="openTab(event, 'Prediction')">🔮 Prédiction</button>
              <button class="tablinks" onclick="openTab(event, 'Graphiques')">📉 Graphes Globaux</button>
            </div>

            <!-- NOUVEL ONGLET ARTISTE -->
            <div id="Artiste" class="tabcontent">
                <h2 style="color: #257059; margin-top: 0;">Répartition des Streams</h2>
                <div style="overflow-x: auto;">{html_tableau_resume}</div>
                
                <h2 style="color: #257059; margin-top: 40px;">Auditeurs Mensuels (Spotify)</h2>
                <p style="color: #666; font-style: italic; margin-top: -10px;">👇 Cliquez sur les cartes ci-dessous pour voir le classement complet et l'évolution.</p>
                <div class="listeners-grid" onclick="afficherDetailsListeners()">
                    <div class="stat-card">
                        <h4>Listeners Actuels</h4>
                        <p>{listeners_actuel}</p>
                    </div>
                    <div class="stat-card">
                        <h4>Évolution (Daily)</h4>
                        <p>{listeners_daily_str}</p>
                    </div>
                    <div class="stat-card">
                        <h4>Pic (Classement)</h4>
                        <p>#{listeners_peak_rank}</p>
                    </div>
                    <div class="stat-card">
                        <h4>Pic (Auditeurs)</h4>
                        <p>{listeners_peak_val}</p>
                    </div>
                </div>
            </div>

            <div id="Global" class="tabcontent">{html_tableau_global}</div>
            <div id="Evolution" class="tabcontent">{html_tableau_evo}</div>
            <div id="Prediction" class="tabcontent">
              <div class="info-prediction">Projection sur {jours_restants} jours avant la fin de l'année.</div>
              {html_tableau_pred}
            </div>
            <div id="Graphiques" class="tabcontent">
                <h2 style="text-align:center; color:#257059;">Cumul Global - Ariana Grande</h2>
                <div class="chart-container"><canvas id="chartTotalGlobal"></canvas></div>
                <div class="chart-container"><canvas id="chartDailyGlobal"></canvas></div>
            </div>
        </div>

        <!-- ============================================== -->
        <!-- ZONE 2 : LA PAGE DÉTAIL D'UNE CHANSON          -->
        <!-- ============================================== -->
        <div class="card" id="PageDetailChanson" style="display: none;">
            <button class="btn-retour" onclick="fermerPopups()">⬅ Retour</button>
            <h2 id="TitreChansonDetail" style="text-align: center; color: #257059; font-size: 2em; margin-top: 0;">Titre</h2>
            <div class="chart-container"><canvas id="chartChansonTotal"></canvas></div>
            <div class="chart-container"><canvas id="chartChansonDaily"></canvas></div>
        </div>

        <!-- ============================================== -->
        <!-- ZONE 3 : LA PAGE DÉTAIL DES LISTENERS          -->
        <!-- ============================================== -->
        <div class="card" id="PageDetailListeners" style="display: none;">
            <button class="btn-retour" onclick="fermerPopups()">⬅ Retour</button>
            <h2 style="text-align: center; color: #257059; font-size: 2em; margin-top: 0;">🌍 Auditeurs Mensuels</h2>
            
            <div class="chart-container"><canvas id="chartListenersGlobal"></canvas></div>
            
            <h3 style="color: #257059; margin-top: 40px;">Classement Actuel (Tous les artistes)</h3>
            <div style="overflow-x: auto;">
                {html_tableau_classement}
            </div>
        </div>

    </div>

    <script>
    // --- ONGLETS ---
    function openTab(evt, tabName) {{
      var i, tabcontent, tablinks;
      tabcontent = document.getElementsByClassName("tabcontent");
      for (i = 0; i < tabcontent.length; i++) {{ tabcontent[i].style.display = "none"; }}
      tablinks = document.getElementsByClassName("tablinks");
      for (i = 0; i < tablinks.length; i++) {{ tablinks[i].className = tablinks[i].className.replace(" active", ""); }}
      document.getElementById(tabName).style.display = "block";
      evt.currentTarget.className += " active";
    }}
    document.getElementById("defaultOpen").click();

    // --- FERMER LES POPUPS ---
    function fermerPopups() {{
        document.getElementById('PageDetailChanson').style.display = 'none';
        document.getElementById('PageDetailListeners').style.display = 'none';
        document.getElementById('DashboardPrincipal').style.display = 'block';
    }}

    // --- GRAPHIQUES GLOBAUX ---
    const datesGlobal = {dates_js};
    new Chart(document.getElementById('chartTotalGlobal').getContext('2d'), {{
        type: 'line', data: {{ labels: datesGlobal, datasets:[{{ label: 'Total Streams (Global)', data: {streams_total_js}, borderColor: '#257059', backgroundColor: 'rgba(37, 112, 89, 0.2)', borderWidth: 3, fill: true, tension: 0.3 }}] }},
        options: {{ responsive: true, maintainAspectRatio: false }}
    }});
    new Chart(document.getElementById('chartDailyGlobal').getContext('2d'), {{
        type: 'line', data: {{ labels: datesGlobal, datasets:[{{ label: 'Streams Quotidiens (Global)', data: {streams_daily_js}, borderColor: '#d9534f', backgroundColor: 'rgba(217, 83, 79, 0.2)', borderWidth: 3, fill: true, tension: 0.3 }}] }},
        options: {{ responsive: true, maintainAspectRatio: false }}
    }});

    // --- POPUP CHANSONS ---
    const historique_chansons = {historique_chansons_js};
    let graphTotal = null, graphDaily = null;

    function afficherDetailsChanson(uid) {{
        document.getElementById('DashboardPrincipal').style.display = 'none';
        document.getElementById('PageDetailChanson').style.display = 'block';
        const donnees = historique_chansons[uid];
        document.getElementById('TitreChansonDetail').innerText = "📈 " + donnees.titre;

        if (graphTotal) graphTotal.destroy();
        if (graphDaily) graphDaily.destroy();

        graphTotal = new Chart(document.getElementById('chartChansonTotal').getContext('2d'), {{
            type: 'line', data: {{ labels: donnees.dates, datasets:[{{ label: 'Total Streams', data: donnees.streams, borderColor: '#257059', backgroundColor: 'rgba(37,112,89,0.2)', borderWidth: 3, fill: true, tension: 0.3 }}] }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});
        graphDaily = new Chart(document.getElementById('chartChansonDaily').getContext('2d'), {{
            type: 'line', data: {{ labels: donnees.dates, datasets:[{{ label: 'Daily Streams', data: donnees.daily, borderColor: '#d9534f', backgroundColor: 'rgba(217,83,79,0.2)', borderWidth: 3, fill: true, tension: 0.3 }}] }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});
        window.scrollTo(0, 0);
    }}

    // --- POPUP LISTENERS ---
    let graphListeners = null;
    const listDates = {list_dates_js};
    const listVals = {list_vals_js};

    function afficherDetailsListeners() {{
        document.getElementById('DashboardPrincipal').style.display = 'none';
        document.getElementById('PageDetailListeners').style.display = 'block';

        if (graphListeners) graphListeners.destroy();

        graphListeners = new Chart(document.getElementById('chartListenersGlobal').getContext('2d'), {{
            type: 'line',
            data: {{
                labels: listDates,
                datasets:[{{
                    label: "Auditeurs Mensuels (Ariana Grande)",
                    data: listVals,
                    borderColor: '#8e44ad', /* Joli violet pour Spotify */
                    backgroundColor: 'rgba(142, 68, 173, 0.2)',
                    borderWidth: 3, fill: true, tension: 0.3
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});
        window.scrollTo(0, 0);
    }}
    </script>
</body>
</html>
"""

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Dashboard mis à jour avec le module ARTISTE et le classement des Listeners !")