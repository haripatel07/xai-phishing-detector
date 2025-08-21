from flask import Flask, request, render_template
import joblib
import pandas as pd
import numpy as np
import lime
import lime.lime_tabular

# We need the function that extracts features from a URL
from src.features.build_features import extract_features

app = Flask(__name__)

model = None
explainer = None
reference_cols = None

def startup():
    """Load model and create explainer at app startup."""
    global model, explainer, reference_cols
    try:
        model = joblib.load('models/phishing_detector_model.joblib')
        
        # Load the training data sample and create the LIME explainer
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
    if request.method == 'POST':
        try:
            url_to_check = request.form['url']

            if not url_to_check.strip():
                 prediction_text = "Please enter a URL."
                 return render_template('index.html', prediction_text=prediction_text, url=url_to_check)

            if model is None or explainer is None:
                prediction_text = "Model/Explainer not loaded. Please check server logs."
                return render_template('index.html', prediction_text=prediction_text, url=url_to_check)

            # 1. Extract features and create DataFrame
            new_url_features = extract_features(url_to_check)
            new_url_df = pd.DataFrame([new_url_features])
            new_url_df = new_url_df.reindex(columns=reference_cols, fill_value=0)

            # 2. Make a prediction
            prediction = model.predict(new_url_df)
            
            # 3. Generate LIME explanation
            predict_fn_wrapper = lambda x: model.predict_proba(pd.DataFrame(x, columns=reference_cols))

            explanation = explainer.explain_instance(
                data_row=new_url_df.iloc[0].to_numpy(), 
                predict_fn=predict_fn_wrapper,
                num_features=5
            )
            explanation_html = explanation.as_html()

            # 4. Interpret the prediction
            if prediction[0] == 1:
                prediction_text = "Warning: This URL is likely a Malicious Site!"
            else:
                prediction_text = "This URL appears to be Benign."

        except Exception as e:
            prediction_text = f"An error occurred: {e}"

        return render_template('index.html', 
                               prediction_text=prediction_text, 
                               url=url_to_check,
                               explanation=explanation_html)
    
    return render_template('index.html')

if __name__ == '__main__':
    startup()
    app.run(debug=True)
else:
    # This block is for production servers like Gunicorn
    startup()