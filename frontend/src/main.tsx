import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import GraceSimpleChat from './GraceSimpleChat.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <GraceSimpleChat />
    </ErrorBoundary>
  </StrictMode>,
)
