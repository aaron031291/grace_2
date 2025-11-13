"""
Model Registry API Tests
"""

import pytest
from fastapi.testclient import TestClient


def test_list_models():
    """Test listing models"""
    from backend.app_factory import create_app
    
    app = create_app()
    client = TestClient(app)
    
    response = client.get("/api/model-registry/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "count" in data


def test_get_registry_stats():
    """Test registry statistics"""
    from backend.app_factory import create_app
    
    app = create_app()
    client = TestClient(app)
    
    response = client.get("/api/model-registry/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_models" in data
    assert "by_stage" in data
    assert "governance" in data


def test_register_model():
    """Test model registration"""
    from backend.app_factory import create_app
    
    app = create_app()
    client = TestClient(app)
    
    model_data = {
        "model_id": "test_model_001",
        "name": "Test Classifier",
        "version": "1.0",
        "framework": "sklearn",
        "model_type": "classification",
        "owner": "test_user",
        "team": "ml",
        "training_data_hash": "abc123",
        "training_dataset_size": 1000,
        "evaluation_metrics": {"accuracy": 0.95, "f1": 0.93}
    }
    
    response = client.post("/api/model-registry/models", json=model_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "registered"
    assert data["model_id"] == "test_model_001"


def test_get_model():
    """Test getting specific model"""
    from backend.app_factory import create_app
    
    app = create_app()
    client = TestClient(app)
    
    # First register a model
    model_data = {
        "model_id": "test_get_model",
        "name": "Test Model",
        "version": "1.0",
        "framework": "pytorch",
        "model_type": "regression",
        "owner": "test",
        "team": "ml",
        "training_data_hash": "def456",
        "training_dataset_size": 500,
        "evaluation_metrics": {"mae": 0.12}
    }
    client.post("/api/model-registry/models", json=model_data)
    
    # Get it back
    response = client.get("/api/model-registry/models/test_get_model")
    assert response.status_code == 200
    data = response.json()
    assert data["model"]["model_id"] == "test_get_model"


def test_update_deployment():
    """Test deployment status update"""
    from backend.app_factory import create_app
    
    app = create_app()
    client = TestClient(app)
    
    # Register model with governance passing
    model_data = {
        "model_id": "test_deploy",
        "name": "Test Deploy",
        "version": "1.0",
        "framework": "sklearn",
        "model_type": "classification",
        "owner": "test",
        "team": "ml",
        "training_data_hash": "xyz789",
        "training_dataset_size": 2000,
        "evaluation_metrics": {"accuracy": 0.98}
    }
    client.post("/api/model-registry/models", json=model_data)
    
    # Try to promote (should fail governance)
    response = client.patch(
        "/api/model-registry/models/test_deploy/deployment",
        json={"status": "canary", "canary_percentage": 10.0}
    )
    
    # Should fail because constitutional_compliance not set
    assert response.status_code == 403


def test_generate_model_card():
    """Test model card generation"""
    from backend.app_factory import create_app
    
    app = create_app()
    client = TestClient(app)
    
    # Register a model
    model_data = {
        "model_id": "test_card",
        "name": "Test Card Model",
        "version": "1.0",
        "framework": "pytorch",
        "model_type": "classification",
        "owner": "test",
        "team": "ml",
        "training_data_hash": "card123",
        "training_dataset_size": 5000,
        "evaluation_metrics": {"accuracy": 0.96},
        "description": "Test model for card generation"
    }
    client.post("/api/model-registry/models", json=model_data)
    
    # Generate card
    response = client.post("/api/model-registry/models/test_card/generate-card")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "generated"
    assert "model_card_path" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
