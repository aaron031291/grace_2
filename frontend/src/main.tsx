import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import GraceComplete from './GraceComplete.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <GraceComplete />
    </ErrorBoundary>
  </StrictMode>,
)
