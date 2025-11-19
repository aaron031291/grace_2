/**
 * Reminders API Client
 * 
 * Create and manage automated reminders and scheduled tasks
 */

import { API_BASE_URL } from '../config';

export interface Reminder {
  reminder_id: string;
  user_id: string;
  message: string;
  scheduled_time: string;
  status: 'pending' | 'sent' | 'cancelled';
  created_at: string;
  sent_at?: string;
  metadata?: Record<string, any>;
}

export interface CreateReminderRequest {
  user_id: string;
  message: string;
  scheduled_time: string;
  metadata?: Record<string, any>;
}

export class RemindersAPI {
  private static baseUrl = API_BASE_URL || '';

  static async createReminder(request: CreateReminderRequest): Promise<Reminder> {
    const response = await fetch(`${this.baseUrl}/api/reminders/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create reminder' }));
      throw new Error(error.detail);
    }

    return response.json();
  }

  static async listReminders(userId: string = 'user', status?: string): Promise<Reminder[]> {
    const params = new URLSearchParams({ user_id: userId });
    if (status) params.append('status', status);

    const response = await fetch(`${this.baseUrl}/api/reminders?${params}`);

    if (!response.ok) {
      throw new Error('Failed to fetch reminders');
    }

    const data = await response.json();
    return data.reminders || [];
  }

  static async cancelReminder(reminderId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/reminders/${reminderId}/cancel`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error('Failed to cancel reminder');
    }
  }

  static parseReminderCommand(message: string): CreateReminderRequest | null {
    // Parse natural language like "remind me to X tomorrow at 3pm"
    const reminderPattern = /remind me to (.+?) (tomorrow|today|in \d+ (hour|day|minute)s?|at \d{1,2}(:\d{2})?\s*(am|pm)?)/i;
    const match = message.match(reminderPattern);
    
    if (!match) return null;
    
    const task = match[1].trim();
    const timeStr = match[2].trim();
    
    const scheduledTime = this.parseTimeString(timeStr);
    
    if (!scheduledTime) return null;
    
    return {
      user_id: 'user',
      message: task,
      scheduled_time: scheduledTime.toISOString(),
      metadata: {
        original_command: message,
        parsed_time: timeStr,
      },
    };
  }

  private static parseTimeString(timeStr: string): Date | null {
    const now = new Date();
    
    if (timeStr.toLowerCase() === 'tomorrow') {
      const tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(9, 0, 0, 0);
      return tomorrow;
    }
    
    if (timeStr.toLowerCase() === 'today') {
      const today = new Date(now);
      today.setHours(17, 0, 0, 0);
      return today;
    }
    
    // "in X hours/days"
    const inPattern = /in (\d+) (hour|day|minute)s?/i;
    const inMatch = timeStr.match(inPattern);
    if (inMatch) {
      const amount = parseInt(inMatch[1]);
      const unit = inMatch[2].toLowerCase();
      
      const future = new Date(now);
      if (unit === 'hour') future.setHours(future.getHours() + amount);
      else if (unit === 'day') future.setDate(future.getDate() + amount);
      else if (unit === 'minute') future.setMinutes(future.getMinutes() + amount);
      
      return future;
    }
    
    return null;
  }
}
