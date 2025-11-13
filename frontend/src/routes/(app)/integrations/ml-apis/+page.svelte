<script lang="ts">
  import { onMount } from 'svelte';
  
  interface MLAPIIntegration {
    name: string;
    category: string;
    url: string;
    auth_type: string;
    risk_level: string;
    risk_score: number;
    status: string;
    hunter_scan_status: string;
    health_status: string;
    approved_by: string;
    capabilities: string[];
    use_cases: string[];
  }
  
  let integrations: MLAPIIntegration[] = [];
  let loading = true;
  let selectedFilter = 'all';
  
  onMount(async () => {
    await loadIntegrations();
  });
  
  async function loadIntegrations() {
    try {
      const response = await fetch('/api/integrations/ml-apis');
      if (response.ok) {
        integrations = await response.json();
      }
    } catch (err) {
      console.error('Failed to load integrations:', err);
    } finally {
      loading = false;
    }
  }
  
  function getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      'pending_review': 'bg-yellow-100 text-yellow-800',
      'approved': 'bg-green-100 text-green-800',
      'rejected': 'bg-red-100 text-red-800',
      'sandboxed': 'bg-blue-100 text-blue-800',
      'quarantined': 'bg-red-100 text-red-800',
      'active': 'bg-green-100 text-green-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  }
  
  function getRiskColor(risk: string): string {
    const colors: Record<string, string> = {
      'low': 'bg-green-50 text-green-700 border-green-200',
      'medium': 'bg-yellow-50 text-yellow-700 border-yellow-200',
      'high': 'bg-orange-50 text-orange-700 border-orange-200',
      'critical': 'bg-red-50 text-red-700 border-red-200'
    };
    return colors[risk] || 'bg-gray-50 text-gray-700 border-gray-200';
  }
  
  function getHunterIcon(status: string): string {
    return status === 'passed' ? '✓' : status === 'failed' ? '✗' : '○';
  }
  
  $: filteredIntegrations = integrations.filter(i => {
    if (selectedFilter === 'all') return true;
    return i.status === selectedFilter;
  });
</script>

<div class="p-6 max-w-7xl mx-auto">
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-2">ML/AI API Integrations</h1>
    <p class="text-gray-600">
      Discovered APIs with Hunter Bridge security + Verification Charter governance
    </p>
  </div>
  
  <!-- Filters -->
  <div class="mb-6 flex gap-2">
    <button
      class="px-4 py-2 rounded-lg {selectedFilter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}"
      on:click={() => selectedFilter = 'all'}
    >
      All ({integrations.length})
    </button>
    <button
      class="px-4 py-2 rounded-lg {selectedFilter === 'pending_review' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}"
      on:click={() => selectedFilter = 'pending_review'}
    >
      Pending ({integrations.filter(i => i.status === 'pending_review').length})
    </button>
    <button
      class="px-4 py-2 rounded-lg {selectedFilter === 'approved' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}"
      on:click={() => selectedFilter = 'approved'}
    >
      Approved ({integrations.filter(i => i.status === 'approved').length})
    </button>
    <button
      class="px-4 py-2 rounded-lg {selectedFilter === 'quarantined' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}"
      on:click={() => selectedFilter = 'quarantined'}
    >
      Quarantined ({integrations.filter(i => i.status === 'quarantined').length})
    </button>
  </div>
  
  {#if loading}
    <div class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="mt-4 text-gray-600">Loading integrations...</p>
    </div>
  {:else if filteredIntegrations.length === 0}
    <div class="text-center py-12 bg-gray-50 rounded-lg">
      <p class="text-gray-600">No integrations found</p>
    </div>
  {:else}
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {#each filteredIntegrations as integration}
        <div class="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
          <div class="p-6">
            <!-- Header -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 mb-1">
                  {integration.name}
                </h3>
                <p class="text-sm text-gray-500">{integration.category}</p>
              </div>
              <span class="px-2 py-1 text-xs rounded-full {getStatusColor(integration.status)}">
                {integration.status.replace('_', ' ')}
              </span>
            </div>
            
            <!-- URL -->
            <div class="mb-4">
              <a 
                href={integration.url} 
                target="_blank" 
                class="text-sm text-blue-600 hover:underline truncate block"
              >
                {integration.url}
              </a>
            </div>
            
            <!-- Risk & Security -->
            <div class="grid grid-cols-2 gap-3 mb-4">
              <div class="border rounded-lg p-3 {getRiskColor(integration.risk_level)}">
                <div class="text-xs font-medium mb-1">Risk Level</div>
                <div class="text-sm font-semibold uppercase">{integration.risk_level}</div>
                <div class="text-xs mt-1">{(integration.risk_score * 100).toFixed(0)}%</div>
              </div>
              
              <div class="border rounded-lg p-3 bg-gray-50">
                <div class="text-xs font-medium text-gray-700 mb-1">Hunter Scan</div>
                <div class="text-sm font-semibold">
                  <span class="text-lg mr-1">{getHunterIcon(integration.hunter_scan_status)}</span>
                  {integration.hunter_scan_status || 'pending'}
                </div>
              </div>
            </div>
            
            <!-- Auth & Health -->
            <div class="space-y-2 mb-4">
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">Auth:</span>
                <span class="font-medium">{integration.auth_type}</span>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">Health:</span>
                <span class="font-medium {integration.health_status === 'healthy' ? 'text-green-600' : 'text-gray-600'}">
                  {integration.health_status || 'unknown'}
                </span>
              </div>
            </div>
            
            <!-- Capabilities -->
            {#if integration.capabilities && integration.capabilities.length > 0}
              <div class="mb-4">
                <div class="text-xs font-medium text-gray-700 mb-2">Capabilities</div>
                <div class="flex flex-wrap gap-1">
                  {#each integration.capabilities.slice(0, 2) as capability}
                    <span class="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded">
                      {capability}
                    </span>
                  {/each}
                  {#if integration.capabilities.length > 2}
                    <span class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                      +{integration.capabilities.length - 2} more
                    </span>
                  {/if}
                </div>
              </div>
            {/if}
            
            <!-- Actions -->
            <div class="flex gap-2 pt-4 border-t">
              {#if integration.status === 'pending_review'}
                <button class="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  Sandbox Test
                </button>
              {:else if integration.status === 'approved'}
                <button class="flex-1 px-3 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700">
                  Deploy
                </button>
              {:else if integration.status === 'quarantined'}
                <button class="flex-1 px-3 py-2 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700">
                  Review
                </button>
              {/if}
              <button class="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
                Details
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
  
  <!-- Summary Stats -->
  <div class="mt-8 grid grid-cols-4 gap-4">
    <div class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="text-2xl font-bold text-gray-900">{integrations.length}</div>
      <div class="text-sm text-gray-600">Total APIs</div>
    </div>
    <div class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="text-2xl font-bold text-green-600">
        {integrations.filter(i => i.status === 'approved').length}
      </div>
      <div class="text-sm text-gray-600">Approved</div>
    </div>
    <div class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="text-2xl font-bold text-yellow-600">
        {integrations.filter(i => i.status === 'pending_review').length}
      </div>
      <div class="text-sm text-gray-600">Pending</div>
    </div>
    <div class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="text-2xl font-bold text-blue-600">
        {integrations.filter(i => i.hunter_scan_status === 'passed').length}
      </div>
      <div class="text-sm text-gray-600">Hunter Verified</div>
    </div>
  </div>
</div>

<style>
  /* Custom styles if needed */
</style>
