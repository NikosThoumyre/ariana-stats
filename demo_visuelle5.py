import pandas as pd
import json
import os

print("📊 Génération de la démo (Pyramide & Treemap) avec tes VRAIES données...")

# Le dictionnaire pour savoir quelle chanson appartient à quel album
ALBUM_TRACKS = {
    "Yours Truly": ["Honeymoon Avenue", "Baby I", "Right There (feat. Big Sean)", "Tattooed Heart", "Lovin' It", "Piano", "Daydreamin'", "The Way (feat. Mac Miller)", "You'll Never Know", "Almost Is Never Enough (with Nathan Sykes)", "* Popular Song (MIKA & Ariana Grande)", "Better Left Unsaid"],
    "My Everything": ["Intro", "Problem", "One Last Time", "Why Try", "Break Free", "Best Mistake", "Be My Baby", "Break Your Heart Right Back", "Love Me Harder", "Just A Little Bit Of Your Heart", "Hands On Me", "My Everything", "* Bang Bang", "Only 1", "You Don't Know Me"],
    "Dangerous Woman": ["Moonlight", "Dangerous Woman", "Be Alright", "Into You", "Side To Side", "Let Me Love You", "Greedy", "Leave Me Lonely", "Everyday", "Sometimes", "I Don't Care", "Bad Decisions", "Touch It", "Knew Better / Forever Boy", "Thinking Bout You", "Step On Up", "Jason's Song (Gave It Away)"],
    "Sweetener": ["raindrops (an angel cried)", "blazed (feat. Pharrell Williams)", "the light is coming (feat. Nicki Minaj)", "R.E.M", "God is a woman", "sweetener", "successful", "everytime", "breathin", "no tears left to cry", "borderline (feat. Missy Elliott)", "better off", "goodnight n go", "pete davidson", "get well soon"],
    "thank u, next": ["imagine", "needy", "NASA", "bloodline", "fake smile", "bad idea", "make up", "ghostin", "in my head", "7 rings", "thank u, next", "break up with your girlfriend, i'm bored"],
    "Positions": ["shut up", "34+35", "motive (with Doja Cat)", "just like magic", "off the table (with The Weeknd)", "six thirty", "safety net (feat. Ty Dolla $ign)", "my hair", "nasty", "west side", "love language", "positions", "obvious", "pov", "someone like u - interlude", "test drive", "34+35 Remix (feat. Doja Cat, Megan Thee Stallion) - Remix", "worst behavior", "main thing"],
    "eternal sunshine": ["intro (end of the world)", "bye", "don't wanna break up again", "Saturn Returns Interlude", "eternal sunshine", "supernatural", "true story", "the boy is mine", "yes, and?", "we can't be friends (wait for your love)", "i wish i hated you", "imperfect for you", "ordinary things (feat. Nonna)", "intro (end of the world) - extended", "twilight zone", "warm", "dandelion", "past life", "Hampstead"]
}

# Inversion du dictionnaire pour le Treemap
song_to_album = {}
for album, tracks in ALBUM_TRACKS.items():
    for t in tracks:
        clean_t = t.split('___')[0] # Sécurité
        song_to_album[clean_t] = album

# --- LECTURE DES VRAIES DONNÉES ---
if os.path.exists("historique_ariana.csv"):
    df = pd.read_csv("historique_ariana.csv")
    date_max = df['Date'].max()
    df_latest = df[df['Date'] == date_max].copy()
    df_latest['Streams_num'] = pd.to_numeric(df_latest['Streams'], errors='coerce').fillna(0)
else:
    print("Fichier historique introuvable, création de fausses données...")
    df_latest = pd.DataFrame() # Sécurité

# 1. CALCULS POUR LA PYRAMIDE (RÉPARTITION DU CATALOGUE)
c_2b = len(df_latest[df_latest['Streams_num'] >= 2_000_000_000])
c_1b = len(df_latest[(df_latest['Streams_num'] >= 1_000_000_000) & (df_latest['Streams_num'] < 2_000_000_000)])
c_500m = len(df_latest[(df_latest['Streams_num'] >= 500_000_000) & (df_latest['Streams_num'] < 1_000_000_000)])
c_100m = len(df_latest[(df_latest['Streams_num'] >= 100_000_000) & (df_latest['Streams_num'] < 500_000_000)])
c_rest = len(df_latest[df_latest['Streams_num'] < 100_000_000])

