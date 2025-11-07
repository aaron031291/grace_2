import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './GraceAgentic.css'
import GraceBidirectional from './GraceBidirectional.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <GraceBidirectional />
    </ErrorBoundary>
  </StrictMode>,
)
