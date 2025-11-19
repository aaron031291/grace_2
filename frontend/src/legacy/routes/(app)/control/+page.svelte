<script lang="ts">
  import { onMount } from 'svelte';
  
  interface SystemState {
    system_state: string;
    pending_tasks: number;
    active_workers: string[];
    can_accept_tasks: boolean;
    co_pilot_active: boolean;
    automation_active: boolean;
  }
  
  let state: SystemState | null = null;
  let loading = true;
  let actionInProgress = false;
  
  onMount(async () => {
    await loadState();
    
    // Refresh state every 2 seconds
    setInterval(loadState, 2000);
    
    // Listen for ESC key for emergency stop
    document.addEventListener('keydown', handleKeyDown);
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  });
  
  async function loadState() {
    try {
      const response = await fetch('/api/control/state');
      if (response.ok) {
        state = await response.json();
      }
    } catch (err) {
      console.error('Failed to load state:', err);
    } finally {
      loading = false;
    }
  }
  
  async function handleKeyDown(e: KeyboardEvent) {
    // Emergency stop on Escape key (with confirmation)
    if (e.key === 'Escape' && !actionInProgress) {
      const confirmed = confirm('EMERGENCY STOP: Are you sure? This will halt all Grace automation immediately.');
      if (confirmed) {
        await emergencyStop();
      }
    }
  }
  
  async function resume() {
    if (actionInProgress) return;
    
    actionInProgress = true;
    
    try {
      const response = await fetch('/api/control/resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'resume', triggered_by: 'user_ui' })
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(result.message);
        await loadState();
      }
    } catch (err) {
      alert('Failed to resume automation');
    } finally {
      actionInProgress = false;
    }
  }
  
  async function pause() {
    if (actionInProgress) return;
    
    actionInProgress = true;
    
    try {
      const response = await fetch('/api/control/pause', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'pause', triggered_by: 'user_ui' })
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(result.message);
        await loadState();
      }
    } catch (err) {
      alert('Failed to pause automation');
    } finally {
      actionInProgress = false;
    }
  }
  
  async function emergencyStop() {
    actionInProgress = true;
    
    try {
      const response = await fetch('/api/control/emergency-stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'emergency_stop', triggered_by: 'user_ui_esc' })
      });
      
      if (response.ok) {
        const result = await response.json();
        alert('🚨 EMERGENCY STOP EXECUTED\n\n' + result.message);
        await loadState();
      }
    } catch (err) {
      alert('Emergency stop failed: ' + err);
    } finally {
      actionInProgress = false;
    }
  }
  
  function getStateColor(stateName: string): string {
    const colors: Record<string, string> = {
      'running': 'bg-green-500',
      'paused': 'bg-yellow-500',
      'stopped': 'bg-gray-500',
      'emergency_stop': 'bg-red-500',
      'shutting_down': 'bg-orange-500'
    };
    return colors[stateName] || 'bg-gray-500';
  }
  
  function getStateText(stateName: string): string {
    return stateName.replace('_', ' ').toUpperCase();
  }
</script>

