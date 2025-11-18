/**
 * Agentic Builder Form
 * Let users describe coding tasks for Grace's autonomous code generation
 */
import React, { useState } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import axios from 'axios';
import './AgenticBuilderForm.css';

interface AgenticBuilderFormProps {
  onBuildCreated: () => void;
}

const API_BASE = apiUrl('';

export const AgenticBuilderForm: React.FC<AgenticBuilderFormProps> = ({ onBuildCreated }) => {
  const [formData, setFormData] = useState({
    project_type: 'feature',
    description: '',
    target_domain: 'full_stack_web',
    constraints: {
      deadline: '',
      environments: ['development'],
      compliance: [] as string[],
      stack: 'react_fastapi'
    },
    artifacts: {
      repository: '',
      datasets: [] as string[],
      docs: [] as string[]
    },
    options: {
      generate_tests: true,
      generate_docs: true,
      include_deployment: true,
      require_review: false
    }
  });

  const [showPreview, setShowPreview] = useState(false);
  const [planPreview, setPlanPreview] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!formData.description.trim()) {
      alert('Please provide a description');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/coding_agent/create`, formData);
      setPlanPreview(response.data.plan_preview);
      setShowPreview(true);
    } catch (error) {
      console.error('Failed to create coding intent:', error);
      alert('Failed to create coding intent');
    }
    setLoading(false);
  };

  const handleApprovePlan = async () => {
    if (!planPreview) return;

    try {
      const intentId = coding_intents[coding_intents.length - 1]?.intent_id;
      await axios.post(`${API_BASE}/api/coding_agent/${intentId}/approve`, {
        approved: true,
        modifications: [],
        priority: 'normal'
      });
      
      setShowPreview(false);
      setFormData({
        ...formData,
        description: ''
      });
      onBuildCreated();
      alert('Build started! Track progress in Active Coding Projects table.');
    } catch (error) {
      console.error('Failed to approve plan:', error);
      alert('Failed to start build');
    }
  };

  return (
    <div className="agentic-builder-form">
      <div className="form-header">
        <h3>🤖 Agentic Builder - Autonomous Code Generation</h3>
        <p>Describe what you want Grace to build</p>
      </div>

      <div className="form-body">
        {/* Project Type */}
        <div className="form-section">
          <label>Project Type</label>
          <div className="radio-group">
            {['feature', 'test_suite', 'infrastructure', 'research', 'website', 'blockchain', 'api', 'custom'].map((type) => (
              <label key={type} className="radio-option">
                <input
                  type="radio"
                  name="project_type"
                  value={type}
                  checked={formData.project_type === type}
                  onChange={(e) => setFormData({ ...formData, project_type: e.target.value })}
                />
                {type.replace('_', ' ').toUpperCase()}
              </label>
            ))}
          </div>
        </div>

        {/* Description */}
        <div className="form-section">
          <label>Description</label>
          <textarea
            rows={4}
            placeholder="E.g., Build a real-time chat feature with WebSocket support, user authentication, and message persistence to PostgreSQL. Include React frontend and FastAPI backend with comprehensive tests."
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
        </div>

        {/* Target Domain */}
        <div className="form-section">
          <label>Target Domain</label>
          <select
            value={formData.target_domain}
            onChange={(e) => setFormData({ ...formData, target_domain: e.target.value })}
          >
            <option value="full_stack_web">Full-Stack Web Application</option>
            <option value="infrastructure">Infrastructure / DevOps</option>
            <option value="blockchain">Blockchain / Web3</option>
            <option value="api">API / Backend Service</option>
            <option value="cli">CLI Tool</option>
            <option value="library">Library / Package</option>
            <option value="research">Research / Analysis</option>
            <option value="documentation">Documentation</option>
          </select>
        </div>

        {/* Constraints */}
        <div className="form-section">
          <label>Constraints</label>
          <div className="constraints-grid">
            <div className="constraint-item">
              <label>Deadline (optional)</label>
              <input
                type="date"
                value={formData.constraints.deadline}
                onChange={(e) => setFormData({
                  ...formData,
                  constraints: { ...formData.constraints, deadline: e.target.value }
                })}
              />
            </div>
            <div className="constraint-item">
              <label>Stack</label>
              <select
                value={formData.constraints.stack}
                onChange={(e) => setFormData({
                  ...formData,
                  constraints: { ...formData.constraints, stack: e.target.value }
                })}
              >
                <option value="react_fastapi">React + FastAPI</option>
                <option value="vue_django">Vue + Django</option>
                <option value="nextjs">Next.js Full-Stack</option>
                <option value="terraform_aws">Terraform + AWS</option>
                <option value="solidity_ethers">Solidity + Ethers.js</option>
                <option value="custom">Custom (describe in description)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Artifacts */}
        <div className="form-section">
          <label>Artifacts (Optional)</label>
          <input
            type="text"
            placeholder="Repository URL (e.g., https://github.com/user/project)"
            value={formData.artifacts.repository}
            onChange={(e) => setFormData({
              ...formData,
              artifacts: { ...formData.artifacts, repository: e.target.value }
            })}
          />
        </div>

        {/* Options */}
        <div className="form-section">
          <label>Advanced Options</label>
          <div className="checkbox-group">
            <label className="checkbox-option">
              <input
                type="checkbox"
                checked={formData.options.generate_tests}
                onChange={(e) => setFormData({
                  ...formData,
                  options: { ...formData.options, generate_tests: e.target.checked }
                })}
              />
              Generate tests (unit + integration)
            </label>
            <label className="checkbox-option">
              <input
                type="checkbox"
                checked={formData.options.generate_docs}
                onChange={(e) => setFormData({
                  ...formData,
                  options: { ...formData.options, generate_docs: e.target.checked }
                })}
              />
              Generate documentation
            </label>
            <label className="checkbox-option">
              <input
                type="checkbox"
                checked={formData.options.include_deployment}
                onChange={(e) => setFormData({
                  ...formData,
                  options: { ...formData.options, include_deployment: e.target.checked }
                })}
              />
              Include deployment config
            </label>
            <label className="checkbox-option">
              <input
                type="checkbox"
                checked={formData.options.require_review}
                onChange={(e) => setFormData({
                  ...formData,
                  options: { ...formData.options, require_review: e.target.checked }
                })}
              />
              Request human review before deployment
            </label>
          </div>
        </div>
      </div>

      <div className="form-footer">
        <button className="btn-secondary" onClick={() => setFormData({ ...formData, description: '' })}>
          Clear
        </button>
        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Generating Plan...' : 'Preview Plan'}
        </button>
      </div>

      {/* Plan Preview Modal */}
      {showPreview && planPreview && (
        <div className="modal-overlay">
          <div className="modal-content plan-preview-modal">
            <div className="modal-header">
              <h3>🤖 Build Plan Preview</h3>
              <button className="close-btn" onClick={() => setShowPreview(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="plan-summary">
                <div className="plan-stat">
                  <span>Estimated Duration:</span>
                  <strong>{planPreview.total_duration_hours}h</strong>
                </div>
                <div className="plan-stat">
                  <span>Complexity:</span>
                  <strong>{planPreview.complexity}</strong>
                </div>
                <div className="plan-stat">
                  <span>Phases:</span>
                  <strong>{planPreview.phases.length}</strong>
                </div>
              </div>

              <div className="plan-phases">
                <h4>Execution Phases</h4>
                <ol>
                  {planPreview.phases.map((phase: any, idx: number) => (
                    <li key={idx}>
                      <strong>{phase.name}</strong> ({phase.duration_hours}h)
                      <ul>
                        {phase.tasks.map((task: string, tidx: number) => (
                          <li key={tidx}>{task}</li>
                        ))}
                      </ul>
                    </li>
                  ))}
                </ol>
              </div>

              <div className="plan-deliverables">
                <h4>Expected Deliverables</h4>
                <ul>
                  {planPreview.deliverables.map((item: string, idx: number) => (
                    <li key={idx}>✓ {item}</li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowPreview(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleApprovePlan}>
                ✓ Approve & Start Build
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
