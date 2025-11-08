import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import GraceFinal from './GraceFinal.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <GraceFinal />
    </ErrorBoundary>
  </StrictMode>,
)
