<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  
  interface ActivityEvent {
    timestamp: string;
    type: string;
    description: string;
    details: Record<string, any>;
  }
  
  let events: ActivityEvent[] = [];
  let currentActivity: ActivityEvent | null = null;
  let connected = false;
  let ws: WebSocket | null = null;
  let autoScroll = true;
  
  onMount(() => {
    connectWebSocket();
  });
  
  onDestroy(() => {
    if (ws) {
      ws.close();
    }
  });
  
  function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8000/api/activity/stream`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      connected = true;
      console.log('Connected to activity stream');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'history') {
        events = data.events;
      } else if (data.type === 'current') {
        currentActivity = data.event;
      } else if (data.type === 'event') {
        events = [...events, data.event];
        currentActivity = data.event;
        
        // Auto-scroll to bottom
        if (autoScroll) {
          setTimeout(scrollToBottom, 100);
        }
      }
    };
    
    ws.onclose = () => {
      connected = false;
      console.log('Disconnected from activity stream');
      
      // Reconnect after 2 seconds
      setTimeout(connectWebSocket, 2000);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }
  
  function scrollToBottom() {
    const container = document.getElementById('events-container');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }
  
  function getActivityIcon(type: string): string {
    const icons: Record<string, string> = {
      'thinking': '🧠',
      'pc_command': '💻',
      'browsing': '🌐',
      'sandbox_experiment': '🧪',
      'learning': '📚',
      'proposal': '📝',
      'api_call': '🔌',
      'download': '⬇️',
      'code_generation': '⚡'
    };
    return icons[type] || '•';
  }
  
  function getActivityColor(type: string): string {
    const colors: Record<string, string> = {
      'thinking': 'bg-purple-100 text-purple-800 border-purple-200',
      'pc_command': 'bg-blue-100 text-blue-800 border-blue-200',
      'browsing': 'bg-green-100 text-green-800 border-green-200',
      'sandbox_experiment': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'learning': 'bg-indigo-100 text-indigo-800 border-indigo-200',
      'proposal': 'bg-pink-100 text-pink-800 border-pink-200'
    };
    return colors[type] || 'bg-gray-100 text-gray-800 border-gray-200';
  }
  
  function formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  }
  
  function clearEvents() {
    events = [];
    currentActivity = null;
  }
</script>

<div class="h-screen flex flex-col bg-gray-50">
  <!-- Header -->
  <div class="bg-white border-b border-gray-200 px-6 py-4">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Grace Activity Monitor</h1>
        <p class="text-sm text-gray-600">Real-time view of what Grace is doing</p>
      </div>
      
      <div class="flex items-center gap-4">
        <!-- Connection Status -->
        <div class="flex items-center gap-2">
          <div class="h-3 w-3 rounded-full {connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}"></div>
          <span class="text-sm font-medium {connected ? 'text-green-700' : 'text-red-700'}">
            {connected ? 'Live' : 'Disconnected'}
          </span>
        </div>
        
        <!-- Auto-scroll Toggle -->
        <label class="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" bind:checked={autoScroll} class="rounded" />
          <span class="text-sm text-gray-700">Auto-scroll</span>
        </label>
        
        <!-- Clear Button -->
        <button
          on:click={clearEvents}
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium"
        >
          Clear
        </button>
      </div>
    </div>
  </div>
  
  <!-- Current Activity (Sticky) -->
  {#if currentActivity}
    <div class="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-4">
      <div class="flex items-center gap-3">
        <div class="text-3xl">{getActivityIcon(currentActivity.type)}</div>
        <div class="flex-1">
          <div class="text-sm opacity-75">Currently</div>
          <div class="text-lg font-semibold">{currentActivity.description}</div>
          <div class="text-sm opacity-90 mt-1">
            {formatTime(currentActivity.timestamp)}
          </div>
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Events Stream -->
  <div id="events-container" class="flex-1 overflow-y-auto px-6 py-4 space-y-2">
    {#if events.length === 0}
      <div class="text-center py-12 text-gray-500">
        <div class="text-4xl mb-4">👀</div>
        <p>Waiting for Grace to do something...</p>
        <p class="text-sm mt-2">Activity will appear here in real-time</p>
      </div>
    {:else}
      {#each events as event, i (i)}
        <div class="bg-white rounded-lg border {getActivityColor(event.type)} p-4 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex items-start gap-3">
            <div class="text-2xl flex-shrink-0">{getActivityIcon(event.type)}</div>
            
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between mb-1">
                <span class="text-xs font-medium uppercase tracking-wide opacity-75">
                  {event.type.replace('_', ' ')}
                </span>
                <span class="text-xs text-gray-500">
                  {formatTime(event.timestamp)}
                </span>
              </div>
              
              <div class="text-sm font-semibold text-gray-900 mb-2">
                {event.description}
              </div>
              
              {#if Object.keys(event.details || {}).length > 0}
                <div class="text-xs space-y-1">
                  {#each Object.entries(event.details) as [key, value]}
                    <div class="flex gap-2">
                      <span class="font-medium opacity-75">{key}:</span>
                      <span class="opacity-90 truncate">
                        {typeof value === 'string' && value.length > 80 
                          ? value.substring(0, 80) + '...' 
                          : value}
                      </span>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          </div>
        </div>
      {/each}
    {/if}
  </div>
  
  <!-- Footer Stats -->
  <div class="bg-white border-t border-gray-200 px-6 py-3">
    <div class="flex items-center justify-between text-sm text-gray-600">
      <div>
        Total Events: <span class="font-semibold text-gray-900">{events.length}</span>
      </div>
      <div>
        Last Update: <span class="font-semibold text-gray-900">
          {currentActivity ? formatTime(currentActivity.timestamp) : 'N/A'}
        </span>
      </div>
    </div>
  </div>
</div>

<style>
  /* Smooth animations */
  #events-container {
    scroll-behavior: smooth;
  }
</style>
