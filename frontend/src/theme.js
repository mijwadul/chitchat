// src/theme.js
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Contoh warna biru
    },
    secondary: {
      main: '#dc004e', // Contoh warna merah
      light: '#fce4ec', // Untuk latar belakang pesan AI
    },
    info: {
      main: '#2196f3', // Contoh warna biru muda
      light: '#e0f7fa', // Untuk latar belakang pesan user
    },
    background: {
      default: '#f4f6f8', // Contoh warna latar belakang aplikasi
    },
    divider: '#e0e0e0', // Contoh warna untuk pembatas
  },
  spacing: 8, // Default spacing unit (misal: theme.spacing(1) = 8px)
  shape: {
    borderRadius: 8, // Default border radius
  },
  breakpoints: {
    values: {
      xs: 0,
      sm: 600, // Lebar maksimum untuk komponen chat
      md: 900,
      lg: 1200,
      xl: 1536,
    },
  },
});

export default theme;