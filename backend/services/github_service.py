# backend/services/github_service.py
from github import Github, GithubException
import os

github_token = os.getenv("GITHUB_TOKEN")
if github_token:
    g = Github(github_token)
else:
    print("Peringatan: GITHUB_TOKEN tidak ditemukan di .env. Akses ke repositori mungkin terbatas.")
    g = Github() # Akses anonim dengan batasan rate yang lebih rendah

def get_repo_contents(repo_url):
    """
    Mengambil konten (file dan folder) dari sebuah repositori GitHub.
    Mengembalikan kamus {nama_file: konten_file}.
    Hanya membaca file teks untuk saat ini.
    """
    try:
        # Mengurai URL untuk mendapatkan owner/org dan repo name
        # Lebih baik menggunakan pustaka urlparse untuk robust
        from urllib.parse import urlparse
        parsed_url = urlparse(repo_url)
        path_parts = [part for part in parsed_url.path.split('/') if part]
        
        if len(path_parts) < 2:
            raise ValueError("URL repositori tidak valid. Contoh: https://github.com/owner/repo")
        
        owner_repo_name = f"{path_parts[0]}/{path_parts[1]}" # Ini akan menjadi "owner/repo"

        print(f"DEBUG: Input URL: {repo_url}")
        print(f"DEBUG: Parsed path parts: {path_parts}")
        print(f"DEBUG: Formed owner_repo_name: {owner_repo_name}")
        repo = g.get_repo(owner_repo_name) 
        # --- AKHIR PERUBAHAN KRITIS ---

        contents = {}

        # Fungsi rekursif untuk membaca konten folder
        def _read_dir(dir_content):
            for content_file in dir_content:
                if content_file.type == "dir":
                    # Rekursif untuk sub-folder
                    _read_dir(repo.get_contents(content_file.path)) # Pastikan path diperbarui
                elif content_file.type == "file":
                    # Hanya baca file teks untuk menghindari biner
                    if content_file.encoding == "base64":
                        try:
                            file_content = content_file.decoded_content.decode('utf-8')
                            contents[content_file.path] = file_content
                        except UnicodeDecodeError:
                            # Lewati file biner atau yang tidak dapat didekode
                            pass
                    else:
                        # Jika encoding bukan base64, coba ambil langsung (jarang)
                        contents[content_file.path] = content_file.content
            total_chars = sum(len(content) for content in contents.values())
            print(f"DEBUG: Total files fetched: {len(contents)}")
            print(f"DEBUG: Total characters of content fetched: {total_chars}")            

        # Mulai membaca dari root repositori
        _read_dir(repo.get_contents(""))

        return contents

    except GithubException as e:
        print(f"GitHub API Error: {e.status} - {e.data}")
        raise Exception(f"Gagal mengakses repositori GitHub: {e.data.get('message', 'Terjadi kesalahan')}")
    except ValueError as e: # Tambahkan penanganan untuk ValueError dari parsing URL
        raise Exception(f"Error parsing repo URL: {e}")
    except Exception as e:
        print(f"Error fetching GitHub content: {e}")
        raise Exception(f"Terjadi kesalahan saat mengambil konten GitHub: {e}")

# Fungsi untuk mendapatkan info repo dasar (opsional)
def get_repo_info(repo_url):
    try:
        # --- PERUBAHAN KRITIS DI SINI ---
        from urllib.parse import urlparse
        parsed_url = urlparse(repo_url)
        path_parts = [part for part in parsed_url.path.split('/') if part]
        
        if len(path_parts) < 2:
            raise ValueError("URL repositori tidak valid.")
        
        owner_repo_name = f"{path_parts[0]}/{path_parts[1]}"
        print(f"DEBUG: Input URL (info): {repo_url}")
        print(f"DEBUG: Parsed path parts (info): {path_parts}")
        print(f"DEBUG: Formed owner_repo_name (info): {owner_repo_name}")
        repo = g.get_repo(owner_repo_name)
        # --- AKHIR PERUBAHAN KRITIS ---

        return {
            "name": repo.name,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "url": repo.html_url
        }
    except GithubException as e:
        raise Exception(f"Gagal mendapatkan info repo: {e.data.get('message', 'Terjadi kesalahan')}")
    except ValueError as e:
        raise Exception(f"Error parsing repo URL: {e}")
    except Exception as e:
        raise Exception(f"Terjadi kesalahan saat mengambil info repo: {e}")