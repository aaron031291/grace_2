import { useState, useEffect } from 'react';
import type { WorkspacePayload } from '../../hooks/useWorkspaces';
import './WorkspaceCommon.css';

interface ArtifactViewerWorkspaceProps {
  payload: WorkspacePayload;
}

export default function ArtifactViewerWorkspace({ payload }: ArtifactViewerWorkspaceProps) {
  const { artifactId } = payload;
  const [artifact, setArtifact] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading artifact
    const timer = setTimeout(() => {
      setArtifact({
        id: artifactId,
        title: `Artifact ${artifactId}`,
        type: 'document',
        content: 'Artifact content would be loaded here...',
      });
      setLoading(false);
    }, 500);

    return () => clearTimeout(timer);
  }, [artifactId]);

  if (loading) {
    return (
      <div className="workspace-container">
        <div className="workspace-loading">
          <div className="loading-spinner"></div>
          <p>Loading artifact...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="workspace-container artifact-viewer-workspace">
      <div className="workspace-header">
        <h2>📄 {artifact?.title || 'Artifact Viewer'}</h2>
      </div>

      <div className="workspace-content">
        <div className="artifact-preview">
          <div className="preview-placeholder">
            <div className="placeholder-icon">📄</div>
            <h3>Artifact Viewer</h3>
            <p>ID: <code>{artifactId}</code></p>
            <p>Wire this to your artifact preview component to display:</p>
            <ul>
              <li>PDFs (with PDF.js)</li>
              <li>Images</li>
              <li>Code files (with syntax highlighting)</li>
              <li>Text documents</li>
              <li>JSON/YAML viewers</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="workspace-actions">
        <button className="action-btn">Download</button>
        <button className="action-btn">Share</button>
        <button className="action-btn">Re-ingest</button>
      </div>
    </div>
  );
}
