import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';

// Definisikan theme dasar MUI
const theme = createTheme({
  palette: {
    primary: {
      main: '#1C1C1C', // Warna primer standar MUI Blue
    },
    secondary: {
      main: '#6FCF97', // Warna sekunder
    },
  },
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline /> {/* Mereset CSS default browser */}
      <App />
    </ThemeProvider>
  </React.StrictMode>
);

reportWebVitals();