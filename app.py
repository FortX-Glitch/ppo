from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import uuid

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Serveur Operationnel", 200

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        video_url = data.get('url')
        if not video_url:
            return jsonify({"error": "URL manquante"}), 400

        tmpdir = tempfile.gettempdir()
        unique_id = str(uuid.uuid4())[:8]
        
        ydl_opts = {
            # Format 18 = MP4 360p (Vidéo + Audio déjà ensemble, très léger)
            'format': '18/best',
            'outtmpl': os.path.join(tmpdir, f'tubehub_{unique_id}_%(title)s.%(ext)s'),
            'noplaylist': True,
            'nocheckcertificate': True,
            'quiet': False,
            # On limite la vitesse pour ne pas faire crash le petit serveur Render
            'ratelimit': 1000000, 
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # On essaye d'extraire et télécharger
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)
        
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        # On force l'affichage de l'erreur dans la console Render
        print(f"--- ERREUR SERVEUR ---")
        print(str(e))
        print(f"-----------------------")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
