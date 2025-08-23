from flask import Flask, request, render_template
import joblib
import pandas as pd
import lime
import lime.lime_tabular
import re

# Import feature extractor
from src.features.build_features import extract_features

app = Flask(__name__)

model = None
explainer = None
reference_cols = None


def generate_natural_language_explanation(explanation_list, features):
    """Translates LIME's output into human-readable sentences."""

    templates = {
        'sensitive_words': {
            'risk': "It includes sensitive keywords (like 'login' or 'account'), a common tactic in phishing attacks.",
            'safe': "It does not contain high-risk keywords, which is a good sign."
        },
        'qty_hyphens': {
            'risk': f"It contains {int(features.get('qty_hyphens', 0))} hyphens, which is a pattern often used to mimic legitimate domains.",
            'safe': "The number of hyphens is not suspicious."
        },
        'url_length': {
            'risk': f"The URL is unusually long ({int(features.get('url_length', 0))} characters), which can be used to hide the true domain.",
            'safe': "The URL has a standard length."
        },
        'qty_slash': {
            'risk': f"It uses {int(features.get('qty_slash', 0))} slashes in its path, which can indicate a complex and potentially deceptive structure.",
            'safe': "The URL structure is simple and not suspicious."
        },
        'qty_dots': {
            'risk': f"The URL has {int(features.get('qty_dots', 0))} dots, which might be an attempt to create misleading subdomains.",
            'safe': "The number of dots in the URL is normal."
        },
        'is_ip': {
            'risk': "The domain is an IP address, which is highly suspicious and rarely used for legitimate websites.",
            'safe': "The domain is not an IP address."
        }
    }

    nl_explanations = []
    for feature, weight in explanation_list:
        factor_type = 'risk' if weight > 0 else 'safe'
        feature_name = re.split(r'[<>=]', feature)[0].strip()

        if feature_name in templates:
            text = templates[feature_name][factor_type]
            nl_explanations.append({'text': text, 'type': factor_type})

    return nl_explanations


def generate_non_technical_summary(is_malicious, confidence, explanations):
    """Creates a friendly explanation for non-technical users."""
    if is_malicious:
        summary = f"This website looks suspicious with {confidence}% certainty. "
        summary += "It shows patterns often used by phishing sites. "
        reasons = [e['text'] for e in explanations if e['type'] == 'risk']
        if reasons:
            summary += "For example, " + reasons[0].lower()
    else:
        summary = f"This website looks safe with {confidence}% certainty. "
        safe_reasons = [e['text'] for e in explanations if e['type'] == 'safe']
        if safe_reasons:
            summary += "One good sign is that " + safe_reasons[0].lower()
    return summary


def startup():
    """Load model and create explainer at app startup."""
    global model, explainer, reference_cols
    try:
        model = joblib.load('models/phishing_detector_model.joblib')
        training_data_sample = pd.read_csv('data/training_data_sample.csv')
        explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=training_data_sample.to_numpy(),
            feature_names=training_data_sample.columns.tolist(),
            class_names=['Benign', 'Malicious'],
            mode='classification'
        )
        reference_cols = pd.read_csv('data/processed_data.csv').drop('label', axis=1).columns
        print("Model and explainer loaded successfully.")
    except FileNotFoundError:
        print("ERROR: Model or data files not found. Please run the training script first.")


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    prediction_text = ''
    explanation_html = ''
    url_to_check = ''
    is_malicious = False
    confidence = 0
    natural_explanations = []
    non_technical_summary = ""

    if request.method == 'POST':
        try:
            url_to_check = request.form['url']
            if not url_to_check.strip():
                return render_template('index.html', prediction_text="Please enter a URL.", url=url_to_check)

            # 1. Extract features
            new_url_features = extract_features(url_to_check)
            new_url_df = pd.DataFrame([new_url_features])
            new_url_df = new_url_df.reindex(columns=reference_cols, fill_value=0)

            # 2. Make prediction
            prediction_proba = model.predict_proba(new_url_df)[0]
            is_malicious = prediction_proba[1] > 0.5

            # 3. Confidence and text
            if is_malicious:
                confidence = round(prediction_proba[1] * 100)
                prediction_text = "Warning: This URL is likely a Malicious Site!"
            else:
                confidence = round(prediction_proba[0] * 100)
                prediction_text = "This URL appears to be Benign."

            # 4. LIME Explanation
            predict_fn_wrapper = lambda x: model.predict_proba(pd.DataFrame(x, columns=reference_cols))
            explanation = explainer.explain_instance(
                data_row=new_url_df.iloc[0].to_numpy(),
                predict_fn=predict_fn_wrapper,
                num_features=5
            )
            explanation_html = explanation.as_html()

            # 5. Natural explanations
            natural_explanations = generate_natural_language_explanation(explanation.as_list(), new_url_features)

            # 6. Simple user-friendly explanation
            non_technical_summary = generate_non_technical_summary(is_malicious, confidence, natural_explanations)

        except Exception as e:
            prediction_text = f"An error occurred: {e}"

        return render_template(
            'index.html',
            prediction_text=prediction_text,
            url=url_to_check,
            explanation=explanation_html,
            is_malicious=is_malicious,
            confidence=confidence,
            natural_explanations=natural_explanations,
            non_technical_summary=non_technical_summary
        )

    return render_template('index.html')


if __name__ == '__main__':
    startup()
    app.run(debug=True)
else:
    startup()
