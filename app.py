from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import uuid

app = Flask(__name__)
# CORS est configuré pour autoriser les requêtes de ton site Netlify
CORS(app)

# Route "Health Check" pour que Render valide le déploiement
@app.route('/')
def home():
    return "Serveur TubeHub : Operationnel", 200

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        video_url = data.get('url')
        
        if not video_url:
            return jsonify({"error": "URL manquante"}), 400

        # Utilisation du dossier temporaire du serveur
        tmpdir = tempfile.gettempdir()
        unique_id = str(uuid.uuid4())[:8]
        
        # Options optimisées pour éviter l'erreur 500 et le besoin de ffmpeg
        ydl_opts = {
            # On force le MP4 déjà combiné pour éviter les erreurs de fusion
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(tmpdir, f'tubehub_{unique_id}_%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': False,
            'no_warnings': True,
            # Bypass Cloudflare / Anti-bot
            'impersonate': 'chrome',
            'extractor_args': {
                'generic': ['impersonate'],
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraction des informations et téléchargement
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)
        
        # Envoi du fichier au navigateur
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=os.path.basename(file_path)
        )
    
    except Exception as e:
        # Affiche l'erreur précise dans les logs Render pour le debug
        print(f"ERREUR SERVEUR: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Récupère le port via Render ou utilise 10000 par défaut
    port = int(os.environ.get('PORT', 10000))
    # host='0.0.0.0' est obligatoire pour être accessible depuis Netlify
    app.run(host='0.0.0.0', port=port)
