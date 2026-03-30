import os
from fastapi.testclient import TestClient
from src.features.build_features import extract_features
import app as api_app


class DummyModel:
    def predict_proba(self, X):
        # Always returns malicious probability high for deterministic tests
        return [[0.1, 0.9]]


class DummyExplanation:
    def __init__(self, exp):
        self._exp = exp

    def as_list(self):
        return self._exp


class DummyExplainer:
    def explain_instance(self, data_row, predict_fn, num_features=5):
        # deterministically return a simple explanation set
        return DummyExplanation([('url_length', 0.2), ('qty_dots', -0.1)])


def setup_module(module):
    os.environ['SKIP_MODEL_LOAD'] = '1'
    api_app.model = DummyModel()
    api_app.explainer = DummyExplainer()
    # Setup columns for extract_features output to match reindex referenced columns
    api_app.reference_cols = list(extract_features('http://example.com').keys())


def test_health_endpoint():
    client = TestClient(api_app.app)
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_predict_endpoint():
    client = TestClient(api_app.app)
    response = client.post('/predict', json={'url': 'http://example.com'})
    assert response.status_code == 200
    body = response.json()
    assert body['label'] in ['benign', 'malicious']
    assert isinstance(body['confidence'], float)


def test_explain_endpoint():
    client = TestClient(api_app.app)
    response = client.post('/explain', json={'url': 'http://example.com'})
    assert response.status_code == 200
    body = response.json()
    assert body['label'] in ['benign', 'malicious']
    assert 'top_features' in body
    assert isinstance(body['top_features'], list)
