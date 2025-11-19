/**
 * User Presence Component
 * 
 * Shows active users and their status for multi-user scenarios
 */

import React, { useState, useEffect } from 'react';
import { PresenceAPI, type UserPresence } from '../api/presence';
import './UserPresence.css';

interface UserPresenceProps {
  currentUser: string;
}

export const UserPresenceBar: React.FC<UserPresenceProps> = ({ currentUser }) => {
  const [users, setUsers] = useState<UserPresence[]>([]);

  useEffect(() => {
    // Join session
    joinSession();
    
    // Send heartbeats
    const heartbeatInterval = setInterval(() => {
      PresenceAPI.sendHeartbeat(currentUser).catch(console.warn);
    }, 30000); // Every 30s

    // Load active users
    loadUsers();
    const usersInterval = setInterval(loadUsers, 10000); // Every 10s

    return () => {
      clearInterval(heartbeatInterval);
      clearInterval(usersInterval);
    };
  }, [currentUser]);

  const joinSession = async () => {
    try {
      await PresenceAPI.joinSession(currentUser, currentUser);
    } catch (error) {
      console.warn('Failed to join session:', error);
    }
  };

  const loadUsers = async () => {
    try {
      const activeUsers = await PresenceAPI.getActiveUsers();
      setUsers(activeUsers);
    } catch (error) {
      console.warn('Failed to load users:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return '#4caf50';
      case 'away': return '#ff9800';
      default: return '#888';
    }
  };

  if (users.length <= 1) return null; // Don't show if only current user

  return (
    <div className="user-presence-bar">
      <span className="presence-label">👥 Active:</span>
      <div className="presence-users">
        {users.map((user) => (
          <div
            key={user.user_id}
            className="presence-user"
            title={`${user.user_name} - ${user.status}`}
          >
            <div
              className="presence-indicator"
              style={{ backgroundColor: getStatusColor(user.status) }}
            />
            <span className="presence-name">
              {user.user_name}
              {user.user_id === currentUser && ' (you)'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
