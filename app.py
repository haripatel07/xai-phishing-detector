from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import joblib
import pandas as pd
import lime
import lime.lime_tabular
from src.features.build_features import extract_features


def _load_env_var(name: str, default=None):
    return os.getenv(name, default)


class PredictRequest(BaseModel):
    url: str | None = None
    text: str | None = None


class PredictResponse(BaseModel):
    label: str
    confidence: float


class ExplainResponse(BaseModel):
    label: str
    confidence: float
    top_features: list


app = FastAPI()
model = None
explainer = None
reference_cols = None

def _build_explainer(training_csv_path: str):
    df = pd.read_csv(training_csv_path)
    return lime.lime_tabular.LimeTabularExplainer(
        training_data=df.to_numpy(),
        feature_names=df.columns.tolist(),
        class_names=['Benign', 'Malicious'],
        mode='classification'
    )


@app.on_event('startup')
def startup_event():
    global model, explainer, reference_cols

    model_path = _load_env_var('MODEL_PATH', 'models/phishing_detector_model.joblib')
    explainer_path = _load_env_var('EXPLAINER_PATH', '')
    training_sample_path = 'data/training_data_sample.csv'
    processed_data_path = 'data/processed_data.csv'

    if not os.path.exists(model_path):
        raise RuntimeError(f'Model not found at {model_path}')

    model = joblib.load(model_path)

    if explainer_path and os.path.exists(explainer_path):
        explainer = joblib.load(explainer_path)
    else:
        if not os.path.exists(training_sample_path):
            raise RuntimeError('Training sample missing for explainer: data/training_data_sample.csv')
        explainer = _build_explainer(training_sample_path)

    if not os.path.exists(processed_data_path):
        raise RuntimeError(f'Processed data not found at {processed_data_path}')

    reference_cols = pd.read_csv(processed_data_path).drop(columns=['label']).columns.tolist()


@app.get('/health')
def health_check():
    return {'status': 'ok'}


def _prepare_features(payload: PredictRequest) -> pd.DataFrame:
    value = payload.url or payload.text
    if not value or not isinstance(value, str) or not value.strip():
        raise HTTPException(status_code=400, detail='Either "url" or "text" must be a non-empty string.')

    features = extract_features(value.strip())
    row = pd.DataFrame([features])

    if reference_cols is None:
        raise RuntimeError('Feature columns are not initialized.')

    row = row.reindex(columns=reference_cols, fill_value=0)
    return row


@app.post('/predict', response_model=PredictResponse)
def predict(payload: PredictRequest):
    row = _prepare_features(payload)

    try:
        proba = model.predict_proba(row)[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Prediction failed: {e}')

    label = 'malicious' if proba[1] > 0.5 else 'benign'
    confidence = float(round(float(max(proba)), 4))

    return {'label': label, 'confidence': confidence}


@app.post('/explain', response_model=ExplainResponse)
def explain(payload: PredictRequest):
    row = _prepare_features(payload)

    try:
        proba = model.predict_proba(row)[0]
        label = 'malicious' if proba[1] > 0.5 else 'benign'
        confidence = float(round(float(max(proba)), 4))

        def predict_fn(x):
            return model.predict_proba(pd.DataFrame(x, columns=reference_cols))

        explanation = explainer.explain_instance(
            data_row=row.iloc[0].to_numpy(),
            predict_fn=predict_fn,
            num_features=5
        )

        top_explanations = explanation.as_list()
        top_features = [
            {'feature': feat, 'weight': float(round(wt, 4)), 'impact': 'risk' if wt > 0 else 'safe'}
            for feat, wt in sorted(top_explanations, key=lambda x: abs(x[1]), reverse=True)
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Explainer failed: {e}')

    return {'label': label, 'confidence': confidence, 'top_features': top_features}

