from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import uuid

app = Flask(__name__)
# Autorise ton site Netlify à communiquer avec ce serveur
CORS(app)

# Route d'accueil pour que Render reste au vert (Health Check)
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

        # Création d'un dossier temporaire sécurisé
        tmpdir = tempfile.gettempdir()
        unique_id = str(uuid.uuid4())[:8]
        
        ydl_opts = {
            # On force le MP4 déjà mixé pour ne pas avoir besoin de FFmpeg sur Render
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(tmpdir, f'tubehub_{unique_id}_%(title)s.%(ext)s'),
            'noplaylist': True,
            'nocheckcertificate': True,
            
            # --- CONFIGURATION FURTIVE ---
            # On imite une version spécifique de Chrome
            'impersonate': 'chrome-110', 
            'extractor_args': {
                'generic': ['impersonate'],
            },
            # On ajoute des headers de navigation réels
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="110", "Chromium";v="110"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Upgrade-Insecure-Requests': '1',
            },
            'quiet': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraction et téléchargement
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)
        
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=os.path.basename(file_path)
        )
    
    except Exception as e:
        # Affiche l'erreur détaillée dans les logs Render pour nous aider
        print(f"ERREUR TECHNIQUE : {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Récupération du port dynamique de Render
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
