import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import GraceFinal from './GraceFinal.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <GraceFinal />
  </StrictMode>,
)
