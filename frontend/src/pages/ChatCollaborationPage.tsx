import { Surface } from '../design-system';
import { ChatPanel } from '../components/ChatPanel';
import { TelemetryStrip } from '../components/TelemetryStrip';
import { UserPresenceBar } from '../components/UserPresence';
import './ChatCollaborationPage.css';

export function ChatCollaborationPage() {
  return (
    <Surface className="chat-collaboration-page">
      <div className="chat-collaboration-page__container">
        <div className="chat-collaboration-page__header">
          <UserPresenceBar currentUser="default-user" />
          <TelemetryStrip />
        </div>
        
        <div className="chat-collaboration-page__main">
          <ChatPanel />
        </div>
      </div>
    </Surface>
  );
}
