/**
 * Keyboard Shortcuts for Grace
 * Ctrl+T: Switch to Chat
 * Ctrl+`: Toggle Terminal
 * Ctrl+K: Focus search
 * Ctrl+N: New chat
 */

import { useEffect } from 'react';

interface ShortcutHandlers {
  onChat?: () => void;
  onTerminal?: () => void;
  onSearch?: () => void;
  onNewChat?: () => void;
  onFiles?: () => void;
  onKnowledge?: () => void;
}

export function useKeyboardShortcuts(handlers: ShortcutHandlers) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+T: Switch to Chat
      if (e.ctrlKey && e.key === 't') {
        e.preventDefault();
        handlers.onChat?.();
      }
      
      // Ctrl+`: Toggle Terminal
      if (e.ctrlKey && e.key === '`') {
        e.preventDefault();
        handlers.onTerminal?.();
      }
      
      // Ctrl+K: Focus search
      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        handlers.onSearch?.();
      }
      
      // Ctrl+N: New chat
      if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        handlers.onNewChat?.();
      }
      
      // Ctrl+F: Files
      if (e.ctrlKey && e.key === 'f' && e.shiftKey) {
        e.preventDefault();
        handlers.onFiles?.();
      }
      
      // Ctrl+Shift+K: Knowledge
      if (e.ctrlKey && e.key === 'k' && e.shiftKey) {
        e.preventDefault();
        handlers.onKnowledge?.();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handlers]);
}
