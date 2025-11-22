-- Grace 3.0 - Cryptographic Provenance Database Schema
-- PostgreSQL Database for Fusion Layer (Durable Storage)

-- Drop existing tables if they exist
DROP TABLE IF EXISTS lifecycle_events CASCADE;
DROP TABLE IF EXISTS memory_dna CASCADE;
DROP TABLE IF EXISTS fusion_artifacts CASCADE;

-- Main artifacts table
CREATE TABLE fusion_artifacts (
    artifact_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    type VARCHAR(50) NOT NULL,
    layer VARCHAR(20) DEFAULT 'fusion' CHECK (layer IN ('lightning', 'fusion')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Memory DNA table (stores versioning information)
CREATE TABLE memory_dna (
    id SERIAL PRIMARY KEY,
    artifact_id VARCHAR(255) REFERENCES fusion_artifacts(artifact_id) ON DELETE CASCADE,
    version_id VARCHAR(255) UNIQUE NOT NULL,
    origin VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    intent VARCHAR(500) NOT NULL,
    checksum VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Lifecycle events table (audit log)
CREATE TABLE lifecycle_events (
    id SERIAL PRIMARY KEY,
    artifact_id VARCHAR(255) REFERENCES fusion_artifacts(artifact_id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    action VARCHAR(100) NOT NULL,
    actor VARCHAR(255) NOT NULL,
    description TEXT,
    previous_version_id VARCHAR(255),
    snapshot JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_fusion_artifacts_layer ON fusion_artifacts(layer);
CREATE INDEX idx_fusion_artifacts_created_at ON fusion_artifacts(created_at DESC);
CREATE INDEX idx_memory_dna_artifact_id ON memory_dna(artifact_id);
CREATE INDEX idx_memory_dna_version_id ON memory_dna(version_id);
CREATE INDEX idx_lifecycle_events_artifact_id ON lifecycle_events(artifact_id);
CREATE INDEX idx_lifecycle_events_timestamp ON lifecycle_events(timestamp DESC);
CREATE INDEX idx_lifecycle_events_action ON lifecycle_events(action);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
CREATE TRIGGER update_fusion_artifacts_updated_at 
    BEFORE UPDATE ON fusion_artifacts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Sample data for testing
INSERT INTO fusion_artifacts (artifact_id, name, type, layer) VALUES
    ('ART-sample-001', 'system_health_v1.json', 'file', 'fusion'),
    ('ART-sample-002', 'governance_rules.yaml', 'file', 'fusion');

INSERT INTO memory_dna (artifact_id, version_id, origin, timestamp, intent, checksum) VALUES
    ('ART-sample-001', 'VER-001', 'SystemMonitor', NOW(), 'HealthCheck', 'abc123'),
    ('ART-sample-002', 'VER-002', 'GovernanceAgent', NOW(), 'PolicyDefinition', 'def456');

INSERT INTO lifecycle_events (artifact_id, timestamp, action, actor, description) VALUES
    ('ART-sample-001', NOW(), 'Created', 'SystemMonitor', 'Initial health check artifact'),
    ('ART-sample-002', NOW(), 'Created', 'GovernanceAgent', 'Initial governance rules');
