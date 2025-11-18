import { apiUrl, WS_BASE_URL } from './config';
/**
 * UI Notification System for Book Ingestion Events
 * Integrates with event bus to show toasts and co-pilot messages
 */

export type NotificationType = 'success' | 'info' | 'warning' | 'error';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: Date;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

class NotificationManager {
  private subscribers: Set<(notification: Notification) => void> = new Set();
  private notifications: Notification[] = [];

  subscribe(callback: (notification: Notification) => void) {
    this.subscribers.add(callback);
    return () => this.subscribers.delete(callback);
  }

  notify(notification: Omit<Notification, 'id' | 'timestamp'>) {
    const fullNotification: Notification = {
      ...notification,
      id: `notif-${Date.now()}-${Math.random()}`,
      timestamp: new Date(),
      duration: notification.duration || 5000,
    };

    this.notifications.push(fullNotification);
    this.subscribers.forEach(callback => callback(fullNotification));

    return fullNotification.id;
  }

  success(title: string, message: string, duration?: number) {
    return this.notify({ type: 'success', title, message, duration });
  }

  info(title: string, message: string, duration?: number) {
    return this.notify({ type: 'info', title, message, duration });
  }

  warning(title: string, message: string, duration?: number) {
    return this.notify({ type: 'warning', title, message, duration });
  }

  error(title: string, message: string, duration?: number) {
    return this.notify({ type: 'error', title, message, duration: duration || 8000 });
  }

  dismiss(id: string) {
    this.notifications = this.notifications.filter(n => n.id !== id);
  }

  getAll() {
    return this.notifications;
  }

  clear() {
    this.notifications = [];
  }
}

export const notifications = new NotificationManager();

// Book-specific notification helpers
export const bookNotifications = {
  bookDetected: (filename: string) => {
    notifications.info(
      '📚 Book Detected',
      `${filename} queued for processing`,
      4000
    );
  },

  schemaApproved: (title: string) => {
    notifications.success(
      '✅ Schema Approved',
      `${title} ready for ingestion`,
      4000
    );
  },

  ingestionStarted: (title: string) => {
    notifications.info(
      '🔄 Ingestion Started',
      `Processing ${title}...`,
      4000
    );
  },

  ingestionProgress: (title: string, stage: string) => {
    notifications.info(
      '⚙️ Processing',
      `${title}: ${stage}`,
      3000
    );
  },

  ingestionComplete: (title: string, stats: { chunks: number; insights: number }) => {
    notifications.success(
      '✅ Ingestion Complete',
      `${title} processed: ${stats.chunks} chunks, ${stats.insights} insights`,
      6000
    );
  },

  verificationStarted: (title: string) => {
    notifications.info(
      '🔍 Verification Started',
      `Running trust tests for ${title}`,
      3000
    );
  },

  verificationComplete: (title: string, trustScore: number) => {
    const emoji = trustScore >= 0.9 ? '🎉' : trustScore >= 0.7 ? '👍' : '⚠️';
    const type = trustScore >= 0.9 ? 'success' : trustScore >= 0.7 ? 'info' : 'warning';
    
    notifications.notify({
      type,
      title: `${emoji} Verification Complete`,
      message: `${title} trust score: ${(trustScore * 100).toFixed(0)}%`,
      duration: 6000,
    });
  },

  lowTrustScore: (title: string, trustScore: number) => {
    notifications.warning(
      '⚠️ Low Trust Score',
      `${title} (${(trustScore * 100).toFixed(0)}%) flagged for review`,
      8000
    );
  },

  ingestionFailed: (title: string, error: string) => {
    notifications.error(
      '❌ Ingestion Failed',
      `${title}: ${error}`,
      10000
    );
  },

  readyForQueries: (title: string) => {
    notifications.success(
      '🤖 Ready for Queries',
      `${title} available in co-pilot!`,
      5000
    );
  },
};

// Event bus integration
export function setupBookEventListeners() {
  const eventSource = new EventSource(apiUrl('/api/events/stream');

  eventSource.addEventListener('file.created', (event) => {
    const data = JSON.parse(event.data);
    if (data.is_book) {
      bookNotifications.bookDetected(data.path.split('/').pop());
    }
  });

  eventSource.addEventListener('schema.proposal.decided', (event) => {
    const data = JSON.parse(event.data);
    if (data.decision.status === 'approved') {
      bookNotifications.schemaApproved(data.proposal.file_path.split('/').pop());
    }
  });

  eventSource.addEventListener('book.ingestion.metadata_extraction', (event) => {
    const data = JSON.parse(event.data);
    bookNotifications.ingestionStarted(data.file.split('/').pop());
  });

  eventSource.addEventListener('book.ingestion.chunking', (event) => {
    const data = JSON.parse(event.data);
    bookNotifications.ingestionProgress(
      data.document_id,
      `Chunking ${data.chapters} chapters`
    );
  });

  eventSource.addEventListener('book.ingestion.completed', (event) => {
    const data = JSON.parse(event.data);
    bookNotifications.ingestionComplete(data.file_path?.split('/').pop() || 'Book', {
      chunks: data.chunks_created || 0,
      insights: data.insights_created || 0,
    });
  });

  eventSource.addEventListener('verification.book.requested', (event) => {
    const data = JSON.parse(event.data);
    bookNotifications.verificationStarted(data.document_id);
  });

  eventSource.addEventListener('verification.book.completed', (event) => {
    const data = JSON.parse(event.data);
    const trustScore = data.trust_score || 0;
    
    bookNotifications.verificationComplete(data.document_id, trustScore);

    if (trustScore < 0.7) {
      bookNotifications.lowTrustScore(data.document_id, trustScore);
    } else if (trustScore >= 0.9) {
      bookNotifications.readyForQueries(data.document_id);
    }
  });

  eventSource.addEventListener('book.ingestion.failed', (event) => {
    const data = JSON.parse(event.data);
    bookNotifications.ingestionFailed(
      data.file_path?.split('/').pop() || 'Book',
      data.error || 'Unknown error'
    );
  });

  return () => eventSource.close();
}
