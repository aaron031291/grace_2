import React, { useState } from 'react';

interface TranscriptViewProps {
  speechId: number;
  transcript: string;
  confidence: number;
  status: string;
  needsReview?: boolean;
  reviewStatus?: string;
  onTranscriptEdit?: (newTranscript: string) => void;
  onReviewSubmit?: (approved: boolean, notes?: string) => void;
}

export const TranscriptView: React.FC<TranscriptViewProps> = ({
  speechId,
  transcript,
  confidence,
  status,
  needsReview,
  reviewStatus,
  onTranscriptEdit,
  onReviewSubmit
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTranscript, setEditedTranscript] = useState(transcript);
  const [reviewNotes, setReviewNotes] = useState('');
  const [showReviewPanel, setShowReviewPanel] = useState(false);

  const handleSaveEdit = () => {
    if (onTranscriptEdit) {
      onTranscriptEdit(editedTranscript);
    }
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditedTranscript(transcript);
    setIsEditing(false);
  };

  const handleApprove = () => {
    if (onReviewSubmit) {
      onReviewSubmit(true, reviewNotes);
    }
    setShowReviewPanel(false);
    setReviewNotes('');
  };

  const handleReject = () => {
    if (onReviewSubmit) {
      onReviewSubmit(false, reviewNotes);
    }
    setShowReviewPanel(false);
    setReviewNotes('');
  };

  const getConfidenceColor = (conf: number) => {
    if (conf >= 0.9) return '#10b981';
    if (conf >= 0.7) return '#f59e0b';
    return '#ef4444';
  };

  const getConfidenceLabel = (conf: number) => {
    if (conf >= 0.9) return 'High';
    if (conf >= 0.7) return 'Medium';
    return 'Low';
  };

  return (
    <div className="transcript-view">
      <div className="transcript-header">
        <h3>Transcript</h3>
        <div className="header-actions">
          <div 
            className="confidence-indicator"
            style={{ color: getConfidenceColor(confidence) }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
            </svg>
            {getConfidenceLabel(confidence)} ({(confidence * 100).toFixed(0)}%)
          </div>
          
          {!isEditing && (
            <button onClick={() => setIsEditing(true)} className="edit-button">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
              </svg>
              Edit
            </button>
          )}
        </div>
      </div>

      {needsReview && reviewStatus !== 'approved' && (
        <div className="review-alert">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
          </svg>
          <span>This transcript needs review</span>
          {reviewStatus === 'quarantined' && (
            <span className="quarantine-badge">Quarantined</span>
          )}
        </div>
      )}

      <div className="transcript-content">
        {isEditing ? (
          <div className="edit-mode">
            <textarea
              value={editedTranscript}
              onChange={(e) => setEditedTranscript(e.target.value)}
              className="transcript-editor"
              rows={6}
              autoFocus
            />
            <div className="edit-actions">
              <button onClick={handleSaveEdit} className="save-button">
                Save
              </button>
              <button onClick={handleCancelEdit} className="cancel-button">
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="transcript-text">
            {transcript || <span className="empty-state">No transcript available</span>}
          </div>
        )}
      </div>

      {status === 'transcribing' && (
        <div className="processing-indicator">
          <div className="spinner"></div>
          <span>Transcribing audio...</span>
        </div>
      )}

      {needsReview && !showReviewPanel && (
        <button 
          onClick={() => setShowReviewPanel(true)}
          className="review-button"
        >
          Review Transcript
        </button>
      )}

      {showReviewPanel && (
        <div className="review-panel">
          <h4>Review Transcript</h4>
          <textarea
            placeholder="Add review notes (optional)"
            value={reviewNotes}
            onChange={(e) => setReviewNotes(e.target.value)}
            className="review-notes"
            rows={3}
          />
          <div className="review-actions">
            <button onClick={handleApprove} className="approve-button">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
              </svg>
              Approve
            </button>
            <button onClick={handleReject} className="reject-button">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
              </svg>
              Reject
            </button>
            <button onClick={() => setShowReviewPanel(false)} className="cancel-button">
              Cancel
            </button>
          </div>
        </div>
      )}

      <style>{`
        .transcript-view {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          padding: 20px;
        }

        .transcript-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .transcript-header h3 {
          margin: 0;
          font-size: 18px;
          color: #111827;
        }

        .header-actions {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .confidence-indicator {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 14px;
          font-weight: 600;
        }

        .edit-button {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          border: 1px solid #d1d5db;
          background: white;
          color: #374151;
          border-radius: 6px;
          font-size: 14px;
          cursor: pointer;
        }

        .edit-button:hover {
          background: #f9fafb;
        }

        .review-alert {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px;
          background: #fef3c7;
          border: 1px solid #fde68a;
          border-radius: 8px;
          color: #92400e;
          margin-bottom: 16px;
          font-size: 14px;
        }

        .quarantine-badge {
          margin-left: auto;
          padding: 4px 12px;
          background: #fee2e2;
          color: #991b1b;
          border-radius: 12px;
          font-weight: 600;
          font-size: 12px;
        }

        .transcript-content {
          min-height: 100px;
        }

        .transcript-text {
          padding: 16px;
          background: #f9fafb;
          border-radius: 8px;
          font-size: 15px;
          line-height: 1.6;
          color: #374151;
        }

        .empty-state {
          color: #9ca3af;
          font-style: italic;
        }

        .edit-mode {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .transcript-editor {
          width: 100%;
          padding: 12px;
          border: 2px solid #4f46e5;
          border-radius: 8px;
          font-size: 15px;
          line-height: 1.6;
          font-family: inherit;
          resize: vertical;
        }

        .transcript-editor:focus {
          outline: none;
          border-color: #4338ca;
        }

        .edit-actions {
          display: flex;
          gap: 8px;
          justify-content: flex-end;
        }

        .save-button {
          padding: 8px 16px;
          background: #4f46e5;
          color: white;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          cursor: pointer;
        }

        .save-button:hover {
          background: #4338ca;
        }

        .cancel-button {
          padding: 8px 16px;
          background: white;
          color: #374151;
          border: 1px solid #d1d5db;
          border-radius: 6px;
          font-weight: 600;
          cursor: pointer;
        }

        .cancel-button:hover {
          background: #f9fafb;
        }

        .processing-indicator {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          background: #eff6ff;
          border: 1px solid #dbeafe;
          border-radius: 8px;
          color: #1e40af;
          margin-top: 16px;
          font-size: 14px;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid #93c5fd;
          border-top-color: #1e40af;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .review-button {
          width: 100%;
          padding: 12px;
          margin-top: 16px;
          background: #4f46e5;
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
        }

        .review-button:hover {
          background: #4338ca;
        }

        .review-panel {
          margin-top: 16px;
          padding: 16px;
          background: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
        }

        .review-panel h4 {
          margin: 0 0 12px 0;
          font-size: 16px;
          color: #111827;
        }

        .review-notes {
          width: 100%;
          padding: 10px;
          border: 1px solid #d1d5db;
          border-radius: 6px;
          font-size: 14px;
          font-family: inherit;
          resize: vertical;
          margin-bottom: 12px;
        }

        .review-notes:focus {
          outline: none;
          border-color: #4f46e5;
        }

        .review-actions {
          display: flex;
          gap: 8px;
        }

        .approve-button {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 16px;
          background: #10b981;
          color: white;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          cursor: pointer;
        }

        .approve-button:hover {
          background: #059669;
        }

        .reject-button {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 16px;
          background: #ef4444;
          color: white;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          cursor: pointer;
        }

        .reject-button:hover {
          background: #dc2626;
        }
      `}</style>
    </div>
  );
};
