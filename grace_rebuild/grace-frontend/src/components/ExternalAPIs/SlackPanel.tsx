/**
 * Slack Integration Panel
 * 
 * UI for Slack operations with governance
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';

interface SlackChannel {
  id: string;
  name: string;
  is_channel: boolean;
  is_private: boolean;
  is_archived: boolean;
  num_members: number;
  topic: string;
  purpose: string;
}

interface SlackMessage {
  type: string;
  user: string;
  text: string;
  ts: string;
  thread_ts?: string;
}

export function SlackPanel() {
  const [channels, setChannels] = useState<SlackChannel[]>([]);
  const [messages, setMessages] = useState<SlackMessage[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<string>('');
  const [loading, setLoading] = useState(false);
  
  // Message form
  const [messageText, setMessageText] = useState('');

  const fetchChannels = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/external/slack/channels');
      const data = await response.json();
      setChannels(data.channels || []);
    } catch (error) {
      console.error('Failed to fetch channels:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (channelId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/external/slack/channels/${channelId}/history`);
      const data = await response.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!selectedChannel || !messageText) {
      alert('Please select a channel and enter a message');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/external/slack/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          channel: selectedChannel,
          text: messageText
        })
      });

      const result = await response.json();
      
      if (response.ok) {
        alert('Message sent successfully!');
        setMessageText('');
        fetchMessages(selectedChannel);
      } else {
        alert(`Failed to send message: ${result.detail}`);
      }
    } catch (error) {
      alert(`Error sending message: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChannels();
  }, []);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>💬 Slack Integration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            {/* Channels List */}
            <div className="col-span-1">
              <h3 className="text-lg font-semibold mb-2">Channels</h3>
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {channels.map((channel) => (
                  <div
                    key={channel.id}
                    className={`p-3 border rounded cursor-pointer hover:bg-gray-50 ${
                      selectedChannel === channel.id ? 'border-blue-500 bg-blue-50' : ''
                    }`}
                    onClick={() => {
                      setSelectedChannel(channel.id);
                      fetchMessages(channel.id);
                    }}
                  >
                    <div className="font-semibold">
                      {channel.is_private ? '🔒' : '#'} {channel.name}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {channel.num_members} members
                    </div>
                    {channel.topic && (
                      <div className="text-xs text-gray-500 mt-1 truncate">
                        {channel.topic}
                      </div>
                    )}
                    {channel.is_archived && (
                      <Badge variant="outline" className="mt-1">Archived</Badge>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Messages & Send */}
            <div className="col-span-2 space-y-4">
              {selectedChannel && (
                <>
                  {/* Send Message */}
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Send Message</h3>
                    <div className="space-y-3">
                      <Textarea
                        placeholder="Type your message..."
                        value={messageText}
                        onChange={(e) => setMessageText(e.target.value)}
                        rows={4}
                      />
                      <Button onClick={sendMessage} disabled={loading}>
                        {loading ? 'Sending...' : 'Send Message'}
                      </Button>
                    </div>
                  </div>

                  {/* Messages History */}
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Recent Messages</h3>
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {messages.map((msg, idx) => (
                        <div key={msg.ts || idx} className="p-3 border rounded bg-gray-50">
                          <div className="flex justify-between items-start">
                            <div className="font-semibold text-sm">{msg.user || 'Unknown'}</div>
                            <div className="text-xs text-gray-500">
                              {new Date(parseFloat(msg.ts) * 1000).toLocaleString()}
                            </div>
                          </div>
                          <div className="text-sm mt-1">{msg.text}</div>
                          {msg.thread_ts && (
                            <Badge variant="outline" className="mt-1">In Thread</Badge>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}

              {!selectedChannel && (
                <div className="text-center text-gray-500 py-20">
                  Select a channel to view messages
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
