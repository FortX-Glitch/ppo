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
    return "Serveur Actif", 200

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
            # On force un format mobile (souvent moins protégé que le 1080p)
            'format': 'best[ext=mp4]/18/best',
            'outtmpl': os.path.join(tmpdir, f'tubehub_{unique_id}_%(title)s.%(ext)s'),
            'noplaylist': True,
            'nocheckcertificate': True,
            'quiet': False,
            'no_warnings': True,
            
            # --- STRATÉGIE MOBILE (Plus discret) ---
            'impersonate': 'chrome', # Utilise curl_cffi pour bypass Cloudflare
            'extractor_args': {
                'generic': ['impersonate'],
                'youtube': ['player_client=android'] 
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5',
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)
        
        return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))
    
    except Exception as e:
        # On force l'affichage pour voir ENFIN ce qui se passe
        print(f"DEBUG: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
