import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import GraceShell from './GraceShell.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <GraceShell />
    </ErrorBoundary>
  </StrictMode>,
)
