import type { ModelInstructions, Project, ChatThread } from "../types/chat";
import { systemInstructions } from "../config/instructions";

/**
 * Builds a complete set of model instructions by combining global (system),
 * project and thread level instructions.  This layered approach allows
 * context to be progressively refined from general to specific.
 *
 * @param project - The active project (if any)
 * @param thread - The active chat thread
 * @returns A ModelInstructions object with all layers populated
 */
export function buildModelInstructions(
  project: Project | null,
  thread: ChatThread
): ModelInstructions {
  return {
    global: systemInstructions.global,
    project: project?.instructions || "",
    thread: thread.instructions,
  };
}

/**
 * Assembles a complete prompt by concatenating all instruction layers.
 * The final prompt includes:
 * 1. Global system instructions
 * 2. Project instructions (if available)
 * 3. Thread-specific instructions
 *
 * @param instructions - The layered instructions object
 * @returns A single string containing the full prompt
 */
export function assemblePrompt(instructions: ModelInstructions): string {
  const parts: string[] = [];

  if (instructions.global) {
    parts.push("=== SYSTEM INSTRUCTIONS ===");
    parts.push(instructions.global.trim());
    parts.push("");
  }

  if (instructions.project) {
    parts.push("=== PROJECT CONTEXT ===");
    parts.push(instructions.project.trim());
    parts.push("");
  }

  if (instructions.thread) {
    parts.push("=== THREAD INSTRUCTIONS ===");
    parts.push(instructions.thread.trim());
    parts.push("");
  }

  return parts.join("\n");
}

/**
 * Helper function to get the complete prompt for a given thread.
 *
 * @param project - The active project (if any)
 * @param thread - The active chat thread
 * @returns The fully assembled prompt string
 */
export function getThreadPrompt(
  project: Project | null,
  thread: ChatThread
): string {
  const instructions = buildModelInstructions(project, thread);
  return assemblePrompt(instructions);
}
