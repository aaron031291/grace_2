import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import AppChat from './AppChat.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppChat />
  </StrictMode>,
)