# 2. CALCULS POUR LE TREEMAP
treemap_data = []
for _, row in df_latest.iterrows():
    song_name = row['Song Title'].split('___')[0]
    album = song_to_album.get(song_name, "Singles & Features")
    treemap_data.append({
        'album': album,
        'song': song_name,
        'streams': row['Streams_num']
    })
treemap_json = json.dumps(treemap_data)

# --- GÉNÉRATION DU HTML ---
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demo Visuals 5 - Analytics</title>
    <!-- Importation de Chart.js ET de son plugin Treemap -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-treemap@2.3.0/dist/chartjs-chart-treemap.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 40px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h2 {{ color: #257059; border-bottom: 2px solid #b0c4b1; padding-bottom: 10px; margin-top: 40px; text-transform: uppercase; font-size: 1.2em; letter-spacing: 1px; }}
        .desc {{ color: #666; font-style: italic; margin-bottom: 30px; }}
        
        .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 8px 15px rgba(0,0,0,0.05); border: 1px solid #eaeaea; margin-bottom: 40px; }}

        /* DESIGN DE LA PYRAMIDE (100% CSS) */
        .pyramid-wrapper {{ display: flex; flex-direction: column; align-items: center; gap: 8px; margin: 20px 0; }}
        .pyr-tier {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; border-radius: 6px; color: white; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.2); box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; }}
        .pyr-tier:hover {{ transform: scale(1.02); }}
        .pyr-label {{ font-size: 1.1em; letter-spacing: 1px; }}
        .pyr-val {{ font-family: 'Courier New', monospace; font-size: 1.2em; background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 15px; }}
        
        /* Largeurs mathématiques de la pyramide */
        .t-2b {{ width: 35%; background: linear-gradient(135deg, #d4af37, #f1c40f); }}
        .t-1b {{ width: 50%; background: linear-gradient(135deg, #7f8c8d, #bdc3c7); }}
        .t-500m {{ width: 65%; background: linear-gradient(135deg, #257059, #359c7b); }}
        .t-100m {{ width: 85%; background: linear-gradient(135deg, #2980b9, #3498db); }}
        .t-rest {{ width: 100%; background: linear-gradient(135deg, #8e44ad, #9b59b6); }}

        /* CONTENEUR TREEMAP */
        .treemap-container {{ position: relative; height: 500px; width: 100%; }}


        /* 💡 DESIGN : PYRAMIDE DES STREAMS (CATALOGUE) */
        .pyramid-wrapper {{ display: flex; flex-direction: column; align-items: center; gap: 8px; margin: 30px auto 40px auto; width: 100%; max-width: 800px; }}
        .pyr-tier {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; border-radius: 6px; color: white; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.2); box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; }}
        .pyr-tier:hover {{ transform: scale(1.02); }}
        .pyr-label {{ font-size: 1.1em; letter-spacing: 1px; }}
        .pyr-val {{ font-family: 'Courier New', monospace; font-size: 1.2em; background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 15px; }}
        
        .t-2b {{ width: 35%; background: linear-gradient(135deg, #d4af37, #f1c40f); }}
        .t-1b {{ width: 50%; background: linear-gradient(135deg, #7f8c8d, #bdc3c7); }}
        .t-500m {{ width: 65%; background: linear-gradient(135deg, #257059, #359c7b); }}
        .t-100m {{ width: 85%; background: linear-gradient(135deg, #2980b9, #3498db); }}
        .t-rest {{ width: 100%; background: linear-gradient(135deg, #8e44ad, #9b59b6); }}
    </style>
</head>
<body>

    <div class="container">
        <h1 style="text-align: center; color: #257059;">📊 Visualisations de Données (Tes Vraies Chansons !)</h1>

        <!-- 1. LA PYRAMIDE -->
        <h2>1. Catalog Distribution (La Pyramide des Streams)</h2>
        <p class="desc">Affiche la répartition exacte de toutes les chansons de ta base de données selon leurs caps de streams.</p>
        
        <div class="card">
            <div class="pyramid-wrapper">
                <div class="pyr-tier t-2b">
                    <span class="pyr-label">👑 +2 BILLION</span>
                    <span class="pyr-val">{c_2b} songs</span>
                </div>
                <div class="pyr-tier t-1b">
                    <span class="pyr-label">💿 +1 BILLION</span>
                    <span class="pyr-val">{c_1b} songs</span>
                </div>
                <div class="pyr-tier t-500m">
                    <span class="pyr-label">📀 +500 MILLION</span>
                    <span class="pyr-val">{c_500m} songs</span>
                </div>
                <div class="pyr-tier t-100m">
                    <span class="pyr-label">🎵 +100 MILLION</span>
                    <span class="pyr-val">{c_100m} songs</span>
                </div>
                <div class="pyr-tier t-rest">
                    <span class="pyr-label">💤 Under 100M</span>
                    <span class="pyr-val">{c_rest} songs</span>
                </div>
            </div>
        </div>

        <!-- 2. LE TREEMAP (CARTOGRAPHIE) -->
        <h2>2. Catalog Mapping (Le Treemap)</h2>
        <p class="desc">Chaque bloc représente un album. À l'intérieur, les rectangles sont les chansons. La taille du rectangle dépend des Streams totaux exacts d'aujourd'hui. (Passe la souris pour voir les détails !)</p>
        
        <div class="card">
            <div class="treemap-container">
                <canvas id="treemapChart"></canvas>
            </div>
        </div>

    </div>

    <script>
        // --- SCRIPT POUR LE TREEMAP CHART.JS ---
        const rawData = {treemap_json};
        
        // Couleurs par albums (Personnalisable !)
        const albumColors = {{
            'Yours Truly': 'rgba(108, 117, 125, 0.8)', // Gris
            'My Everything': 'rgba(0, 0, 0, 0.8)',      // Noir
            'Dangerous Woman': 'rgba(142, 68, 173, 0.8)', // Violet
            'Sweetener': 'rgba(243, 156, 18, 0.8)',     // Beige/Orange
            'thank u, next': 'rgba(255, 105, 180, 0.8)',// Rose
            'Positions': 'rgba(76, 175, 80, 0.8)',      // Vert d'eau
            'eternal sunshine': 'rgba(217, 83, 79, 0.8)', // Rouge
            'Singles & Features': 'rgba(41, 128, 185, 0.8)' // Bleu
        }};

        const ctx = document.getElementById('treemapChart').getContext('2d');
        
        new Chart(ctx, {{
            type: 'treemap',
            data: {{
                datasets: [{{
                    tree: rawData,
                    key: 'streams', // La taille dépend des streams
                    groups: ['album', 'song'], // On groupe par album, puis par chanson
                    spacing: 1,
                    borderWidth: 1,
                    borderColor: '#ffffff',
                    backgroundColor: function(ctx) {{
                        // On colore en fonction du nom de l'album
                        if (ctx.type !== 'data') return 'transparent';
                        const albumName = ctx.raw._data.album;
                        return albumColors[albumName] || '#999999';
                    }},
                    labels: {{
                        align: 'center',
                        display: true,
                        color: 'white',
                        font: {{ family: 'Segoe UI', weight: 'bold', size: 11 }},
                        formatter: function(ctx) {{
                            // On n'affiche le nom de la chanson que si la boîte est assez grande
                            if (ctx.raw.w < 60 || ctx.raw.h < 30) return '';
                            return ctx.raw._data.song;
                        }}
                    }}
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            title: function(items) {{
                                return items[0].raw._data.album;
                            }},
                            label: function(item) {{
                                const song = item.raw._data.song;
                                const streams = item.raw._data.streams.toLocaleString('en-US');
                                return song + ' : ' + streams + ' streams';
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

with open("demo_visuelle5.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Fichier 'demo_visuelle5.html' généré ! Va voir tes vraies stats dans ton navigateur !")