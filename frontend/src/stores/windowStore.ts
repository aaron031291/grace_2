import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface WindowConfig {
  id: string;
  type: 'builder' | 'health' | 'memory';
  title: string;
  x: number;
  y: number;
  width: number;
  height: number;
  minimized: boolean;
  maximized: boolean;
  zIndex: number;
  data?: any;
}

interface WindowStore {
  windows: WindowConfig[];
  activeWindowId: string | null;
  nextZIndex: number;

  // Actions
  spawnWindow: (config: Omit<WindowConfig, 'id' | 'zIndex'>) => void;
  closeWindow: (id: string) => void;
  updateWindow: (id: string, updates: Partial<WindowConfig>) => void;
  setActiveWindow: (id: string | null) => void;
  minimizeWindow: (id: string) => void;
  maximizeWindow: (id: string) => void;
  restoreWindow: (id: string) => void;
  bringToFront: (id: string) => void;
}

export const useWindowStore = create<WindowStore>()(
  persist(
    (set, get) => ({
      windows: [],
      activeWindowId: null,
      nextZIndex: 1,

      spawnWindow: (config) => {
        const { windows, nextZIndex } = get();
        const newWindow: WindowConfig = {
          ...config,
          id: `window-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          zIndex: nextZIndex,
          minimized: false,
          maximized: false,
        };

        set({
          windows: [...windows, newWindow],
          activeWindowId: newWindow.id,
          nextZIndex: nextZIndex + 1,
        });
      },

      closeWindow: (id) => {
        const { windows, activeWindowId } = get();
        const filteredWindows = windows.filter(w => w.id !== id);
        const newActiveId = activeWindowId === id
          ? (filteredWindows.length > 0 ? filteredWindows[filteredWindows.length - 1].id : null)
          : activeWindowId;

        set({
          windows: filteredWindows,
          activeWindowId: newActiveId,
        });
      },

      updateWindow: (id, updates) => {
        const { windows } = get();
        set({
          windows: windows.map(w =>
            w.id === id ? { ...w, ...updates } : w
          ),
        });
      },

      setActiveWindow: (id) => {
        const { windows, nextZIndex } = get();
        if (id) {
          set({
            activeWindowId: id,
            windows: windows.map(w =>
              w.id === id ? { ...w, zIndex: nextZIndex } : w
            ),
            nextZIndex: nextZIndex + 1,
          });
        } else {
          set({ activeWindowId: id });
        }
      },

      minimizeWindow: (id) => {
        get().updateWindow(id, { minimized: true });
      },

      maximizeWindow: (id) => {
        get().updateWindow(id, { maximized: true, minimized: false });
      },

      restoreWindow: (id) => {
        get().updateWindow(id, { maximized: false, minimized: false });
      },

      bringToFront: (id) => {
        get().setActiveWindow(id);
      },
    }),
    {
      name: 'grace-windows',
      partialize: (state) => ({
        windows: state.windows.map(w => ({
          ...w,
          minimized: false, // Don't persist minimized state
          maximized: false, // Don't persist maximized state
        })),
      }),
    }
  )
);