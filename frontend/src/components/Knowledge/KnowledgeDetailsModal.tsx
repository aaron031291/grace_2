import React from 'react';
import './KnowledgeDetailsModal.css';

interface Source {
    id: string;
    title: string;
    url: string;
    citationDate: string;
    relevanceScore: number;
    trustScore: number;
}

interface KnowledgeDetailsModalProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    trustScore: number;
    sources: Source[];
}

const KnowledgeDetailsModal: React.FC<KnowledgeDetailsModalProps> = ({
    isOpen,
    onClose,
    title,
    trustScore,
    sources
}) => {
    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <div className="header-title-wrapper">
                        <h2>{title}</h2>
                        <div className={`trust-badge ${trustScore >= 90 ? 'high' : trustScore >= 70 ? 'medium' : 'low'}`}>
                            Trust Score: {trustScore}%
                        </div>
                    </div>
                    <button className="close-btn" onClick={onClose}>×</button>
                </div>

                <div className="modal-body">
                    <div className="sources-list">
                        <h3>Verified Sources</h3>
                        {sources.map(source => (
                            <div key={source.id} className="source-item">
                                <div className="source-header">
                                    <a href={source.url} target="_blank" rel="noopener noreferrer" className="source-title">
                                        {source.title}
                                        <span className="external-link-icon">↗</span>
                                    </a>
                                    <span className="citation-date">{source.citationDate}</span>
                                </div>
                                <div className="source-metrics">
                                    <div className="metric">
                                        <span className="label">Relevance</span>
                                        <div className="progress-bar small">
                                            <div
                                                className="progress-fill"
                                                style={{ width: `${source.relevanceScore}%` }}
                                            ></div>
                                        </div>
                                        <span className="value">{source.relevanceScore}%</span>
                                    </div>
                                    <div className="metric">
                                        <span className="label">Trust</span>
                                        <span className={`value ${source.trustScore >= 90 ? 'high' : 'medium'}`}>
                                            {source.trustScore}%
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default KnowledgeDetailsModal;
