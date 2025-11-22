import React, { useState, useEffect } from 'react';
import './IntelligencePanel.css';
import { librarian } from '../../services/LibrarianService';

interface ModelStatus {
    id: string;
    name: string;
    type: 'LLM' | 'Diffusion' | 'Audio' | 'Code';
    status: 'active' | 'training' | 'idle' | 'offline';
    accuracy: number;
    latency: number;
    version: string;
    artifactId?: string; // Track model DNA
}

const IntelligencePanel: React.FC = () => {
    const [models, setModels] = useState<ModelStatus[]>([
        { id: '1', name: 'Grace 3.0 (Core)', type: 'LLM', status: 'active', accuracy: 98.5, latency: 45, version: 'v3.0.1' },
        { id: '2', name: 'Builder Agent', type: 'Code', status: 'active', accuracy: 99.2, latency: 30, version: 'v2.1.0' },
        { id: '3', name: 'Researcher', type: 'LLM', status: 'idle', accuracy: 96.0, latency: 120, version: 'v1.5.4' },
        { id: '4', name: 'Vision Module', type: 'Diffusion', status: 'offline', accuracy: 94.5, latency: 0, version: 'v1.0.0' },
    ]);

    const [trainingMetrics, setTrainingMetrics] = useState({
        currentEpoch: 45,
        totalEpochs: 100,
        loss: 0.024,
        learningRate: 0.001,
        gpuUsage: 85,
        memoryUsage: 62,
        trainingArtifactId: null as string | null
    });

    // Initialize models with DNA on mount
    useEffect(() => {
        const initializeModels = () => {
            const updatedModels = models.map(model => {
                if (!model.artifactId) {
                    // Generate DNA for each model
                    const modelDNA = librarian.trackAction(
                        'ModelInitialization',
                        `Agent:${model.name}`,
                        JSON.stringify({
                            type: model.type,
                            version: model.version,
                            accuracy: model.accuracy,
                            latency: model.latency
                        })
                    );
                    return { ...model, artifactId: modelDNA.artifactId };
                }
                return model;
            });
            setModels(updatedModels);
        };

        initializeModels();
    }, []); // eslint-disable-line react-hooks/exhaustive-deps

    // Simulate training progress and track it
    useEffect(() => {
        const trainingInterval = setInterval(() => {
            setTrainingMetrics(prev => {
                if (prev.currentEpoch < prev.totalEpochs) {
                    const newEpoch = prev.currentEpoch + 1;
                    const newLoss = Math.max(0.001, prev.loss * 0.99); // Simulate decreasing loss

                    // Track training progress every 5 epochs
                    if (newEpoch % 5 === 0) {
                        const trainingDNA = librarian.trackAction(
                            'ModelTraining',
                            'Agent:MLEngine',
                            JSON.stringify({
                                model: 'Code Optimization v2',
                                epoch: newEpoch,
                                totalEpochs: prev.totalEpochs,
                                loss: newLoss,
                                learningRate: prev.learningRate,
                                gpuUsage: prev.gpuUsage,
                                memoryUsage: prev.memoryUsage
                            }),
                            prev.trainingArtifactId || undefined
                        );

                        console.log(`[Intelligence] 🧠 Training tracked: Epoch ${newEpoch}, Loss ${newLoss.toFixed(4)}`);

                        return {
                            ...prev,
                            currentEpoch: newEpoch,
                            loss: newLoss,
                            trainingArtifactId: trainingDNA.artifactId
                        };
                    }

                    return { ...prev, currentEpoch: newEpoch, loss: newLoss };
                }
                return prev;
            });
        }, 2000); // Update every 2 seconds

        return () => clearInterval(trainingInterval);
    }, []);

    const handleFineTune = (model: ModelStatus) => {
        if (model.status === 'offline') return;

        // Track fine-tuning action
        const fineTuneDNA = librarian.trackAction(
            'ModelFineTune',
            'User',
            JSON.stringify({
                modelId: model.id,
                modelName: model.name,
                currentVersion: model.version,
                targetVersion: `${model.version}-ft`
            }),
            model.artifactId
        );

        console.log(`[Intelligence] 🎯 Fine-tune initiated for ${model.name} (Root: ${fineTuneDNA.artifactId})`);
        alert(`Fine-tuning ${model.name}...\nArtifactID: ${fineTuneDNA.artifactId}`);
    };

    const handleViewLogs = (model: ModelStatus) => {
        // Track log access
        librarian.trackAction(
            'ModelLogAccess',
            'User',
            JSON.stringify({
                modelId: model.id,
                modelName: model.name
            }),
            model.artifactId
        );

        console.log(`[Intelligence] 📋 Logs accessed for ${model.name}`);
        alert(`Viewing logs for ${model.name}...\nCheck FileExplorer > Lightning for DNA`);
    };

    return (
        <div className="intelligence-panel">
            <div className="panel-header">
                <h3>Neural Intelligence Hub</h3>
                <div className="system-status">
                    <span className="status-dot active"></span>
                    <span>Neural Network Online</span>
                </div>
            </div>

            <div className="models-grid">
                {models.map(model => (
                    <div key={model.id} className={`model-card ${model.status}`}>
                        <div className="model-header">
                            <span className="model-name">{model.name}</span>
                            <span className={`status-badge ${model.status}`}>{model.status}</span>
                        </div>
                        <div className="model-details">
                            <div className="detail-item">
                                <span className="label">Type</span>
                                <span className="value">{model.type}</span>
                            </div>
                            <div className="detail-item">
                                <span className="label">Version</span>
                                <span className="value">{model.version}</span>
                            </div>
                            <div className="detail-item">
                                <span className="label">Accuracy</span>
                                <span className="value">{model.accuracy}%</span>
                            </div>
                            <div className="detail-item">
                                <span className="label">Latency</span>
                                <span className="value">{model.latency}ms</span>
                            </div>
                            {model.artifactId && (
                                <div className="detail-item full-width">
                                    <span className="label">DNA</span>
                                    <span className="value code" title={model.artifactId}>
                                        {model.artifactId.substring(0, 16)}...
                                    </span>
                                </div>
                            )}
                        </div>
                        <div className="model-actions">
                            <button
                                className="action-btn"
                                disabled={model.status === 'offline'}
                                onClick={() => handleFineTune(model)}
                            >
                                Fine-tune
                            </button>
                            <button
                                className="action-btn secondary"
                                onClick={() => handleViewLogs(model)}
                            >
                                Logs
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            <div className="training-dashboard">
                <h4>Active Training Session: Code Optimization v2</h4>
                {trainingMetrics.trainingArtifactId && (
                    <div className="training-dna-badge" title={`Root: ${trainingMetrics.trainingArtifactId}`}>
                        🧬 Tracked: {trainingMetrics.trainingArtifactId.substring(0, 12)}...
                    </div>
                )}
                <div className="training-metrics">
                    <div className="metric-box">
                        <span className="metric-label">Epoch</span>
                        <span className="metric-value">{trainingMetrics.currentEpoch}/{trainingMetrics.totalEpochs}</span>
                        <div className="progress-bar">
                            <div className="fill" style={{ width: `${(trainingMetrics.currentEpoch / trainingMetrics.totalEpochs) * 100}%` }}></div>
                        </div>
                    </div>
                    <div className="metric-box">
                        <span className="metric-label">Loss</span>
                        <span className="metric-value">{trainingMetrics.loss.toFixed(4)}</span>
                    </div>
                    <div className="metric-box">
                        <span className="metric-label">GPU Load</span>
                        <span className="metric-value">{trainingMetrics.gpuUsage}%</span>
                    </div>
                    <div className="metric-box">
                        <span className="metric-label">VRAM</span>
                        <span className="metric-value">{trainingMetrics.memoryUsage}%</span>
                    </div>
                </div>
                <div className="visualizer-placeholder">
                    {/* Placeholder for a real-time loss graph or neural visualizer */}
                    <div className="wave-animation">
                        <span></span><span></span><span></span><span></span><span></span>
                    </div>
                    <p>Real-time Neural Activity</p>
                </div>
            </div>
        </div>
    );
};

export default IntelligencePanel;
