/**
 * Presence Indicators
 * Shows who's viewing/editing files and tables
 */

import { Eye, Edit, Users, Lock } from 'lucide-react';

interface PresenceInfo {
  viewers: string[];
  viewer_count: number;
  editor: string | null;
  is_locked: boolean;
  pending_requests: number;
}

interface PresenceIndicatorsProps {
  presence: PresenceInfo;
  currentUser: string;
  onRequestEdit?: () => void;
}

export function PresenceIndicators({ presence, currentUser, onRequestEdit }: PresenceIndicatorsProps) {
  const { viewers, editor, is_locked, pending_requests } = presence;
  
  const otherViewers = viewers.filter(v => v !== currentUser && v !== editor);
  
  return (
    <div className="flex items-center gap-3 text-sm">
      {/* Viewers */}
      {otherViewers.length > 0 && (
        <div className="flex items-center gap-1 text-gray-400">
          <Eye className="w-4 h-4" />
          <span className="text-xs">
            {otherViewers.length === 1 
              ? otherViewers[0]
              : `${otherViewers.length} viewing`
            }
          </span>
        </div>
      )}
      
      {/* Editor */}
      {editor && (
        <div className="flex items-center gap-1">
          {editor === currentUser ? (
            <div className="flex items-center gap-1 text-green-400">
              <Edit className="w-4 h-4" />
              <span className="text-xs font-medium">You're editing</span>
            </div>
          ) : (
            <div className="flex items-center gap-1 text-orange-400">
              <Lock className="w-4 h-4" />
              <span className="text-xs">{editor} is editing</span>
              {onRequestEdit && (
                <button
                  onClick={onRequestEdit}
                  className="ml-2 px-2 py-0.5 bg-orange-600 hover:bg-orange-700 rounded text-xs"
                >
                  Request Edit
                </button>
              )}
            </div>
          )}
        </div>
      )}
      
      {/* Pending Requests */}
      {pending_requests > 0 && editor === currentUser && (
        <div className="flex items-center gap-1 text-blue-400">
          <Users className="w-4 h-4" />
          <span className="text-xs">{pending_requests} waiting</span>
        </div>
      )}
      
      {/* Can Edit */}
      {!is_locked && !editor && onRequestEdit && (
        <button
          onClick={onRequestEdit}
          className="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs flex items-center gap-1"
        >
          <Edit className="w-3 h-3" />
          Start Editing
        </button>
      )}
    </div>
  );
}

interface ActiveUsersProps {
  users: Array<{
    user_name: string;
    current_view?: string;
    current_file?: string;
    current_table?: string;
  }>;
}

export function ActiveUsers({ users }: ActiveUsersProps) {
  if (users.length === 0) {
    return null;
  }
  
  return (
    <div className="flex items-center gap-2">
      <Users className="w-4 h-4 text-gray-400" />
      <div className="flex -space-x-2">
        {users.slice(0, 5).map((user, idx) => (
          <div
            key={idx}
            className="
              w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500
              flex items-center justify-center text-xs font-bold text-white
              border-2 border-gray-900
            "
            title={user.user_name}
          >
            {user.user_name.substring(0, 2).toUpperCase()}
          </div>
        ))}
        {users.length > 5 && (
          <div className="
            w-8 h-8 rounded-full bg-gray-700
            flex items-center justify-center text-xs text-gray-300
            border-2 border-gray-900
          ">
            +{users.length - 5}
          </div>
        )}
      </div>
    </div>
  );
}
