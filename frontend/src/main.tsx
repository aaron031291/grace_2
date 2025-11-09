import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import GraceOrb from './GraceOrb.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <GraceOrb />
    </ErrorBoundary>
  </StrictMode>,
)
