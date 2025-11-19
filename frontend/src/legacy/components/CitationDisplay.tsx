/**
 * Citation Display Component - Visual citations in UI
 */
import React, { useState } from 'react';
import { ExternalLinkIcon, CheckCircleIcon, QuestionMarkCircleIcon } from '@heroicons/react/outline';

interface Citation {
  id: string;
  display_number: number;
  formatted_text: string;
  confidence_badge: {
    type: 'high' | 'medium' | 'low';
    color: string;
    text: string;
    percentage: string;
    tooltip: string;
  };
  verification_badge: {
    type: 'verified' | 'unverified';
    color: string;
    icon: string;
    text: string;
    tooltip: string;
  };
  interactive_elements: {
    preview_available: boolean;
    external_link?: string;
    feedback_enabled: boolean;
    share_enabled: boolean;
    preview_content?: {
      excerpt: string;
      full_content_available: boolean;
    };
  };
  metadata: {
    source_type: string;
    confidence: number;
    verified: boolean;
    url?: string;
    date?: string;
  };
}

interface CitationDisplayProps {
  citations: Citation[];
  citationSummary: {
    total: number;
    verified: number;
    average_confidence: number;
    source_types: Record<string, number>;
    summary_text: string;
    confidence_distribution: {
      high: number;
      medium: number;
      low: number;
    };
  };
  showSummary?: boolean;
  compact?: boolean;
}

export const CitationDisplay: React.FC<CitationDisplayProps> = ({
  citations,
  citationSummary,
  showSummary = true,
  compact = false
}) => {
  const [expandedCitation, setExpandedCitation] = useState<string | null>(null);
  const [feedbackGiven, setFeedbackGiven] = useState<Set<string>>(new Set());

  const handleCitationClick = (citationId: string) => {
    setExpandedCitation(expandedCitation === citationId ? null : citationId);
  };

  const handleFeedback = async (citationId: string, helpful: boolean) => {
    // Submit feedback to API
    try {
      await fetch('/api/provenance/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          response_id: citationId,
          feedback_score: helpful ? 1.0 : 0.0,
          feedback_type: helpful ? 'helpful' : 'not_helpful'
        })
      });
      
      setFeedbackGiven(prev => new Set([...prev, citationId]));
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const ConfidenceBadge: React.FC<{ badge: Citation['confidence_badge'] }> = ({ badge }) => (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium`}
      style={{ backgroundColor: badge.color + '20', color: badge.color }}
      title={badge.tooltip}
    >
      {badge.percentage}
    </span>
  );

  const VerificationBadge: React.FC<{ badge: Citation['verification_badge'] }> = ({ badge }) => (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium`}
      style={{ backgroundColor: badge.color + '20', color: badge.color }}
      title={badge.tooltip}
    >
      {badge.type === 'verified' ? (
        <CheckCircleIcon className="w-3 h-3 mr-1" />
      ) : (
        <QuestionMarkCircleIcon className="w-3 h-3 mr-1" />
      )}
      {badge.text}
    </span>
  );

  if (compact) {
    return (
      <div className="text-sm text-gray-600 border-l-4 border-blue-200 pl-3 py-2">
        <div className="font-medium mb-1">Sources ({citationSummary.total})</div>
        <div className="text-xs space-y-1">
          {citations.slice(0, 3).map((citation) => (
            <div key={citation.id} className="flex items-center space-x-2">
              <span className="w-4 h-4 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-medium">
                {citation.display_number}
              </span>
              <span className="truncate">{citation.formatted_text.replace(/<[^>]*>/g, '')}</span>
              <ConfidenceBadge badge={citation.confidence_badge} />
            </div>
          ))}
          {citations.length > 3 && (
            <div className="text-xs text-gray-500">
              +{citations.length - 3} more sources
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 rounded-lg p-4 mt-4">
      {showSummary && (
        <div className="mb-4 pb-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Sources & Citations</h3>
          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
            <span>{citationSummary.summary_text}</span>
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>{citationSummary.confidence_distribution.high} high</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span>{citationSummary.confidence_distribution.medium} medium</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span>{citationSummary.confidence_distribution.low} low</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {citations.map((citation) => (
          <div
            key={citation.id}
            className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                    {citation.display_number}
                  </span>
                  <div className="flex items-center space-x-2">
                    <ConfidenceBadge badge={citation.confidence_badge} />
                    <VerificationBadge badge={citation.verification_badge} />
                  </div>
                </div>
                
                <div 
                  className="text-gray-900 mb-2 cursor-pointer hover:text-blue-600"
                  onClick={() => handleCitationClick(citation.id)}
                  dangerouslySetInnerHTML={{ __html: citation.formatted_text }}
                />
                
                {expandedCitation === citation.id && citation.interactive_elements.preview_available && (
                  <div className="mt-3 p-3 bg-gray-50 rounded border-l-4 border-blue-200">
                    <p className="text-sm text-gray-700 italic">
                      "{citation.interactive_elements.preview_content?.excerpt}"
                    </p>
                    {citation.interactive_elements.preview_content?.full_content_available && (
                      <button className="text-blue-600 text-xs mt-2 hover:underline">
                        View full content
                      </button>
                    )}
                  </div>
                )}
              </div>
              
              <div className="flex items-center space-x-2 ml-4">
                {citation.interactive_elements.external_link && (
                  <a
                    href={citation.interactive_elements.external_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-blue-600"
                    title="Open source"
                  >
                    <ExternalLinkIcon className="w-4 h-4" />
                  </a>
                )}
                
                {citation.interactive_elements.feedback_enabled && !feedbackGiven.has(citation.id) && (
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => handleFeedback(citation.id, true)}
                      className="text-xs px-2 py-1 text-green-600 hover:bg-green-50 rounded"
                      title="Mark as helpful"
                    >
                      👍
                    </button>
                    <button
                      onClick={() => handleFeedback(citation.id, false)}
                      className="text-xs px-2 py-1 text-red-600 hover:bg-red-50 rounded"
                      title="Mark as not helpful"
                    >
                      👎
                    </button>
                  </div>
                )}
                
                {feedbackGiven.has(citation.id) && (
                  <span className="text-xs text-gray-500">Thanks!</span>
                )}
              </div>
            </div>
            
            <div className="flex items-center justify-between text-xs text-gray-500 mt-2">
              <span>Source: {citation.metadata.source_type}</span>
              {citation.metadata.date && (
                <span>{new Date(citation.metadata.date).toLocaleDateString()}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CitationDisplay;