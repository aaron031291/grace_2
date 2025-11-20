import { create } from 'zustand';
import type { Project, ChatThread, ChatKind, ChatMessage } from '../types/chat';
import { instructionPresets } from '../config/instructions';

interface ChatStore {
  projects: Project[];
  activeProjectId: string | null;
  activeThreadId: string | null;

  // Actions
  createProject: (name: string, description?: string, instructions?: string) => string;
  deleteProject: (projectId: string) => void;
  setActiveProject: (projectId: string | null) => void;

  createThread: (projectId: string, kind: ChatKind, title?: string) => string;
  deleteThread: (projectId: string, threadId: string) => void;
  setActiveThread: (threadId: string | null) => void;

  addMessage: (projectId: string, threadId: string, message: Omit<ChatMessage, 'id' | 'createdAt'>) => void;
  updateThreadInstructions: (projectId: string, threadId: string, instructions: string) => void;
  updateProjectInstructions: (projectId: string, instructions: string) => void;

  // Selectors
  getActiveProject: () => Project | null;
  getActiveThread: () => ChatThread | null;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  projects: [],
  activeProjectId: null,
  activeThreadId: null,

  createProject: (name, description = '', instructions = '') => {
    const projectId = `project-${Date.now()}-${Math.random().toString(36).substring(7)}`;
    const newProject: Project = {
      id: projectId,
      name,
      description,
      instructions,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      threads: [],
    };

    set((state) => ({
      projects: [...state.projects, newProject],
      activeProjectId: projectId,
    }));

    return projectId;
  },

  deleteProject: (projectId) => {
    set((state) => ({
      projects: state.projects.filter((p) => p.id !== projectId),
      activeProjectId: state.activeProjectId === projectId ? null : state.activeProjectId,
    }));
  },

  setActiveProject: (projectId) => {
    set({ activeProjectId: projectId });
  },

  createThread: (projectId, kind, title) => {
    const threadId = `thread-${Date.now()}-${Math.random().toString(36).substring(7)}`;
    const defaultTitle = title || `${kind} chat`;

    const newThread: ChatThread = {
      id: threadId,
      kind,
      title: defaultTitle,
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      instructions: instructionPresets[kind],
    };

    set((state) => ({
      projects: state.projects.map((p) =>
        p.id === projectId
          ? {
              ...p,
              threads: [...p.threads, newThread],
              updatedAt: new Date().toISOString(),
            }
          : p
      ),
      activeThreadId: threadId,
    }));

    return threadId;
  },

  deleteThread: (projectId, threadId) => {
    set((state) => ({
      projects: state.projects.map((p) =>
        p.id === projectId
          ? {
              ...p,
              threads: p.threads.filter((t) => t.id !== threadId),
              updatedAt: new Date().toISOString(),
            }
          : p
      ),
      activeThreadId: state.activeThreadId === threadId ? null : state.activeThreadId,
    }));
  },

  setActiveThread: (threadId) => {
    set({ activeThreadId: threadId });
  },

  addMessage: (projectId, threadId, message) => {
    const messageId = `msg-${Date.now()}-${Math.random().toString(36).substring(7)}`;
    const newMessage: ChatMessage = {
      ...message,
      id: messageId,
      createdAt: new Date().toISOString(),
    };

    set((state) => ({
      projects: state.projects.map((p) =>
        p.id === projectId
          ? {
              ...p,
              threads: p.threads.map((t) =>
                t.id === threadId
                  ? {
                      ...t,
                      messages: [...t.messages, newMessage],
                      updatedAt: new Date().toISOString(),
                    }
                  : t
              ),
              updatedAt: new Date().toISOString(),
            }
          : p
      ),
    }));
  },

  updateThreadInstructions: (projectId, threadId, instructions) => {
    set((state) => ({
      projects: state.projects.map((p) =>
        p.id === projectId
          ? {
              ...p,
              threads: p.threads.map((t) =>
                t.id === threadId
                  ? {
                      ...t,
                      instructions,
                      updatedAt: new Date().toISOString(),
                    }
                  : t
              ),
              updatedAt: new Date().toISOString(),
            }
          : p
      ),
    }));
  },

  updateProjectInstructions: (projectId, instructions) => {
    set((state) => ({
      projects: state.projects.map((p) =>
        p.id === projectId
          ? {
              ...p,
              instructions,
              updatedAt: new Date().toISOString(),
            }
          : p
      ),
    }));
  },

  getActiveProject: () => {
    const { projects, activeProjectId } = get();
    return projects.find((p) => p.id === activeProjectId) || null;
  },

  getActiveThread: () => {
    const { projects, activeProjectId, activeThreadId } = get();
    const project = projects.find((p) => p.id === activeProjectId);
    if (!project) return null;
    return project.threads.find((t) => t.id === activeThreadId) || null;
  },
}));
