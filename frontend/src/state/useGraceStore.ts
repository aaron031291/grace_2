import { create } from 'zustand';

interface RemoteState {
  isActive: boolean;
  sessionId: string | null;
  loading: boolean;
  status: string;
  requiresApproval: boolean;
}

interface ScreenShareState {
  isActive: boolean;
  sessionId: string | null;
  loading: boolean;
  status: string;
  mode: 'learn' | 'observe_only' | 'consent_required';
}

interface OverlayState {
  cockpitOpen: boolean;
  tasksOpen: boolean;
  historyOpen: boolean;
  fileExplorerOpen: boolean;
  missionControlOpen: boolean;
  mentorOpen: boolean;
}

interface GraceStore {
  // Remote access
  remote: RemoteState;
  setRemoteActive: (active: boolean) => void;
  setRemoteSessionId: (id: string | null) => void;
  setRemoteLoading: (loading: boolean) => void;
  setRemoteStatus: (status: string) => void;
  setRemoteRequiresApproval: (requires: boolean) => void;

  // Screen share
  screenShare: ScreenShareState;
  setScreenShareActive: (active: boolean) => void;
  setScreenShareSessionId: (id: string | null) => void;
  setScreenShareLoading: (loading: boolean) => void;
  setScreenShareStatus: (status: string) => void;
  setScreenShareMode: (mode: 'learn' | 'observe_only' | 'consent_required') => void;

  // Overlays
  overlays: OverlayState;
  toggleOverlay: (key: keyof OverlayState) => void;
  closeAllOverlays: () => void;

  // General
  error: string | null;
  setError: (error: string | null) => void;
}

export const useGraceStore = create<GraceStore>((set) => ({
  // Remote state
  remote: {
    isActive: false,
    sessionId: null,
    loading: false,
    status: '',
    requiresApproval: false,
  },
  setRemoteActive: (active) => set((state) => ({ 
    remote: { ...state.remote, isActive: active } 
  })),
  setRemoteSessionId: (id) => set((state) => ({ 
    remote: { ...state.remote, sessionId: id } 
  })),
  setRemoteLoading: (loading) => set((state) => ({ 
    remote: { ...state.remote, loading } 
  })),
  setRemoteStatus: (status) => set((state) => ({ 
    remote: { ...state.remote, status } 
  })),
  setRemoteRequiresApproval: (requiresApproval) => set((state) => ({ 
    remote: { ...state.remote, requiresApproval } 
  })),

  // Screen share state
  screenShare: {
    isActive: false,
    sessionId: null,
    loading: false,
    status: '',
    mode: 'learn',
  },
  setScreenShareActive: (active) => set((state) => ({ 
    screenShare: { ...state.screenShare, isActive: active } 
  })),
  setScreenShareSessionId: (id) => set((state) => ({ 
    screenShare: { ...state.screenShare, sessionId: id } 
  })),
  setScreenShareLoading: (loading) => set((state) => ({ 
    screenShare: { ...state.screenShare, loading } 
  })),
  setScreenShareStatus: (status) => set((state) => ({ 
    screenShare: { ...state.screenShare, status } 
  })),
  setScreenShareMode: (mode) => set((state) => ({ 
    screenShare: { ...state.screenShare, mode } 
  })),

  // Overlay state
  overlays: {
    cockpitOpen: false,
    tasksOpen: false,
    historyOpen: false,
    fileExplorerOpen: false,
    missionControlOpen: false,
    mentorOpen: false,
  },
  toggleOverlay: (key) => set((state) => ({
    overlays: { ...state.overlays, [key]: !state.overlays[key] }
  })),
  closeAllOverlays: () => set({
    overlays: {
      cockpitOpen: false,
      tasksOpen: false,
      historyOpen: false,
      fileExplorerOpen: false,
      missionControlOpen: false,
      mentorOpen: false,
    }
  }),

  // General
  error: null,
  setError: (error) => set({ error }),
}));
