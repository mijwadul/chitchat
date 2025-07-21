# backend/services/github_service.py
from github import Github, GithubException
import os
from urllib.parse import urlparse

# --- Tambahkan ini ---
# Tambahkan fungsi traceback untuk logging yang lebih baik
import traceback
# --- Akhir tambahan ---

github_token = os.getenv("GITHUB_TOKEN")
if github_token:
    g = Github(github_token)
else:
    print("Peringatan: GITHUB_TOKEN tidak ditemukan di .env. Akses ke repositori mungkin terbatas.")
    g = Github() # Akses anonim dengan batasan rate yang lebih rendah

# --- Konfigurasi baru untuk filter file ---
RELEVANT_EXTENSIONS = [
    '.py', '.js', '.java', '.ts', '.html', '.css', '.md', '.txt', '.json',
    '.xml', '.yaml', '.yml', '.jsx', '.tsx', '.go', '.php', '.cpp', '.h', '.c',
    '.cs', '.sh', '.bash', '.fish' # Tambahkan ekstensi relevan lainnya
]
MAX_FILE_SIZE_KB = 100 # Batas ukuran file individual untuk menghindari file biner besar

# --- Pastikan `contents` didefinisikan sebelum _read_dir dipanggil ---
contents = {} # Definisi global atau passing sebagai argumen dan mengembalikannya

def _read_dir(repo, contents_dict, path=""): # Mengubah argumen menjadi repo dan contents_dict
    try:
        current_contents = repo.get_contents(path)
    except GithubException as e:
        # Tangani error jika direktori tidak dapat diakses (misalnya, folder kosong atau masalah izin)
        print(f"DEBUG: Could not read directory {path}: {e.status} - {e.data}")
        return

    for content_item in current_contents: # Ubah content_file menjadi content_item
        if content_item.type == "dir":
            _read_dir(repo, contents_dict, content_item.path) # Lewatkan repo dan contents_dict
        elif content_item.type == "file":
            file_extension = os.path.splitext(content_item.name)[1].lower()
            
            # Filter berdasarkan ekstensi dan ukuran file
            if file_extension in RELEVANT_EXTENSIONS and content_item.size <= MAX_FILE_SIZE_KB * 1024:
                try:
                    # Pastikan ini adalah file teks dan tidak terlalu besar
                    # getContent().decoded_content mengembalikan bytes, perlu di-decode
                    decoded_content = content_item.decoded_content.decode('utf-8')
                    contents_dict[content_item.path] = decoded_content
                except UnicodeDecodeError:
                    print(f"DEBUG: Skipping binary or undecodable file: {content_item.path}")
                except Exception as e:
                    print(f"DEBUG: Error reading file {content_item.path}: {e}")
                    traceback.print_exc() # Cetak traceback untuk debugging
            else:
                print(f"DEBUG: Skipping irrelevant or too large file: {content_item.path} (Type: {content_item.type}, Size: {content_item.size} bytes, Ext: {file_extension})")


def get_repo_contents(repo_url):
    """
    Mengambil konten (file dan folder) dari sebuah repositori GitHub.
    Mengembalikan kamus {nama_file: konten_file}.
    Hanya membaca file teks yang relevan.
    """
    global contents # Pastikan ini diakses sebagai global, atau lebih baik lagi, hapus global dan passing sebagai argumen
    contents = {} # Reset contents untuk setiap panggilan fungsi

    try:
        parsed_url = urlparse(repo_url)
        path_parts = [part for part in parsed_url.path.split('/') if part]
        
        if len(path_parts) < 2:
            raise ValueError("URL repositori tidak valid. Contoh: https://github.com/owner/repo")
        
        owner = path_parts[0]
        repo_name_with_git = path_parts[1]
        
        if repo_name_with_git.endswith('.git'):
            repo_name = repo_name_with_git[:-4]
        else:
            repo_name = repo_name_with_git

        owner_repo_name = f"{owner}/{repo_name}"
        
        print(f"DEBUG: Input URL: {repo_url}")
        print(f"DEBUG: Parsed path parts: {path_parts}")
        print(f"DEBUG: Formed owner_repo_name (after fix): {owner_repo_name}")
        
        repo = g.get_repo(owner_repo_name)
        
        # Panggil _read_dir dengan repo dan contents sebagai argumen
        _read_dir(repo, contents, "") 

        total_chars = sum(len(content) for content in contents.values())
        print(f"DEBUG: Total files fetched: {len(contents)}")
        print(f"DEBUG: Total characters of content fetched: {total_chars}")

        return contents

    except GithubException as e:
        print(f"GitHub API Error: {e.status} - {e.data}")
        traceback.print_exc()
        raise Exception(f"Gagal mengakses repositori GitHub: {e.data.get('message', 'Terjadi kesalahan')}")
    except ValueError as e:
        print(f"Error parsing repo URL: {e}")
        traceback.print_exc()
        raise Exception(f"Error parsing repo URL: {e}")
    except Exception as e:
        print(f"Error fetching GitHub content: {e}")
        traceback.print_exc()
        raise Exception(f"Terjadi kesalahan saat mengambil konten GitHub: {e}")

# Fungsi untuk mendapatkan info repo dasar (get_repo_info)
# ... (pastikan Anda juga menerapkan filter dan error handling yang sama jika ada di sini)
# Pastikan Anda memanggil _read_dir dengan repo dan contents_dict sebagai argumen.
def get_repo_info(repo_url):
    # Logika yang mirip dengan get_repo_contents untuk parsing URL dan mendapatkan repo
    try:
        parsed_url = urlparse(repo_url)
        path_parts = [part for part in parsed_url.path.split('/') if part]
        
        if len(path_parts) < 2:
            raise ValueError("URL repositori tidak valid.")
        
        owner = path_parts[0]
        repo_name_with_git = path_parts[1]
        
        if repo_name_with_git.endswith('.git'):
            repo_name = repo_name_with_git[:-4]
        else:
            repo_name = repo_name_with_git

        owner_repo_name = f"{owner}/{repo_name}"

        print(f"DEBUG: Input URL (info): {repo_url}")
        print(f"DEBUG: Parsed path parts (info): {path_parts}")
        print(f"DEBUG: Formed owner_repo_name (info, after fix): {owner_repo_name}")

        repo = g.get_repo(owner_repo_name)
        
        # Mengembalikan info dasar repo
        return {
            "name": repo.name,
            "owner": repo.owner.login,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "url": repo.html_url,
            "language": repo.language,
            "created_at": repo.created_at.isoformat(),
            "updated_at": repo.updated_at.isoformat()
        }
        
    except GithubException as e:
        print(f"GitHub API Error for info: {e.status} - {e.data}")
        traceback.print_exc()
        raise Exception(f"Gagal mendapatkan info repo: {e.data.get('message', 'Terjadi kesalahan')}")
    except ValueError as e:
        print(f"Error parsing repo URL for info: {e}")
        traceback.print_exc()
        raise Exception(f"Error parsing repo URL: {e}")
    except Exception as e:
        print(f"Terjadi kesalahan saat mengambil info repo: {e}")
        traceback.print_exc()
        raise Exception(f"Terjadi kesalahan saat mengambil info repo: {e}")