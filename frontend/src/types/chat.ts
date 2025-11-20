export type ChatKind =
  | "build"
  | "research"
  | "governance"
  | "ops"
  | "sandbox"
  | "guardian"
  | "selfHealing"
  | "coding"
  | "general";

export type ChatMessageRole = "user" | "assistant" | "system";

export interface ChatMessage {
  id: string;
  role: ChatMessageRole;
  content: string;
  createdAt: string; // ISO-8601 timestamp
}

/**
 * A conversation thread within a project.  Each thread has its own instruction string
 * which tailors the behaviour of the assistant for that chat.  The `kind` field
 * should match one of the values in `ChatKind` so that preset instructions can
 * be applied by default.
 */
export interface ChatThread {
  id: string;
  kind: ChatKind;
  title: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
  instructions: string;
}

/**
 * A project groups multiple chat threads and can carry its own instruction string
 * so that all conversations within the project share a common context (e.g. the
 * purpose of the project, the domain, key constraints, etc.).
 */
export interface Project {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  instructions: string;
  threads: ChatThread[];
}

/**
 * UIState keeps track of which project and thread are currently active.  This
 * state would normally live in a Zustand or Redux store.
 */
export interface UIState {
  activeProjectId: string | null;
  activeThreadId: string | null;
}

/**
 * ModelInstructions groups the layers of instruction used to build a model
 * prompt.  These correspond to global (system), project and thread level
 * instructions as discussed in the Grace UI design.
 */
export interface ModelInstructions {
  global: string;
  project: string;
  thread: string;
}