<div class="p-6 max-w-6xl mx-auto">
  <!-- Header -->
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-2">Grace Control Center</h1>
    <p class="text-gray-600">
      Control Grace's automation. Co-pilot is always available.
    </p>
    <p class="text-sm text-gray-500 mt-2">
      💡 Press <kbd class="px-2 py-1 bg-gray-100 rounded text-xs font-mono">ESC</kbd> for emergency stop
    </p>
  </div>
  
  {#if loading}
    <div class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="mt-4 text-gray-600">Loading system state...</p>
    </div>
  {:else if state}
    <!-- System Status -->
    <div class="bg-white rounded-lg border border-gray-200 shadow-sm p-6 mb-6">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-xl font-semibold text-gray-900 mb-1">System Status</h2>
          <p class="text-sm text-gray-600">Current automation state</p>
        </div>
        <div class="flex items-center gap-3">
          <div class="h-4 w-4 rounded-full {getStateColor(state.system_state)} animate-pulse"></div>
          <span class="text-lg font-bold text-gray-900">
            {getStateText(state.system_state)}
          </span>
        </div>
      </div>
      
      <!-- Status Grid -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-gray-50 rounded-lg p-4">
          <div class="text-sm text-gray-600 mb-1">Co-Pilot</div>
          <div class="text-lg font-semibold {state.co_pilot_active ? 'text-green-600' : 'text-gray-400'}">
            {state.co_pilot_active ? '✓ Active' : '✗ Inactive'}
          </div>
        </div>
        
        <div class="bg-gray-50 rounded-lg p-4">
          <div class="text-sm text-gray-600 mb-1">Automation</div>
          <div class="text-lg font-semibold {state.automation_active ? 'text-green-600' : 'text-gray-400'}">
            {state.automation_active ? '✓ Running' : '○ Paused'}
          </div>
        </div>
        
        <div class="bg-gray-50 rounded-lg p-4">
          <div class="text-sm text-gray-600 mb-1">Pending Tasks</div>
          <div class="text-2xl font-bold text-gray-900">
            {state.pending_tasks}
          </div>
        </div>
        
        <div class="bg-gray-50 rounded-lg p-4">
          <div class="text-sm text-gray-600 mb-1">Active Workers</div>
          <div class="text-2xl font-bold text-gray-900">
            {state.active_workers.length}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Control Buttons -->
    <div class="bg-white rounded-lg border border-gray-200 shadow-sm p-6 mb-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Controls</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Resume -->
        <button
          on:click={resume}
          disabled={state.system_state === 'running' || actionInProgress}
          class="px-6 py-4 rounded-lg font-semibold transition-colors
                 {state.system_state === 'running' || actionInProgress
                   ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                   : 'bg-green-600 text-white hover:bg-green-700'}"
        >
          <div class="text-2xl mb-1">▶️</div>
          <div>Resume</div>
          <div class="text-xs opacity-75 mt-1">Start automation</div>
        </button>
        
        <!-- Pause -->
        <button
          on:click={pause}
          disabled={state.system_state !== 'running' || actionInProgress}
          class="px-6 py-4 rounded-lg font-semibold transition-colors
                 {state.system_state !== 'running' || actionInProgress
                   ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                   : 'bg-yellow-600 text-white hover:bg-yellow-700'}"
        >
          <div class="text-2xl mb-1">⏸️</div>
          <div>Pause</div>
          <div class="text-xs opacity-75 mt-1">Queue new tasks</div>
        </button>
        
        <!-- Emergency Stop -->
        <button
          on:click={emergencyStop}
          disabled={actionInProgress}
          class="px-6 py-4 rounded-lg font-semibold transition-colors
                 {actionInProgress
                   ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                   : 'bg-red-600 text-white hover:bg-red-700'}"
        >
          <div class="text-2xl mb-1">🚨</div>
          <div>Emergency Stop</div>
          <div class="text-xs opacity-75 mt-1">Halt everything</div>
        </button>
      </div>
      
      <div class="mt-4 p-4 bg-blue-50 rounded-lg">
        <p class="text-sm text-blue-900">
          <strong>Note:</strong> Co-pilot remains available in all states. 
          Pausing only stops automation workers. You can still query Grace.
        </p>
      </div>
    </div>
    
    <!-- Active Workers -->
    {#if state.active_workers.length > 0}
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm p-6 mb-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Active Workers</h2>
        
        <div class="space-y-2">
          {#each state.active_workers as worker}
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div class="flex items-center gap-3">
                <div class="h-2 w-2 rounded-full bg-green-500"></div>
                <span class="font-medium text-gray-900">{worker}</span>
              </div>
              <span class="text-sm text-gray-600">Running</span>
            </div>
          {/each}
        </div>
      </div>
    {/if}
    
    <!-- Pending Tasks -->
    {#if state.pending_tasks > 0}
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Task Queue</h2>
        
        <div class="flex items-center justify-between p-4 bg-yellow-50 rounded-lg border border-yellow-200">
          <div>
            <div class="font-semibold text-yellow-900">{state.pending_tasks} tasks queued</div>
            <div class="text-sm text-yellow-700 mt-1">
              {#if state.system_state === 'paused'}
                Tasks will execute when automation is resumed
              {:else if state.system_state === 'running'}
                Tasks are being processed
              {:else}
                Tasks waiting (system {state.system_state})
              {/if}
            </div>
          </div>
          <button
            on:click={() => window.location.href = '/api/control/queue'}
            class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 text-sm"
          >
            View Queue
          </button>
        </div>
      </div>
    {/if}
  {/if}
</div>

<style>
  kbd {
    box-shadow: 0 1px 3px rgba(0,0,0,0.12);
  }
</style>
