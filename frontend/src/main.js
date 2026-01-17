import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css' // <--- CHANGE THIS (Import your original CSS)
import App from './App.js'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)