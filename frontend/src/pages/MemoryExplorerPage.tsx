import { useState } from 'react';
import { Surface, Card, CardHeader, CardContent, Button, Tag } from '../design-system';
import { FileExplorer } from '../components/FileExplorer';
import { Upload, Search, TrendingUp } from 'lucide-react';
import './MemoryExplorerPage.css';

export function MemoryExplorerPage() {
  const [showUpload, setShowUpload] = useState(false);

  return (
    <Surface>
      <div className="memory-explorer-page">
        <div className="memory-explorer-page__header">
          <div>
            <h1 className="memory-explorer-page__title">Memory File Explorer</h1>
            <p className="memory-explorer-page__subtitle">
              Browse, upload, and manage Grace's knowledge base
            </p>
          </div>
          <div className="memory-explorer-page__actions">
            <Button 
              variant="secondary"
              icon={<Search size={18} />}
            >
              Search Memory
            </Button>
            <Button 
              icon={<Upload size={18} />}
              onClick={() => setShowUpload(!showUpload)}
            >
              Upload Files
            </Button>
          </div>
        </div>

        <div className="memory-explorer-page__stats">
          <div className="memory-explorer-page__stat">
            <div className="memory-explorer-page__stat-value">1,247</div>
            <div className="memory-explorer-page__stat-label">Total Files</div>
          </div>
          <div className="memory-explorer-page__stat">
            <div className="memory-explorer-page__stat-value">142</div>
            <div className="memory-explorer-page__stat-label">Added This Week</div>
          </div>
          <div className="memory-explorer-page__stat">
            <div className="memory-explorer-page__stat-value">89%</div>
            <div className="memory-explorer-page__stat-label">Ingestion Complete</div>
          </div>
        </div>

        {showUpload && (
          <Card variant="bordered" className="memory-explorer-page__upload">
            <CardHeader>
              Upload Files for Ingestion
            </CardHeader>
            <CardContent>
              <div className="memory-explorer-page__upload-zone">
                <Upload size={48} />
                <p>Drop files here or click to browse</p>
                <p className="memory-explorer-page__upload-hint">
                  Supports PDF, TXT, MD, DOCX, and more
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        <Card variant="bordered">
          <CardHeader>
            File Browser
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <Tag variant="success">Active</Tag>
              <Tag variant="info">Synced</Tag>
            </div>
          </CardHeader>
          <CardContent className="memory-explorer-page__browser">
            <FileExplorer isOpen={true} onClose={() => {}} />
          </CardContent>
        </Card>

        <Card variant="bordered">
          <CardHeader>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <TrendingUp size={20} />
              What Did Grace Learn?
            </div>
          </CardHeader>
          <CardContent>
            <div className="memory-explorer-page__insights">
              <div className="memory-explorer-page__insight">
                <div className="memory-explorer-page__insight-title">
                  Recent Ingestions
                </div>
                <div className="memory-explorer-page__insight-value">
                  42 documents processed in the last 24 hours
                </div>
              </div>
              <div className="memory-explorer-page__insight">
                <div className="memory-explorer-page__insight-title">
                  Top Categories
                </div>
                <div className="memory-explorer-page__insight-value">
                  Technical Documentation (45%), Code Reviews (22%), Meeting Notes (18%)
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </Surface>
  );
}
