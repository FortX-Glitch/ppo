from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import uuid

app = Flask(__name__)
CORS(app)

# --- AJOUT CRUCIAL ICI ---
# Cette route permet à Render de voir que le serveur fonctionne
@app.route('/')
def health_check():
    return "Serveur TubeHub : OK", 200
# -------------------------

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
            'quiet': False,
            'impersonate': 'chrome',
            'extractor_args': {
                'generic': ['impersonate'],
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)
        
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=os.path.basename(file_path)
        )
    
    except Exception as e:
        print(f"Erreur : {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # On force le port 10000 qui est le standard chez Render
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
