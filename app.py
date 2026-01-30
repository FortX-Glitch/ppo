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
    return "Serveur TubeHub : Operationnel", 200

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
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(tmpdir, f'tubehub_{unique_id}_%(title)s.%(ext)s'),
            'noplaylist': True,
            'nocheckcertificate': True,
            # --- CORRECTIF CLOUDFLARE ICI ---
            'impersonate': 'chrome',
            'extractor_args': {
                'generic': ['impersonate'],
                'youtube': ['player_client=android,web'] # Optionnel pour aider YouTube
            },
            # -------------------------------
            'quiet': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)
        
        return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))
    
    except Exception as e:
        # On affiche l'erreur complète pour voir si Cloudflare bloque encore
        print(f"ERREUR CLOUDFLARE : {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
