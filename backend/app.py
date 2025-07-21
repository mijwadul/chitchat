# backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
# Hapus: import together # Kita tidak akan menggunakan together.Complete.create lagi
from together import Together # Import kelas Together untuk client baru

import traceback # Import traceback untuk debugging error

# Impor layanan yang baru
from services.github_service import get_repo_contents

load_dotenv()

app = Flask(__name__)
CORS(app) # Mengizinkan CORS untuk semua rute

# --- PERUBAHAN KRITIS: Inisialisasi client Together AI di sini ---
# Ini akan membaca TOGETHER_API_KEY dari environment variable secara otomatis
client = Together()
# --- AKHIR PERUBAHAN KRITIS ---

# Konfigurasi
MAX_CHARS = 2000 # Tetapkan batas karakter yang lebih kecil untuk pengujian

# Fungsi untuk menghasilkan respons AI
def generate_ai_response(prompt):
    try:
        # --- PERUBAHAN KRITIS: Menggunakan client.chat.completions.create ---
        chat_completion = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", # Menggunakan model yang Anda temukan
            messages=[
              {
                "role": "user",
                "content": prompt # Mengirim prompt sebagai pesan user
              }
            ],
            max_tokens=500, # Batasi jumlah token respons dari AI
            temperature=0.7,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1
        )
        # --- PERUBAHAN KRITIS: Mengakses respons yang benar ---
        return chat_completion.choices[0].message.content
        # --- AKHIR PERUBAHAN KRITIS ---
    except Exception as e:
        print(f"Error saat memanggil Together AI: {e}")
        traceback.print_exc()
        raise Exception("Gagal mendapatkan respons dari AI.")

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "Pesan tidak boleh kosong"}), 400

    try:
        ai_response = generate_ai_response(user_message)
        return jsonify({"response": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-github-repo', methods=['POST'])
def analyze_github_repo():
    data = request.json
    repo_url = data.get('repo_url')
    question = data.get('question')

    if not repo_url or not question:
        return jsonify({"error": "URL repositori dan pertanyaan tidak boleh kosong"}), 400

    try:
        repo_contents_dict = get_repo_contents(repo_url)
        
        repo_content_string = ""
        for file_path, content in repo_contents_dict.items():
            repo_content_string += f"--- {file_path} ---\n{content}\n\n"

        if len(repo_content_string) > MAX_CHARS:
            repo_content_string = repo_content_string[:MAX_CHARS] + "\n... (konten dipotong karena terlalu panjang)"

        prompt = (
            f"Saya ingin Anda menganalisis repositori GitHub ini dan menjawab pertanyaan saya.\n"
            f"Konten repositori (dipotong jika terlalu panjang):\n```\n{repo_content_string}\n```\n\n"
            f"Pertanyaan: {question}\n"
            f"Berikan jawaban yang ringkas dan relevan berdasarkan konten yang diberikan."
        )

        # --- TAMBAHKAN BARIS DEBUGGING INI ---
        print(f"DEBUG: Length of final prompt sent to AI: {len(prompt)}")
        # ------------------------------------

        ai_response = generate_ai_response(prompt)
        return jsonify({"response": ai_response})

    except Exception as e:
        print(f"Error menganalisis repo GitHub: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)