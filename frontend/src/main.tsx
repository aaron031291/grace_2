import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './GraceAgentic.css'
import GraceBidirectional from './GraceBidirectional.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <GraceBidirectional />
  </StrictMode>,
)
