from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import uuid

app = Flask(__name__)
# Autorise les requêtes provenant de votre site Netlify
CORS(app)

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        video_url = data.get('url')
        
        if not video_url:
            return jsonify({"error": "URL manquante"}), 400

        # Dossier temporaire sur le serveur Render
        tmpdir = tempfile.gettempdir()
        unique_id = str(uuid.uuid4())[:8]
        
        # Options avancées pour contourner les protections (Cloudflare/Anti-bot)
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(tmpdir, f'tubehub_{unique_id}_%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': False,
            # Argument d'impersonation pour imiter un vrai navigateur
            'extractor_args': {
                'generic': ['impersonate'],
            },
            # Simulation d'un navigateur récent
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraction et téléchargement
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)
        
        # Envoi du fichier généré au client
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=os.path.basename(file_path)
        )
    
    except Exception as e:
        error_msg = str(e)
        print(f"Détail de l'erreur : {error_msg}")
        return jsonify({"error": error_msg}), 500

# CONFIGURATION CRUCIALE POUR RENDER
if __name__ == '__main__':
    # Render définit automatiquement une variable d'environnement PORT
    port = int(os.environ.get('PORT', 5000))
    # '0.0.0.0' est obligatoire pour être accessible sur le web
    app.run(host='0.0.0.0', port=port)
