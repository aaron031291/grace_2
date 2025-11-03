<script>
  import { onMount } from 'svelte';
  
  let sessions = [];
  let members = [];
  let stats = null;
  let activeTab = 'sessions';
  let selectedSession = null;
  let loading = true;
  
  const API_BASE = 'http://localhost:8000';
  
  async function fetchSessions() {
    try {
      const response = await fetch(`${API_BASE}/api/parliament/sessions`, {
        credentials: 'include'
      });
      const data = await response.json();
      if (data.success) {
        sessions = data.sessions;
      }
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
    }
  }
  
  async function fetchMembers() {
    try {
      const response = await fetch(`${API_BASE}/api/parliament/members`, {
        credentials: 'include'
      });
      const data = await response.json();
      if (data.success) {
        members = data.members;
      }
    } catch (error) {
      console.error('Failed to fetch members:', error);
    }
  }
  
  async function fetchStats() {
    try {
      const response = await fetch(`${API_BASE}/api/parliament/stats`, {
        credentials: 'include'
      });
      const data = await response.json();
      if (data.success) {
        stats = data.stats;
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  }
  
  async function viewSession(sessionId) {
    try {
      const response = await fetch(`${API_BASE}/api/parliament/sessions/${sessionId}`, {
        credentials: 'include'
      });
      const data = await response.json();
      if (data.success) {
        selectedSession = data.session;
      }
    } catch (error) {
      console.error('Failed to fetch session:', error);
    }
  }
  
  async function castVote(sessionId, vote, reason = '') {
    try {
      const response = await fetch(`${API_BASE}/api/parliament/sessions/${sessionId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ vote, reason, automated: false })
      });
      
      const data = await response.json();
      if (data.success) {
        alert(`Vote cast: ${vote}`);
        await viewSession(sessionId);
        await fetchSessions();
      } else {
        alert(`Vote failed: ${data.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Failed to cast vote:', error);
      alert('Failed to cast vote');
    }
  }
  
  onMount(async () => {
    await Promise.all([fetchSessions(), fetchMembers(), fetchStats()]);
    loading = false;
    
    // Refresh every 30 seconds
    setInterval(() => {
      if (activeTab === 'sessions') fetchSessions();
      if (activeTab === 'members') fetchMembers();
    }, 30000);
  });
  
  function getStatusColor(status) {
    const colors = {
      'approved': 'green',
      'rejected': 'red',
      'voting': 'yellow',
      'pending': 'blue',
      'expired': 'gray'
    };
    return colors[status] || 'gray';
  }
</script>

<div class="parliament-dashboard">
  <h1>🏛️ Parliament Governance</h1>
  
  {#if stats}
    <div class="stats-summary">
      <div class="stat-card">
        <h3>{stats.total_sessions}</h3>
        <p>Total Sessions</p>
      </div>
      <div class="stat-card">
        <h3>{stats.sessions_pending}</h3>
        <p>Pending</p>
      </div>
      <div class="stat-card success">
        <h3>{stats.sessions_approved}</h3>
        <p>Approved</p>
      </div>
      <div class="stat-card error">
        <h3>{stats.sessions_rejected}</h3>
        <p>Rejected</p>
      </div>
      <div class="stat-card">
        <h3>{(stats.approval_rate * 100).toFixed(1)}%</h3>
        <p>Approval Rate</p>
      </div>
    </div>
  {/if}
  
  <div class="tabs">
    <button class:active={activeTab === 'sessions'} on:click={() => activeTab = 'sessions'}>
      Sessions
    </button>
    <button class:active={activeTab === 'members'} on:click={() => activeTab = 'members'}>
      Members
    </button>
  </div>
  
  {#if loading}
    <p>Loading...</p>
  {:else if activeTab === 'sessions'}
    <div class="sessions-list">
      <h2>Voting Sessions</h2>
      
      {#if sessions.length === 0}
        <p class="empty">No sessions found</p>
      {:else}
        <table>
          <thead>
            <tr>
              <th>Policy</th>
              <th>Action</th>
              <th>Committee</th>
              <th>Votes</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each sessions as session}
              <tr>
                <td>{session.policy_name}</td>
                <td>{session.action_type}</td>
                <td>{session.committee}</td>
                <td>{session.votes}</td>
                <td>
                  <span class="status {getStatusColor(session.status)}">
                    {session.status}
                  </span>
                </td>
                <td>
                  <button on:click={() => viewSession(session.session_id)} class="btn-small">
                    View
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    </div>
    
    {#if selectedSession}
      <div class="session-details modal">
        <div class="modal-content">
          <button class="close-btn" on:click={() => selectedSession = null}>×</button>
          
          <h2>Session Details</h2>
          
          <div class="detail-grid">
            <div><strong>Policy:</strong> {selectedSession.policy_name}</div>
            <div><strong>Action:</strong> {selectedSession.action_type}</div>
            <div><strong>Category:</strong> {selectedSession.category || 'N/A'}</div>
            <div><strong>Committee:</strong> {selectedSession.committee}</div>
            <div><strong>Risk Level:</strong> {selectedSession.risk_level}</div>
            <div><strong>Status:</strong> 
              <span class="status {getStatusColor(selectedSession.status)}">
                {selectedSession.status}
              </span>
            </div>
            <div><strong>Quorum:</strong> {selectedSession.total_votes}/{selectedSession.quorum_required}</div>
            <div><strong>Threshold:</strong> {(selectedSession.approval_threshold * 100).toFixed(0)}%</div>
          </div>
          
          <div class="vote-tally">
            <h3>Vote Tally</h3>
            <div class="tally-grid">
              <div class="tally-item success">
                ✓ Approve: {selectedSession.votes_approve}
              </div>
              <div class="tally-item error">
                ✗ Reject: {selectedSession.votes_reject}
              </div>
              <div class="tally-item warn">
                ○ Abstain: {selectedSession.votes_abstain}
              </div>
            </div>
          </div>
          
          {#if selectedSession.status === 'voting' || selectedSession.status === 'pending'}
            <div class="voting-actions">
              <h3>Cast Your Vote</h3>
              <div class="vote-buttons">
                <button class="vote-btn approve" on:click={() => {
                  const reason = prompt('Reason for approval (optional):');
                  castVote(selectedSession.session_id, 'approve', reason || '');
                }}>
                  ✓ Approve
                </button>
                <button class="vote-btn reject" on:click={() => {
                  const reason = prompt('Reason for rejection (optional):');
                  castVote(selectedSession.session_id, 'reject', reason || '');
                }}>
                  ✗ Reject
                </button>
                <button class="vote-btn abstain" on:click={() => {
                  castVote(selectedSession.session_id, 'abstain');
                }}>
                  ○ Abstain
                </button>
              </div>
            </div>
          {/if}
          
          {#if selectedSession.votes && selectedSession.votes.length > 0}
            <div class="votes-list">
              <h3>Individual Votes</h3>
              <table>
                <thead>
                  <tr>
                    <th>Member</th>
                    <th>Vote</th>
                    <th>Automated</th>
                    <th>Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {#each selectedSession.votes as vote}
                    <tr>
                      <td>{vote.display_name}</td>
                      <td>
                        <span class="vote-choice {vote.vote}">
                          {vote.vote}
                        </span>
                      </td>
                      <td>{vote.automated ? '🤖' : '👤'}</td>
                      <td class="reason">{vote.reason || '-'}</td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          {/if}
        </div>
      </div>
    {/if}
    
  {:else if activeTab === 'members'}
    <div class="members-list">
      <h2>Parliament Members</h2>
      
      {#if members.length === 0}
        <p class="empty">No members found</p>
      {:else}
        <table>
          <thead>
            <tr>
              <th>Member</th>
              <th>Type</th>
              <th>Role</th>
              <th>Committees</th>
              <th>Weight</th>
              <th>Total Votes</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {#each members as member}
              <tr>
                <td><strong>{member.display_name}</strong><br/><small>{member.member_id}</small></td>
                <td>{member.type}</td>
                <td>{member.role}</td>
                <td>{member.committees.join(', ')}</td>
                <td>{member.vote_weight}</td>
                <td>{member.total_votes}</td>
                <td>
                  {#if member.active && !member.suspended}
                    <span class="status green">✓ Active</span>
                  {:else}
                    <span class="status red">✗ Inactive</span>
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    </div>
  {/if}
</div>

<style>
  .parliament-dashboard {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
  }
  
  h1 {
    color: #333;
    margin-bottom: 20px;
  }
  
  .stats-summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
    margin-bottom: 30px;
  }
  
  .stat-card {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
  }
  
  .stat-card h3 {
    font-size: 32px;
    margin: 0 0 10px 0;
    color: #333;
  }
  
  .stat-card p {
    margin: 0;
    color: #666;
    font-size: 14px;
  }
  
  .stat-card.success h3 { color: #28a745; }
  .stat-card.error h3 { color: #dc3545; }
  
  .tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    border-bottom: 2px solid #ddd;
  }
  
  .tabs button {
    padding: 10px 20px;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 16px;
    color: #666;
    border-bottom: 3px solid transparent;
  }
  
  .tabs button.active {
    color: #007bff;
    border-bottom-color: #007bff;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
    background: white;
  }
  
  th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }
  
  th {
    background: #f8f9fa;
    font-weight: 600;
  }
  
  .status {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
  }
  
  .status.green { background: #d4edda; color: #155724; }
  .status.red { background: #f8d7da; color: #721c24; }
  .status.yellow { background: #fff3cd; color: #856404; }
  .status.blue { background: #d1ecf1; color: #0c5460; }
  .status.gray { background: #e2e3e5; color: #383d41; }
  
  .btn-small {
    padding: 6px 12px;
    font-size: 14px;
    border: 1px solid #007bff;
    background: white;
    color: #007bff;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .btn-small:hover {
    background: #007bff;
    color: white;
  }
  
  .modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .modal-content {
    background: white;
    padding: 30px;
    border-radius: 8px;
    max-width: 800px;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
  }
  
  .close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    font-size: 30px;
    border: none;
    background: none;
    cursor: pointer;
    color: #999;
  }
  
  .detail-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    margin: 20px 0;
  }
  
  .vote-tally {
    margin: 20px 0;
  }
  
  .tally-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
  }
  
  .tally-item {
    padding: 15px;
    border-radius: 4px;
    text-align: center;
    font-weight: 600;
  }
  
  .tally-item.success { background: #d4edda; color: #155724; }
  .tally-item.error { background: #f8d7da; color: #721c24; }
  .tally-item.warn { background: #fff3cd; color: #856404; }
  
  .vote-buttons {
    display: flex;
    gap: 10px;
    margin-top: 10px;
  }
  
  .vote-btn {
    flex: 1;
    padding: 12px;
    font-size: 16px;
    font-weight: 600;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .vote-btn.approve {
    background: #28a745;
    color: white;
  }
  
  .vote-btn.reject {
    background: #dc3545;
    color: white;
  }
  
  .vote-btn.abstain {
    background: #ffc107;
    color: #333;
  }
  
  .vote-choice.approve { color: #28a745; font-weight: 600; }
  .vote-choice.reject { color: #dc3545; font-weight: 600; }
  .vote-choice.abstain { color: #ffc107; font-weight: 600; }
  
  .reason {
    font-size: 12px;
    color: #666;
    max-width: 300px;
  }
  
  .empty {
    text-align: center;
    padding: 40px;
    color: #999;
  }
</style>
