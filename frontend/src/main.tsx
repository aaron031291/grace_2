import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import GraceConsole from './GraceConsole.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <GraceConsole />
    </ErrorBoundary>
  </StrictMode>,
)
