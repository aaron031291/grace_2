import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import GraceConsole from './GraceConsole.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'
import { ChatProvider } from './context/ChatContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <ChatProvider>
        <GraceConsole />
      </ChatProvider>
    </ErrorBoundary>
  </StrictMode>,
)
