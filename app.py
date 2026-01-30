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
        
        # CETTE CONFIGURATION EST LA CLÉ :
        # On demande 'ext=mp4' spécifiquement pour ne pas avoir besoin de FFmpeg
        ydl_opts = {
            'format': 'best[ext=mp4]/best', 
            'outtmpl': os.path.join(tmpdir, f'tubehub_{unique_id}_%(title)s.%(ext)s'),
            'noplaylist': True,
            'nocheckcertificate': True,
            'impersonate': 'chrome',
            'extractor_args': {'generic': ['impersonate']},
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # On récupère les infos et on télécharge
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)
        
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=os.path.basename(file_path)
        )
    
    except Exception as e:
        # On affiche l'erreur réelle dans les logs pour comprendre le blocage
        print(f"ERREUR TECHNIQUE: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
