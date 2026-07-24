import os

print("🎨 Création de la page de démonstration n°2 (Heatmap, Constellation, Wrapped)...")

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demo Visuals 2 - Ariana Stats</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 40px; }
        .container { max-width: 1000px; margin: 0 auto; }
        h2 { color: #257059; border-bottom: 2px solid #b0c4b1; padding-bottom: 10px; margin-top: 60px; }
        .desc { text-align: center; color: #666; font-style: italic; margin-bottom: 30px; }

        /* ------------------------------------------- */
        /* 1. LA HEATMAP (Façon GitHub)                */
        /* ------------------------------------------- */
        .heatmap-card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); overflow-x: auto; }
        .heatmap-grid { 
            display: grid; 
            /* 52 semaines = 52 colonnes */
            grid-template-columns: repeat(52, 1fr); 
            grid-template-rows: repeat(7, 1fr); 
            gap: 4px; width: max-content; margin: 0 auto;
        }
        .day-square { width: 13px; height: 13px; border-radius: 3px; cursor: pointer; transition: transform 0.1s; position: relative; }
        .day-square:hover { transform: scale(1.3); z-index: 10; border: 1px solid rgba(0,0,0,0.2); }
        
        /* Les couleurs de la heatmap (du vide au très foncé) */
        .level-0 { background-color: #ebedf0; }
        .level-1 { background-color: #9be9a8; }
        .level-2 { background-color: #40c463; }
        .level-3 { background-color: #30a14e; }
        .level-4 { background-color: #216e39; }

        .months-labels { display: flex; justify-content: space-between; width: 884px; margin: 0 auto 10px auto; color: #767676; font-size: 0.8em; }

        /* ------------------------------------------- */
        /* 2. CONSTELLATION (BUBBLE CHART)             */
        /* ------------------------------------------- */
        .chart-card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); height: 450px; }

        /* ------------------------------------------- */
        /* 3. SPOTIFY WRAPPED CARD                     */
        /* ------------------------------------------- */
        .wrapped-container { display: flex; justify-content: center; margin-top: 40px; }
        .wrapped-card {
            width: 350px; height: 600px; border-radius: 20px; padding: 30px; box-sizing: border-box;
            /* Le fameux dégradé explosif de Spotify */
            background: linear-gradient(145deg, #FF0A6C 0%, #2D27FF 100%);
            color: white; box-shadow: 0 20px 40px rgba(45,39,255,0.4);
            display: flex; flex-direction: column; justify-content: space-between;
            position: relative; overflow: hidden; transition: transform 0.3s;
        }
        .wrapped-card:hover { transform: scale(1.02); }
        
        /* Cercles décoratifs en arrière-plan */
        .wrapped-card::before { content: ''; position: absolute; top: -50px; right: -50px; width: 200px; height: 200px; background: rgba(255,255,255,0.1); border-radius: 50%; }
        .wrapped-card::after { content: ''; position: absolute; bottom: -80px; left: -80px; width: 250px; height: 250px; background: rgba(255,255,255,0.1); border-radius: 50%; }

        .w-header { font-size: 1.2em; font-weight: bold; letter-spacing: 2px; z-index: 1; }
        .w-title { font-size: 3.5em; font-weight: 900; line-height: 1; margin: 20px 0; z-index: 1; text-shadow: 2px 2px 0px rgba(0,0,0,0.2); }
        .w-stats { z-index: 1; background: rgba(0,0,0,0.2); padding: 20px; border-radius: 15px; backdrop-filter: blur(5px); }
        .w-label { font-size: 0.8em; text-transform: uppercase; color: #ff9ed2; font-weight: bold; margin-bottom: 5px; margin-top: 15px; }
        .w-val { font-size: 1.5em; font-weight: 900; margin-bottom: 10px; }
        .w-footer { text-align: center; font-size: 0.9em; font-weight: bold; opacity: 0.8; z-index: 1; }

        /* Tooltip style */
        [data-title]:hover::after {
            content: attr(data-title);
            position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%);
            background: #333; color: white; padding: 4px 8px; border-radius: 4px;
            font-size: 12px; white-space: nowrap; z-index: 100;
            pointer-events: none; margin-bottom: 5px;
        }
    </style>
</head>
<body>

    <div class="container">
        <h1 style="text-align: center; color: #257059;">✨ Composants Visuels (Démo 2)</h1>
        
        <!-- 1. HEATMAP GITHUB -->
        <h2>1. La Heatmap (Le calendrier des streams)</h2>
        <p class="desc">Chaque carré représente un jour de l'année. Plus c'est foncé, plus Ariana a eu de streams ! Passe la souris sur un carré.</p>
        
        <div class="heatmap-card">
            <div class="months-labels">
                <span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span>
                <span>Jul</span><span>Aug</span><span>Sep</span><span>Oct</span><span>Nov</span><span>Dec</span>
            </div>
            <div class="heatmap-grid" id="heatmap-container">
                <!-- Les carrés seront générés par JavaScript -->
            </div>
        </div>

        <!-- 2. CONSTELLATION BUBBLE CHART -->
        <h2>2. La Constellation des Chansons (Bubble Chart)</h2>
        <p class="desc">Une galaxie musicale ! L'axe horizontal = Date de sortie. L'axe vertical = Peak position (1 = le plus haut). La taille de la bulle = Nombre de streams.</p>
        <div class="chart-card">
            <canvas id="bubbleChart"></canvas>
        </div>

        <!-- 3. SPOTIFY WRAPPED CARD -->
        <h2>3. Carte Bilan "Spotify Wrapped"</h2>
        <p class="desc">Un design audacieux pour faire des bilans annuels (à exporter sur Insta/Twitter !).</p>
        
        <div class="wrapped-container">
            <div class="wrapped-card">
                <div class="w-header">2026 WRAPPED</div>
                <div class="w-title">ARIANA GRANDE</div>
                
                <div class="w-stats">
                    <div class="w-label" style="margin-top:0;">Total Streams</div>
                    <div class="w-val">68,424,741,456</div>
                    
                    <div class="w-label">Top Song</div>
                    <div class="w-val">we can't be friends</div>
                    
                    <div class="w-label">Best Day</div>
                    <div class="w-val">May 29 (17.4M)</div>
                </div>

                <div class="w-footer">Spotify Stats Dashboard</div>
            </div>
        </div>

    </div>

    <script>
        // --------------------------------------------------------
        // JS POUR LA HEATMAP
        // On génère 364 carrés (52 semaines x 7 jours) avec des couleurs aléatoires
        // --------------------------------------------------------
        const heatmap = document.getElementById('heatmap-container');
        for (let i = 0; i < 364; i++) {
            const square = document.createElement('div');
            
            // On simule une donnée (ex: un gros pic vers la case 150 pour la sortie d'un album)
            let level = Math.floor(Math.random() * 2); // De base: 0 ou 1 (jours normaux)
            if (i > 140 && i < 160) level = Math.floor(Math.random() * 3) + 2; // Grosse semaine : 2, 3 ou 4
            if (i % 30 === 0) level = 4; // Des pics réguliers
            
            square.className = `day-square level-${level}`;
            
            // Petit tooltip fictif
            let streamsMock = (level * 5 + Math.floor(Math.random()*5)) + "M";
            if(level === 0) streamsMock = "4M";
            square.setAttribute('data-title', `Day ${i+1} : ${streamsMock} streams`);
            
            heatmap.appendChild(square);
        }

        // --------------------------------------------------------
        // JS POUR LE BUBBLE CHART (CONSTELLATION)
        // --------------------------------------------------------
        const ctx = document.getElementById('bubbleChart').getContext('2d');
        new Chart(ctx, {
            type: 'bubble',
            data: {
                datasets: [
                    {
                        label: 'thank u, next (Album)',
                        data: [
                            {x: 2019.1, y: 1, r: 28}, // 7 rings (Grosse bulle, top 1)
                            {x: 2019.2, y: 1, r: 22}, // tun
                            {x: 2019.3, y: 2, r: 15}  // buwygib
                        ],
                        backgroundColor: 'rgba(255, 105, 180, 0.6)', // Rose
                        borderColor: 'rgba(255, 105, 180, 1)'
                    },
                    {
                        label: 'Dangerous Woman (Album)',
                        data: [
                            {x: 2016.4, y: 3, r: 16}, // DW
                            {x: 2016.6, y: 4, r: 19}, // Side to side
                            {x: 2016.8, y: 13, r: 20} // Into You
                        ],
                        backgroundColor: 'rgba(54, 162, 235, 0.6)', // Bleu
                        borderColor: 'rgba(54, 162, 235, 1)'
                    },
                    {
                        label: 'eternal sunshine (Album)',
                        data: [
                            {x: 2024.1, y: 1, r: 12}, // yes, and?
                            {x: 2024.3, y: 1, r: 20}, // wcbf
                            {x: 2024.5, y: 5, r: 10}  // the boy is mine
                        ],
                        backgroundColor: 'rgba(217, 83, 79, 0.6)', // Rouge
                        borderColor: 'rgba(217, 83, 79, 1)'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { 
                        title: { display: true, text: 'Release Year' },
                        min: 2015, max: 2025
                    },
                    y: { 
                        reverse: true, // IMPORTANT: on inverse l'axe Y pour que la position #1 soit EN HAUT !
                        title: { display: true, text: 'Peak Position' },
                        min: 1, max: 20
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Peak: #${context.raw.y} | Streams size: ${context.raw.r}`;
                            }
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

with open("demo_visuelle2.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Fichier 'demo_visuelle2.html' généré avec succès ! Ouvre-le dans ton navigateur.")