// frontend/src/services/api.js
const API_BASE_URL = 'http://localhost:5000'; // Sesuaikan dengan port backend Anda

export const sendMessageToAI = async (message) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error("Error calling backend API:", error);
    throw error; // Lempar ulang error agar bisa ditangani di komponen
  }
};

// Kita akan tambahkan fungsi untuk integrasi GitHub di sini nanti
export const fetchGitHubContent = async (repoUrl) => {
  // Logika untuk memanggil backend Flask yang akan berinteraksi dengan GitHub
  // Ini akan membutuhkan endpoint baru di Flask
  console.log(`Fetching content from GitHub repo: ${repoUrl}`);
  return "Fungsi integrasi GitHub belum diimplementasikan.";
};