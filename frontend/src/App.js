// src/App.js
import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  CircularProgress
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import ReactMarkdown from 'react-markdown'; // Impor ReactMarkdown

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [openGithubDialog, setOpenGithubDialog] = useState(false);
  const [githubRepoUrl, setGithubRepoUrl] = useState('');
  const [githubQuestion, setGithubQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false); // State baru untuk loading

  const theme = useTheme();

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '' || isLoading) return; // Jangan kirim jika input kosong atau sedang loading

    const newMessage = { text: inputMessage, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInputMessage('');
    setIsLoading(true); // Set loading ke true saat memulai permintaan

    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage }),
      });
      const data = await response.json();
      setMessages((prevMessages) => [...prevMessages, { text: data.response, sender: 'ai' }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prevMessages) => [...prevMessages, { text: 'Maaf, terjadi kesalahan.', sender: 'ai' }]);
    } finally {
      setIsLoading(false); // Set loading ke false setelah permintaan selesai (berhasil/gagal)
    }
  };

  const handleAnalyzeGithubRepo = async () => {
    if (githubRepoUrl.trim() === '' || githubQuestion.trim() === '' || isLoading) {
      alert('URL Repositori dan Pertanyaan tidak boleh kosong atau sedang memuat!');
      return;
    }

    const newMessage = { text: `Menganalisis GitHub Repo: ${githubRepoUrl} dengan pertanyaan: "${githubQuestion}"`, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setOpenGithubDialog(false);
    setGithubRepoUrl('');
    setGithubQuestion('');
    setIsLoading(true); // Set loading ke true saat memulai permintaan

    try {
      const response = await fetch('http://localhost:5000/api/analyze-github-repo', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ repo_url: githubRepoUrl, question: githubQuestion }),
      });
      const data = await response.json();
      setMessages((prevMessages) => [...prevMessages, { text: data.response, sender: 'ai' }]);
    } catch (error) {
      console.error('Error analyzing GitHub repo:', error);
      setMessages((prevMessages) => [...prevMessages, { text: 'Maaf, terjadi kesalahan saat menganalisis repositori GitHub.', sender: 'ai' }]);
    } finally {
      setIsLoading(false); // Set loading ke false setelah permintaan selesai (berhasil/gagal)
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        maxWidth: theme.breakpoints.values.sm,
        mx: 'auto',
        p: theme.spacing(2),
        bgcolor: theme.palette.background.default,
      }}
    >
      <Typography variant="h4" component="h1" gutterBottom sx={{ textAlign: 'center', color: theme.palette.primary.main }}>
        AI Chatbot dengan Analisis GitHub
      </Typography>

      <Box
        sx={{
          flexGrow: 1,
          overflowY: 'auto',
          p: theme.spacing(1),
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: theme.shape.borderRadius,
          mb: theme.spacing(2),
        }}
      >
        {messages.map((msg, index) => (
          <Paper
            key={index}
            sx={{
              p: theme.spacing(1.5),
              mb: theme.spacing(1),
              bgcolor: msg.sender === 'user' ? theme.palette.info.light : theme.palette.secondary.light,
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              borderRadius: theme.shape.borderRadius,
            }}
          >
            {msg.sender === 'ai' ? (
              <ReactMarkdown>{msg.text}</ReactMarkdown>
            ) : (
              <Typography variant="body1">{msg.text}</Typography>
            )}
          </Paper>
        ))}
        {/* Indikator Loading */}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
            <CircularProgress />
            <Typography variant="body1" sx={{ ml: 2, color: theme.palette.text.secondary }}>
              Sedang berpikir...
            </Typography>
          </Box>
        )}
      </Box>

      <Box sx={{ display: 'flex', gap: theme.spacing(1) }}>
        <IconButton color="primary" onClick={() => setOpenGithubDialog(true)} disabled={isLoading}>
          <AddIcon />
        </IconButton>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Ketik pesan Anda..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') handleSendMessage();
          }}
          disabled={isLoading} // Nonaktifkan input saat loading
        />
        <Button variant="contained" onClick={handleSendMessage} disabled={isLoading}>
          Kirim
        </Button>
      </Box>

      <Dialog open={openGithubDialog} onClose={() => setOpenGithubDialog(false)}>
        <DialogTitle>Analisis Repositori GitHub</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="URL Repositori GitHub"
            type="url"
            fullWidth
            variant="outlined"
            placeholder="misal: https://github.com/owner/repo"
            value={githubRepoUrl}
            onChange={(e) => setGithubRepoUrl(e.target.value)}
            sx={{ mb: theme.spacing(2) }}
            disabled={isLoading} // Nonaktifkan input saat loading
          />
          <TextField
            margin="dense"
            label="Pertanyaan Anda"
            type="text"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            placeholder="misal: Apa tujuan proyek ini dan teknologi utamanya?"
            value={githubQuestion}
            onChange={(e) => setGithubQuestion(e.target.value)}
            disabled={isLoading} // Nonaktifkan input saat loading
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenGithubDialog(false)} disabled={isLoading}>Batal</Button>
          <Button onClick={handleAnalyzeGithubRepo} variant="contained" color="primary" disabled={isLoading}>
            Analisis
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default App;