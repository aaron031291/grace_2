import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import GraceEnterpriseUI from './GraceEnterpriseUI.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'
import { ChatProvider } from './context/ChatContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <ChatProvider>
        <GraceEnterpriseUI />
      </ChatProvider>
    </ErrorBoundary>
  </StrictMode>,
)
