/**
 * Template Selector Component
 * Pre-fill Agentic Builder with common project templates
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './TemplateSelector.css';

interface Template {
  id: string;
  name: string;
  description: string;
  estimated_hours: number;
  phases_count: number;
}

interface TemplateSelectorProps {
  onTemplateSelect: (template: any) => void;
}

const API_BASE = 'http://localhost:8000';

export const TemplateSelector: React.FC<TemplateSelectorProps> = ({ onTemplateSelect }) => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/coding_agent/templates`);
      setTemplates(response.data.templates || []);
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    }
    setLoading(false);
  };

  const handleSelectTemplate = async (templateId: string) => {
    setSelectedTemplate(templateId);
    
    try {
      const response = await axios.get(`${API_BASE}/api/coding_agent/templates/${templateId}`);
      onTemplateSelect(response.data);
    } catch (error) {
      console.error('Failed to load template:', error);
    }
  };

  if (loading) {
    return <div className="template-loading">Loading templates...</div>;
  }

  return (
    <div className="template-selector">
      <div className="template-header">
        <h4>🎯 Quick Start Templates</h4>
        <p>Select a template to pre-fill the form</p>
      </div>
      <div className="templates-grid">
        {templates.map((template) => (
          <div
            key={template.id}
            className={`template-card ${selectedTemplate === template.id ? 'selected' : ''}`}
            onClick={() => handleSelectTemplate(template.id)}
          >
            <div className="template-name">{template.name}</div>
            <div className="template-description">{template.description}</div>
            <div className="template-meta">
              <span className="template-time">⏱ ~{template.estimated_hours}h</span>
              <span className="template-phases">{template.phases_count} phases</span>
            </div>
          </div>
        ))}
        <div
          className={`template-card custom ${selectedTemplate === 'custom' ? 'selected' : ''}`}
          onClick={() => handleSelectTemplate('custom')}
        >
          <div className="template-name">Custom Build</div>
          <div className="template-description">Start from scratch with your own requirements</div>
          <div className="template-meta">
            <span className="template-custom">✨ Flexible</span>
          </div>
        </div>
      </div>
    </div>
  );
};
