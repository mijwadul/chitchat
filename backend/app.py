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
def generate_ai_response(messages):
    try:
        chat_completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1-0528", # Atau model pilihan Anda
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1
        )
        ai_response_content = chat_completion.choices[0].message.content
        
        # --- TAMBAHKAN KODE PEMBESIHAN INI ---
        # Menghapus tag <think>...</think> dari respons AI
        import re
        # Pola regex untuk menemukan <think>...</think> dan isinya (non-greedy)
        cleaned_response = re.sub(r'<think>(.*?)</think>', '', ai_response_content, flags=re.DOTALL)
        # Menghapus spasi berlebih atau baris kosong yang mungkin dihasilkan dari penghapusan
        cleaned_response = cleaned_response.strip()
        # --- AKHIR KODE PEMBESIHAN ---

        return cleaned_response # Mengembalikan respons yang sudah dibersihkan
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
        # Untuk chat umum, AI bisa langsung merespons pesan user
        # Jika Anda ingin riwayat chat, frontend perlu mengirim array 'messages' lengkap
        ai_response = generate_ai_response([{"role": "user", "content": user_message}])
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

        # --- PERBAIKAN PROMPT DI SINI UNTUK FORMAT OUTPUT ---
        system_prompt = (
            f"Anda adalah seorang pengembang perangkat lunak ahli yang menganalisis repositori GitHub. "
            f"Tugas Anda adalah memberikan jawaban yang komprehensif, relevan, dan terstruktur berdasarkan konten repositori yang disediakan dan pertanyaan pengguna. "
            f"Fokus pada tujuan proyek, teknologi yang digunakan, struktur utama, dan fitur kunci. "
            f"Jika informasi tidak cukup karena konten dipotong, jelaskan batasannya. "
            f"**Format respons Anda sebagai daftar poin yang jelas (menggunakan tanda hubung '-') atau beberapa paragraf dengan judul bagian kecil jika relevan. Gunakan markdown untuk pemformatan jika sesuai (misalnya, bold untuk nama kunci).** "
            f"Jawaban harus dalam bahasa Indonesia."
        )

        repo_context = (
            f"Berikut adalah konten file dari repositori GitHub yang relevan (dipotong jika terlalu panjang):\n"
            f"```\n{repo_content_string}\n```"
        )
        
        messages_for_ai = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{repo_context}\n\nPertanyaan saya: {question}"}
        ]
        # --- AKHIR PERBAIKAN PROMPT ---

        ai_response = generate_ai_response(messages_for_ai)
        return jsonify({"response": ai_response})

    except Exception as e:
        print(f"Error menganalisis repo GitHub: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)