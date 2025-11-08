import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './GraceHybrid.css'
import GraceHybrid from './GraceHybrid.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <GraceHybrid />
    </ErrorBoundary>
  </StrictMode>,
)
