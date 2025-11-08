import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './GraceVSCode.css'
import GraceVSCode from './GraceVSCode.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <GraceVSCode />
    </ErrorBoundary>
  </StrictMode>,
)
