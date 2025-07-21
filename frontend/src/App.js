import React, { useState } from 'react';
import { Container, TextField, Button, Box, Paper, Typography, CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { sendMessageToAI } from './services/api'; // Import fungsi API

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async () => {
    if (input.trim() === '') return;

    const newUserMessage = { sender: 'user', text: input };
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);
    setInput(''); // Bersihkan input setelah mengirim
    setLoading(true); // Aktifkan loading

    try {
      const aiResponseText = await sendMessageToAI(newUserMessage.text);
      const aiResponse = { sender: 'ai', text: aiResponseText };
      setMessages((prevMessages) => [...prevMessages, aiResponse]);
    } catch (error) {
      const errorMessage = { sender: 'ai', text: "Maaf, saya tidak dapat terhubung ke server AI saat ini." };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setLoading(false); // Nonaktifkan loading
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading) {
      handleSendMessage();
    }
  };

  return (
    <Container maxWidth="sm" sx={{ display: 'flex', flexDirection: 'column', height: '100vh', py: 2 }}>
      <Box sx={{ bgcolor: 'primary.main', color: 'white', p: 2, mb: 2, borderRadius: 1, boxShadow: 3 }}>
        <Typography variant="h5" component="h1">Chatbot AI</Typography>
      </Box>

      <Paper elevation={3} sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 2, overflow: 'hidden' }}>
        <Box sx={{ flexGrow: 1, overflowY: 'auto', mb: 2 }}>
          {messages.map((msg, index) => (
            <Box
              key={index}
              sx={{
                mb: 1,
                p: 1.5,
                borderRadius: '20px',
                maxWidth: '80%',
                wordBreak: 'break-word',
                textAlign: msg.sender === 'user' ? 'right' : 'left',
                ml: msg.sender === 'user' ? 'auto' : 0,
                mr: msg.sender === 'ai' ? 'auto' : 0,
                bgcolor: msg.sender === 'user' ? 'primary.light' : 'grey.200',
                color: msg.sender === 'user' ? 'white' : 'black',
                borderBottomLeftRadius: msg.sender === 'user' ? '20px' : '2px',
                borderBottomRightRadius: msg.sender === 'user' ? '2px' : '20px',
              }}
            >
              <Typography variant="body1">{msg.text}</Typography>
            </Box>
          ))}
        </Box>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Ketik pesan Anda..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
          />
          <Button
            variant="contained"
            endIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
            onClick={handleSendMessage}
            disabled={loading}
          >
            Kirim
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}

export default App;