from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import uuid

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        video_url = data.get('url')
        
        if not video_url:
            return jsonify({"error": "URL manquante"}), 400

        # Dossier temporaire système
        tmpdir = tempfile.gettempdir()
        # ID unique pour éviter les conflits de cache
        unique_id = str(uuid.uuid4())[:8]
        
        # Options yt-dlp optimisées
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(tmpdir, f'tubehub_{unique_id}_%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Récupérer les infos et télécharger
            info = ydl.extract_info(video_url, download=True)
            # Obtenir le chemin exact du fichier créé
            file_path = ydl.prepare_filename(info)
        
        # Envoyer le fichier au navigateur
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=os.path.basename(file_path)
        )
    
    except Exception as e:
        print(f"Détail de l'erreur : {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # On lance sur le port 5000
    app.run(debug=True, port=5000)