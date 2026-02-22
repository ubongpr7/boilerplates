import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import StoreProvider from '../redux/provider.tsx'
import ThemeProvider from '../redux/theme-provider.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <StoreProvider>
    <ThemeProvider  >
      <App />
      </ThemeProvider>
    </StoreProvider>
  </StrictMode>,
)
