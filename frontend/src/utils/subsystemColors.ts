/**
 * Subsystem Color Coding
 * Assign colors to each Grace subsystem/kernel for visual consistency
 */

export interface SubsystemTheme {
  id: string;
  name: string;
  color: string;
  bgColor: string;
  borderColor: string;
  icon: string;
  description: string;
}

export const SUBSYSTEM_THEMES: Record<string, SubsystemTheme> = {
  // Core Systems
  core: {
    id: 'core',
    name: 'Core',
    color: '#64ff96',
    bgColor: 'rgba(100, 255, 150, 0.1)',
    borderColor: 'rgba(100, 255, 150, 0.3)',
    icon: '⚡',
    description: 'Core system operations',
  },
  
  guardian: {
    id: 'guardian',
    name: 'Guardian',
    color: '#ffd700',
    bgColor: 'rgba(255, 215, 0, 0.1)',
    borderColor: 'rgba(255, 215, 0, 0.3)',
    icon: '🛡️',
    description: 'System protection and validation',
  },

  // Self-Healing
  'self-heal': {
    id: 'self-heal',
    name: 'Self-Heal',
    color: '#00d4ff',
    bgColor: 'rgba(0, 212, 255, 0.1)',
    borderColor: 'rgba(0, 212, 255, 0.3)',
    icon: '💊',
    description: 'Autonomous repair and recovery',
  },

  // Memory Systems
  memory: {
    id: 'memory',
    name: 'Memory',
    color: '#b57aff',
    bgColor: 'rgba(181, 122, 255, 0.1)',
    borderColor: 'rgba(181, 122, 255, 0.3)',
    icon: '🧠',
    description: 'Knowledge storage and retrieval',
  },

  librarian: {
    id: 'librarian',
    name: 'Librarian',
    color: '#9d7aff',
    bgColor: 'rgba(157, 122, 255, 0.1)',
    borderColor: 'rgba(157, 122, 255, 0.3)',
    icon: '📚',
    description: 'Knowledge curation and organization',
  },

  // HTM & Trust
  htm: {
    id: 'htm',
    name: 'HTM',
    color: '#ff9500',
    bgColor: 'rgba(255, 149, 0, 0.1)',
    borderColor: 'rgba(255, 149, 0, 0.3)',
    icon: '🔶',
    description: 'Hierarchical Temporal Memory anomaly detection',
  },

  trust: {
    id: 'trust',
    name: 'Trust',
    color: '#ff7aa3',
    bgColor: 'rgba(255, 122, 163, 0.1)',
    borderColor: 'rgba(255, 122, 163, 0.3)',
    icon: '🤝',
    description: 'Trust framework and verification',
  },

  // Governance
  governance: {
    id: 'governance',
    name: 'Governance',
    color: '#ff6b9d',
    bgColor: 'rgba(255, 107, 157, 0.1)',
    borderColor: 'rgba(255, 107, 157, 0.3)',
    icon: '⚖️',
    description: 'Policy enforcement and approval workflows',
  },

  security: {
    id: 'security',
    name: 'Security',
    color: '#ff4757',
    bgColor: 'rgba(255, 71, 87, 0.1)',
    borderColor: 'rgba(255, 71, 87, 0.3)',
    icon: '🔒',
    description: 'Security controls and access management',
  },

  audit: {
    id: 'audit',
    name: 'Audit',
    color: '#ffa502',
    bgColor: 'rgba(255, 165, 2, 0.1)',
    borderColor: 'rgba(255, 165, 2, 0.3)',
    icon: '📝',
    description: 'Audit logging and compliance',
  },

  // Execution
  execution: {
    id: 'execution',
    name: 'Execution',
    color: '#5fd3f3',
    bgColor: 'rgba(95, 211, 243, 0.1)',
    borderColor: 'rgba(95, 211, 243, 0.3)',
    icon: '⚙️',
    description: 'Task execution and orchestration',
  },

  'mission-control': {
    id: 'mission-control',
    name: 'Mission Control',
    color: '#48dbfb',
    bgColor: 'rgba(72, 219, 251, 0.1)',
    borderColor: 'rgba(72, 219, 251, 0.3)',
    icon: '🎯',
    description: 'Mission planning and coordination',
  },

  // Learning
  learning: {
    id: 'learning',
    name: 'Learning',
    color: '#1dd1a1',
    bgColor: 'rgba(29, 209, 161, 0.1)',
    borderColor: 'rgba(29, 209, 161, 0.3)',
    icon: '📖',
    description: 'Autonomous learning systems',
  },

  research: {
    id: 'research',
    name: 'Research',
    color: '#10ac84',
    bgColor: 'rgba(16, 172, 132, 0.1)',
    borderColor: 'rgba(16, 172, 132, 0.3)',
    icon: '🔬',
    description: 'Research and knowledge acquisition',
  },

  // AI/Models
  ai: {
    id: 'ai',
    name: 'AI',
    color: '#a29bfe',
    bgColor: 'rgba(162, 155, 254, 0.1)',
    borderColor: 'rgba(162, 155, 254, 0.3)',
    icon: '🤖',
    description: 'AI model orchestration',
  },

  models: {
    id: 'models',
    name: 'Models',
    color: '#6c5ce7',
    bgColor: 'rgba(108, 92, 231, 0.1)',
    borderColor: 'rgba(108, 92, 231, 0.3)',
    icon: '🧮',
    description: 'Model management and selection',
  },

  // Communication
  chat: {
    id: 'chat',
    name: 'Chat',
    color: '#74b9ff',
    bgColor: 'rgba(116, 185, 255, 0.1)',
    borderColor: 'rgba(116, 185, 255, 0.3)',
    icon: '💬',
    description: 'Chat interface and interactions',
  },

  voice: {
    id: 'voice',
    name: 'Voice',
    color: '#fd79a8',
    bgColor: 'rgba(253, 121, 168, 0.1)',
    borderColor: 'rgba(253, 121, 168, 0.3)',
    icon: '🔊',
    description: 'Voice input and output',
  },

  // Infrastructure
  infrastructure: {
    id: 'infrastructure',
    name: 'Infrastructure',
    color: '#636e72',
    bgColor: 'rgba(99, 110, 114, 0.1)',
    borderColor: 'rgba(99, 110, 114, 0.3)',
    icon: '🏗️',
    description: 'Infrastructure and services',
  },

  monitoring: {
    id: 'monitoring',
    name: 'Monitoring',
    color: '#00b894',
    bgColor: 'rgba(0, 184, 148, 0.1)',
    borderColor: 'rgba(0, 184, 148, 0.3)',
    icon: '📊',
    description: 'System monitoring and metrics',
  },

  // Default
  unknown: {
    id: 'unknown',
    name: 'Unknown',
    color: '#95afc0',
    bgColor: 'rgba(149, 175, 192, 0.1)',
    borderColor: 'rgba(149, 175, 192, 0.3)',
    icon: '❓',
    description: 'Unknown subsystem',
  },
};

/**
 * Get theme for a subsystem
 */
export function getSubsystemTheme(subsystemId: string): SubsystemTheme {
  return SUBSYSTEM_THEMES[subsystemId] || SUBSYSTEM_THEMES.unknown;
}

/**
 * Get CSS variables for a subsystem
 */
export function getSubsystemCSSVars(subsystemId: string): Record<string, string> {
  const theme = getSubsystemTheme(subsystemId);
  return {
    '--subsystem-color': theme.color,
    '--subsystem-bg': theme.bgColor,
    '--subsystem-border': theme.borderColor,
  };
}

/**
 * Format log entry with subsystem color
 */
export function colorizeLogEntry(entry: { domain?: string; subsystem?: string; message: string }) {
  const subsystem = entry.subsystem || entry.domain || 'unknown';
  const theme = getSubsystemTheme(subsystem);
  return {
    ...entry,
    color: theme.color,
    icon: theme.icon,
    subsystemName: theme.name,
  };
}

/**
 * Get all subsystem themes (for legend/key)
 */
export function getAllSubsystemThemes(): SubsystemTheme[] {
  return Object.values(SUBSYSTEM_THEMES).filter(t => t.id !== 'unknown');
}
